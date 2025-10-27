import io
from typing import List, Dict
import re

try:
    import mammoth
    _HAS_MAMMOTH = True
except Exception:
    _HAS_MAMMOTH = False

try:
    from striprtf.striprtf import rtf_to_text
    _HAS_STRIPRTF = True
except Exception:
    _HAS_STRIPRTF = False


def convert_to_paragraphs(input_bytes: bytes, filename: str) -> List[Dict]:
    """Convert input bytes (docx or txt) into a list of paragraph dicts.

    Returns: [{ 'text': '...', 'meta': {'source': 'docx', 'index': 0} }, ...]
    """
    lower = filename.lower() if filename else ''
    paragraphs = []
    if lower.endswith('.docx') and _HAS_MAMMOTH:
        # Use mammoth to get simple HTML, then split on paragraph tags
        with io.BytesIO(input_bytes) as b:
            result = mammoth.extract_raw_text(b)
            text = result.value or ''
            # mammoth returns plain text with paragraphs separated by "\n\n"
            parts = [p.strip() for p in text.split('\n\n') if p.strip()]
            for i, p in enumerate(parts):
                paragraphs.append({'text': p, 'meta': {'source': 'docx', 'index': i}})
    elif lower.endswith('.rtf'):
        # RTF handling: prefer striprtf if available, otherwise fall back to a simple stripper
        if _HAS_STRIPRTF:
            try:
                # striprtf expects str, so decode bytes first
                raw = input_bytes.decode('utf-8', errors='replace')
                text = rtf_to_text(raw) or ''
            except Exception:
                text = ''
        else:
            # Very small fallback: remove RTF control words and braces; best-effort
            raw = input_bytes.decode('utf-8', errors='replace')
            # remove groups and common control words; this is lossy but keeps readable text
            text = re.sub(r'\\[a-zA-Z]+-?\d+\s?', '', raw)
            text = re.sub(r'[{}]', '', text)
            # remove other backslash escapes
            text = re.sub(r'\\[^\s]+', '', text)
        parts = [p.strip() for p in text.split('\n\n') if p.strip()]
        for i, p in enumerate(parts):
            paragraphs.append({'text': p, 'meta': {'source': 'rtf', 'index': i}})
    else:
        # Fall back to plain text
        text = input_bytes.decode('utf-8', errors='replace')
        parts = [p.strip() for p in text.split('\n\n') if p.strip()]
        for i, p in enumerate(parts):
            paragraphs.append({'text': p, 'meta': {'source': 'txt', 'index': i}})

    return paragraphs
