"""Offline, opt-in exact-span dependency swaps over an already frozen pool.

No retrieval, model calls, answer references or case-ID rules. Structural cues are
proposals, not semantic support certificates. Baseline defaults are unaffected.
"""
import re
from newdomain.evidence_pool import grams, weighted_overlap

VERSION = 'dependency-swaps-v1'
STEP = re.compile(r'(?:^|\n)[ \t]*[（(]([一二三四五六七八九十\d]+)[）)]')
SECTION = re.compile(r'(?:^|\n)[ \t]*第[一二三四五六七八九十百\d]+条[^\n]*')
FOOTER = re.compile(r'\n[ \t]*[—―－-]+[ \t]*\d+[ \t]*[—―－-]+[ \t]*$')
QUALIFIER = re.compile(r'但|其中|不得|不超过|最高|最低|仅限|除外|符合|条件|上限|期限|限于')
PROCEDURE = re.compile(r'程序|流程|步骤')
QUERY_PROCEDURE = re.compile(r'流程|步骤|程序|办理|申请|签|先后|之前|之后')


def number(value):
    if value.isdigit():
        return int(value)
    digits = dict(zip('一二三四五六七八九', range(1, 10)))
    if value == '十':
        return 10
    if '十' in value:
        left, right = value.split('十', 1)
        return (digits.get(left, 1) * 10 + digits.get(right, 0))
    return digits.get(value)


def span(rid, source, start, end):
    return {'source_id': rid, 'start': start, 'end': end, 'text': source[start:end]}


def proposals(question, baseline, records):
    """Detect explicit structures only; never infer plain-OCR column relations."""
    found, skipped = [], []
    for rid, current in baseline.items():
        raw = records[rid]
        start = raw.find(current)
        if start < 0:
            skipped.append({'source_id': rid, 'reason': 'baseline is not one exact contiguous record span'})
            continue
        end = start + len(current)
        page = re.fullmatch(r'(D\d+):(\d+):01', rid)
        marks = list(STEP.finditer(current))
        if page and marks and marks[0].start() < 80 and QUERY_PROCEDURE.search(question):
            n = number(marks[0][1]); previous = page[1] + ':' + str(int(page[2]) - 1) + ':01'
            if n and n > 1:
                if previous not in records:
                    skipped.append({'source_id': rid, 'reason': 'preceding numbered-page candidate absent', 'dependency_id': previous})
                else:
                    prior = records[previous]; prior_marks = list(STEP.finditer(prior)); sections = list(SECTION.finditer(prior))
                    if prior_marks and sections and number(prior_marks[-1][1]) == n - 1 and PROCEDURE.search(sections[-1][0]):
                        stop = FOOTER.search(prior); stop = stop.start() if stop else len(prior)
                        dependency = span(previous, prior, sections[-1].start(), stop)
                        if previous in baseline:
                            pos = prior.find(baseline[previous])
                            if pos < 0:
                                skipped.append({'source_id': rid, 'reason': 'existing predecessor not contiguous'})
                                continue
                            dependency = span(previous, prior, min(pos, dependency['start']), max(pos + len(baseline[previous]), stop))
                        found.append({'kind': 'procedure', 'anchor': rid, 'dependency': dependency,
                                      'reason': 'adjacent same-document pages, consecutive enumeration, explicit procedure heading',
                                      'semantic_support_verified': False})
        if page and marks and QUERY_PROCEDURE.search(question):
            headings = list(SECTION.finditer(current))
            if headings and PROCEDURE.search(headings[-1][0]):
                n = number(marks[-1][1]); following_id = page[1] + ':' + str(int(page[2]) + 1) + ':01'
                if following_id in records:
                    following = records[following_id]; next_steps = list(STEP.finditer(following))
                    if next_steps and next_steps[0].start() < 80 and number(next_steps[0][1]) == n + 1:
                        next_headings = list(SECTION.finditer(following)); footer = FOOTER.search(following)
                        stop = next_headings[0].start() if next_headings else footer.start() if footer else len(following)
                        found.append({'kind': 'procedure', 'anchor': rid, 'dependency': span(following_id, following, 0, stop),
                                      'reason': 'explicit procedure heading and consecutive continuation on next same-document page',
                                      'semantic_support_verified': False})
        # Source-title/Markdown-table metadata: only explicit syntax, not adjacency guesses.
        header_start = None; metadata = []
        first = raw.split('\n', 1)[0]
        if start > 0 and re.fullmatch(r'【[^\n]+】', first):
            header_start = 0; metadata.append('explicit bracketed source title')
        lines = list(re.finditer(r'[^\n]*(?:\n|$)', raw))
        for i in range(len(lines) - 1):
            line, following = lines[i], lines[i + 1]
            if line.start() >= start:
                break
            if '|' in line[0] and re.fullmatch(r'[ \t|:\-\n]+', following[0]) and '-' in following[0]:
                between = raw[following.end():start]
                if '\n\n' not in between and '|' in current:
                    header_start = line.start() if header_start is None else min(header_start, line.start())
                    if i and re.search(r'单位\s*[:：]', lines[i - 1][0]):
                        header_start = min(header_start, lines[i - 1].start())
                    metadata.append('explicit Markdown table header/separator and directly preceding unit label')
        if header_start is not None and header_start < start:
            found.append({'kind': 'metadata', 'anchor': rid, 'dependency': span(rid, raw, header_start, end),
                          'reason': '; '.join(metadata), 'semantic_support_verified': False})
        # Only widen a clipped sentence when the newly recovered exact text has a qualifier cue.
        left = start if start == 0 or raw[start - 1] in '。！？；\n' else max([raw.rfind(c, 0, start) for c in '。！？；\n']) + 1
        right = end
        if end < len(raw) and current and current[-1] not in '。！？；\n':
            match = re.search(r'[。！？；\n]', raw[end:])
            right = end + match.end() if match else len(raw)
        recovered = raw[left:start] + raw[end:right]
        if (left < start or right > end) and QUALIFIER.search(recovered):
            found.append({'kind': 'qualifier', 'anchor': rid, 'dependency': span(rid, raw, left, right),
                          'reason': 'clipped sentence envelope contains explicit qualifier cue', 'semantic_support_verified': False})
    return found, skipped


def select(question, baseline, records, views, weights, max_sources, max_bytes,
           enabled=('procedure', 'metadata', 'qualifier'), relaxed_bytes=False):
    if max_sources < len(baseline) or max_bytes < sum(len(t.encode()) for t in baseline.values()):
        raise ValueError('baseline exceeds frozen ceiling')
    if not set(baseline) <= set(records):
        raise ValueError('baseline source absent from frozen pool')
    current = dict(baseline); candidates, skipped = proposals(question, baseline, records)
    qgrams = grams(question); original_coverage = set().union(*(grams(t) & qgrams for t in baseline.values()))
    scores = {}
    for i, view in enumerate(views):
        for rank, rid in enumerate(view):
            scores[rid] = scores.get(rid, 0) + (2 if i < 2 else 1) / (61 + rank)
    protected = set(list(baseline)[:1]); events = []
    for proposal in candidates:
        if proposal['kind'] not in enabled:
            continue
        if proposal['anchor'] not in current:
            events.append({**proposal, 'status': 'anchor_displaced_by_prior_swap', 'removed': []}); continue
        dep = proposal['dependency']; rid = dep['source_id']; raw = records[rid]
        assert raw[dep['start']:dep['end']] == dep['text']
        proposed = dict(current)
        if rid in current:
            if dep['text'] in current[rid]:
                events.append({**proposal, 'status': 'already_preserved', 'removed': []}); continue
            old_start = raw.find(current[rid])
            if old_start < 0:
                events.append({**proposal, 'status': 'unmergeable_exact_spans', 'removed': []}); continue
            dep = span(rid, raw, min(old_start, dep['start']), max(old_start + len(current[rid]), dep['end']))
        proposed[rid] = dep['text']
        keep = protected | {proposal['anchor'], rid}; removed = []
        byte_limit = None if relaxed_bytes else max_bytes
        while len(proposed) > max_sources or (byte_limit is not None and sum(len(t.encode()) for t in proposed.values()) > byte_limit):
            options = []
            for candidate in proposed:
                if candidate in keep:
                    continue
                remaining = [text for key, text in proposed.items() if key != candidate]
                coverage = set().union(*(grams(text) & qgrams for text in remaining)) if remaining else set()
                if not original_coverage <= coverage:
                    continue
                options.append(candidate)
            if not options:
                break
            victim = min(options, key=lambda key: (weighted_overlap(weights, grams(proposed[key]) & qgrams), scores.get(key, 0), key))
            removed.append({'source_id': victim, 'text': proposed[victim],
                            'query_overlap_weight': weighted_overlap(weights, grams(proposed[victim]) & qgrams),
                            'semantic_usefulness': 'not inferred from lexical overlap'})
            del proposed[victim]
        fits = len(proposed) <= max_sources and (byte_limit is None or sum(len(t.encode()) for t in proposed.values()) <= byte_limit)
        if fits:
            current = proposed; protected |= {proposal['anchor'], rid}
        events.append({**proposal, 'dependency': dep, 'status': 'accepted' if fits else 'blocked_by_ceiling_or_literal_coverage',
                       'removed': removed if fits else [], 'attempted_removals': removed,
                       'result_bytes': sum(len(t.encode()) for t in proposed.values())})
    assert set(current) <= set(records)
    assert len(current) <= max_sources
    if not relaxed_bytes:
        assert sum(len(t.encode()) for t in current.values()) <= max_bytes
    return current, {'version': VERSION, 'events': events, 'skipped': skipped,
                     'relaxed_bytes': relaxed_bytes, 'query_literal_coverage_guard': True,
                     'semantic_preservation_verified': False}
