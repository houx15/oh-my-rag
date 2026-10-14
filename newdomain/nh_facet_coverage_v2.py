"""Corpus-derived explicit entity coverage and exact source windows.
No question IDs, answer keys, scores, external knowledge or new embeddings.
Metadata links select evidence; they never prove an author's specific claim.
"""
import re


def _longest(names, question):
    spans=[(m.start(),m.end(),n)for n in names if n for m in re.finditer(re.escape(n),question)]
    # Suppress a short name only at occurrences inside a longer name. A separate
    # explicit occurrence remains a distinct requested entity in comparisons.
    kept=[(a,b,n)for a,b,n in spans if not any(c<=a and b<=d and d-c>b-a for c,d,_ in spans)]
    return list(dict.fromkeys(n for a,b,n in sorted(kept)))


def _main_entry(record):
    title=record.get('metadata',{}).get('标题') or ''
    return title.startswith('牛黄') and '【气味】' in record['text']


def _window(record, question, limit=900):
    text=record['text']
    if len(text)<=limit:return text,{'start':0,'end':len(text),'full':True}
    header,sep,body=text.partition('\n')
    # Keep one contiguous body window. Preserve original words and exact offsets.
    relevant=('性味','气味','寒凉','凉性','寒性','温性','偏性','主治','功效','评价','记载','关系')
    if not _main_entry(record) or not any(t in question for t in relevant):
        return text[:limit],{'start':0,'end':limit,'full':False}
    marker='【气味】' if any(t in question for t in ('性味','气味','寒凉','凉性','寒性','温性','偏性','评价','记载','关系')) else '【主治】'
    start=text.find(marker)
    if start<0:start=text.find('【主治】')
    if start<0:return text[:limit],{'start':0,'end':limit,'full':False}
    end=min(len(text),start+limit-len(header)-1)
    return header+'\n'+text[start:end],{'header_start':0,'header_end':len(header),'start':start,'end':end,'full':False,'contiguous_body':True}


class FacetIndex:
    def __init__(self, records):
        self.records={r['id']:r for r in records}
        self.books={};self.people={};self.formulas={}
        for r in records:
            m=r.get('metadata',{})
            if m.get('type')=='书目':self.books[m.get('书名',m.get('标题','')).strip('《》')]=r['id']
            if m.get('type')=='人物':self.people[m.get('姓名',m.get('标题',''))]=r['id']
            name=m.get('方名')
            if name:self.formulas.setdefault(name,[]).append(r['id'])

    def select(self, question, baseline, max_contexts=4):
        if max_contexts<1:raise ValueError('context bound')
        books=_longest(self.books,question);people=_longest(self.people,question);formulas=_longest(self.formulas,question)
        explicit_books=set(books)
        drug_focus='牛黄' in question and not formulas
        entry_focus=drug_focus and any(x in question for x in ('评价','记载','气味','性味','主治','功效','寒凉','凉性','寒性','温性','偏性','作用'))
        linked=[]
        if (entry_focus or (formulas and people)) and not books:
            for name in people:
                for book,rid in self.books.items():
                    m=self.records[rid].get('metadata',{})
                    if m.get('著者')==name:linked.append(book)
        target_books=books+linked
        groups=[]
        for book in target_books:
            candidates=[r for r in self.records.values() if r.get('metadata',{}).get('出处典籍')=='《'+book+'》' and _main_entry(r)] if entry_focus or (formulas and people) else []
            if candidates:
                candidates.sort(key=lambda r:(-sum(t in r['text'] for t in ('【释名】','【气味】','【主治】','【发明】')),r['id']))
                groups.append(('book_entry:'+book,[r['id']for r in candidates]))
            else:groups.append(('book:'+book,[self.books[book]]))
        for name in people:groups.append(('person:'+name,[self.people[name]]))
        for name in formulas:
            ids=list(self.formulas[name])
            if explicit_books:ids=[rid for rid in ids if self.records[rid]['metadata'].get('出处典籍','').strip('《》') in explicit_books]
            # Prefer sources linked to a named author, then original ranking. A link
            # provides coverage, not proof of authorship or causal influence.
            ids.sort(key=lambda rid:(self.records[rid]['metadata'].get('著者')not in people, list(baseline).index(rid)if rid in baseline else len(baseline),rid))
            if ids:groups.append(('formula:'+name,ids))
        if entry_focus and not target_books and any(t in question for t in ('寒凉','凉性','寒性','温性','偏性','性味','气味')):
            ids=[rid for rid,r in self.records.items()if _main_entry(r)]
            ids.sort(key=lambda rid:(-sum(t in self.records[rid]['text']for t in ('凉','平','寒')),rid))
            if ids:groups.append(('drug_properties',ids))
        chosen=[];coverage=[]
        for label,ids in groups:
            if len(chosen)>=max_contexts:break
            rid=ids[0]
            if rid not in chosen:chosen.append(rid)
            coverage.append({'facet':label,'source':rid})
        for rid in baseline:
            if len(chosen)>=max_contexts:break
            if rid not in chosen:chosen.append(rid)
        out={};windows={}
        for rid in chosen:
            if rid in self.records and any(x['source']==rid and x['facet'].startswith(('book_entry:','drug_properties'))for x in coverage):
                out[rid],windows[rid]=_window(self.records[rid],question)
            else:out[rid]=baseline[rid]if rid in baseline else self.records[rid]['text'][:900]
        return out,{'facets':coverage,'windows':windows,'added':[rid for rid in out if rid not in baseline],'removed':[rid for rid in baseline if rid not in out],'bounded_contexts':max_contexts}
