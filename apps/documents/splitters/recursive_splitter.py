"""Recursive / structure-aware splitter.

This splitter tries to preserve document structure by splitting along
large separators (headings, double newlines) and then combining
paragraphs into chunks up to a target character size with overlap.
"""
import re
from typing import List, Dict


def _chunk_paragraphs(paragraphs: List[str], max_chars: int, overlap_chars: int) -> List[str]:
    chunks = []
    cur = []
    cur_len = 0

    for p in paragraphs:
        plen = len(p)
        if cur_len + plen <= max_chars or not cur:
            cur.append(p)
            cur_len += plen + 2
        else:
            chunks.append('\n\n'.join(cur).strip())
            # start new chunk; include overlap tail from previous chunk
            if overlap_chars > 0:
                tail = ('\n\n'.join(cur))[-overlap_chars:]
                cur = [tail, p]
                cur_len = len(tail) + plen + 2
            else:
                cur = [p]
                cur_len = plen + 2

    if cur:
        chunks.append('\n\n'.join(cur).strip())
    return chunks


def split(text: str, max_chunk_chars: int = 1000, overlap_chars: int = 200) -> List[Dict]:
    """Split `text` into a list of chunk dicts: {'text': ..., 'meta': {...}}.

    Strategy:
    - First split on Markdown-style headings or any line that looks like a
      heading (all-caps or starts with 'Chapter'/'Section'). Those become
      natural section boundaries.
    - Within each section, split into paragraphs (two or more newlines).
    - Recombine paragraphs to form chunks close to `max_chunk_chars` with
      specified `overlap_chars` overlap.
    """
    if not text:
        return []

    # Normalize newlines
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Find candidate section boundaries (markdown headings or common section words)
    lines = text.split('\n')
    sections = []
    cur_lines = []
    heading_re = re.compile(r'^(#{1,6}\s+|Chapter\b|SECTION\b|Section\b)', re.I)

    for ln in lines:
        if heading_re.match(ln.strip()):
            # start a new section when we hit a heading-like line
            if cur_lines:
                sections.append('\n'.join(cur_lines).strip())
            cur_lines = [ln]
        else:
            cur_lines.append(ln)

    if cur_lines:
        sections.append('\n'.join(cur_lines).strip())

    # For each section, split into paragraphs and chunk
    chunks = []
    for i, sec in enumerate(sections):
        # paragraphs: split on two or more newlines
        paragraphs = [p.strip() for p in re.split(r'\n{2,}', sec) if p.strip()]
        sec_chunks = _chunk_paragraphs(paragraphs, max_chunk_chars, overlap_chars)
        for j, c in enumerate(sec_chunks):
            chunks.append({'text': c, 'meta': {'section_index': i, 'chunk_index': j}})

    return chunks
