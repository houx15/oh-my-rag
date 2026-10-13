"""C3B: independently written complete-clause handle ablation.

Conceptual references: S2G-RAG sentence pointers (ACL 2026) and CompSelect's
compact clue selection (WWW 2026). No upstream source, prompt or trained model
is used. This variant changes segmentation only; it does not reproduce either
paper, perform learned selection or establish a quality gain.
"""
import re
from newdomain import candidate as c1

create_index = c1.create_index
validate = c1.validate


def atomic_passages_for_contexts(context_map):
    """Exact source offsets; no splitting at commas, colons or a 240-char limit.

    Strong sentence/semicolon/newline boundaries delimit evidence. Existing
    retrieval chunks remain unchanged (including any upstream truncation).
    A period between digits is decimal punctuation, not a sentence boundary.
    """
    output = {}
    for ci, (cid, text) in enumerate(context_map.items(), 1):
        start = 0
        ends = [m.end() for m in re.finditer(r"[。！？；!?;\n]+|(?<!\d)\.(?!\d)", text)]
        if not ends or ends[-1] != len(text):
            ends.append(len(text))
        si = 0
        for end in ends:
            if text[start:end].strip():
                si += 1
                output[f"E{ci}S{si}"] = dict(id=cid, start=start, end=end, text=text[start:end])
            start = end
    return output


def passages_for_contexts(context_map):
    """Pack adjacent complete clauses toward C1's 240-character target.

    A single longer clause remains whole inside the original retrieval chunk.
    The target is not a hard cutoff. No source text is added, reordered or lost.
    """
    atoms = atomic_passages_for_contexts(context_map)
    output = {}
    for ci, (cid, text) in enumerate(context_map.items(), 1):
        spans = [p for p in atoms.values() if p["id"] == cid]
        packed = []
        for span in spans:
            if packed and span["end"] - packed[-1]["start"] <= c1.MAX_PASSAGE_CHARS:
                packed[-1]["end"] = span["end"]
            else:
                packed.append(dict(start=span["start"], end=span["end"]))
        for si, span in enumerate(packed, 1):
            output[f"E{ci}S{si}"] = dict(id=cid, **span, text=text[span["start"]:span["end"]])
    return output


def build_messages(question, results, mode="C3B"):
    if mode != "C3B":
        raise ValueError("clauses adapter supports C3B only")
    return c1.build_messages(question, results, mode="C1", passage_builder=passages_for_contexts)


def canonicalize(response, context_map):
    result, meta = c1.canonicalize(response, context_map, passage_builder=passages_for_contexts)
    meta["segmentation"] = "C3B-v2: packed complete clauses; unchanged source chunks"
    return result, meta
