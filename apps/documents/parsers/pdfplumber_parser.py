"""Extract text from PDF using pdfplumber."""
def parse(file_path: str) -> str:
    try:
        import pdfplumber
    except Exception as e:
        raise RuntimeError('pdfplumber not available: ' + str(e))

    texts = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            texts.append(page.extract_text() or '')
    return '\n\n'.join(texts)
