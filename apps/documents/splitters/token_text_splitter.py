"""Simple token-based text splitter.

This splitter approximates tokenization by splitting on whitespace and
counts tokens as words. It produces overlapping chunks measured in tokens.
It's intentionally lightweight to avoid requiring an LLM tokenizer library.
"""
from typing import List, Dict


def _tokens(text: str) -> List[str]:
    # naive tokenizer: split on whitespace
    return text.split()


def _detokens(tokens: List[str]) -> str:
    return ' '.join(tokens)


def split(text: str, chunk_size: int = 200, chunk_overlap: int = 40) -> List[Dict]:
    """Split text into token-aware chunks.

    Returns a list of {'text': ..., 'meta': {'start_token': i, 'end_token': j}}
    """
    if not text:
        return []

    toks = _tokens(text)
    n = len(toks)
    if n == 0:
        return []

    chunks = []
    start = 0
    while start < n:
        end = min(start + chunk_size, n)
        chunk_toks = toks[start:end]
        chunks.append({'text': _detokens(chunk_toks), 'meta': {'start_token': start, 'end_token': end}})
        if end == n:
            break
        start = end - chunk_overlap
        if start < 0:
            start = 0

    return chunks
