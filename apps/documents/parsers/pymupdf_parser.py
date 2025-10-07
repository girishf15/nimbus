"""Extract text from PDF using PyMuPDF (fitz)."""
def parse(file_path: str) -> str:
    try:
        import fitz  # PyMuPDF
    except Exception as e:
        raise RuntimeError('PyMuPDF not available: ' + str(e))

    doc = fitz.open(file_path)
    texts = []
    for page in doc:
        texts.append(page.get_text())
    return '\n\n'.join(texts)
