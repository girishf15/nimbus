from flask import render_template, request, session, current_app as app, redirect, url_for, send_from_directory, jsonify, send_file
from werkzeug.utils import secure_filename
from . import documents_bp
from .file_store import delete_file as fs_delete
from flask import current_app
from .db_store import save_metadata as db_save_metadata, list_uploaded_files as db_list_uploaded_files, update_metadata as db_update_metadata, find_file as db_find_file
import os
import requests
import hashlib
import config

# Import configurations from centralized config module
UPLOADS_DIR = config.UPLOADS_DIR
ALLOWED_EXTENSIONS = set(config.ALLOWED_EXTENSIONS)
OLLAMA_URL = config.OLLAMA_URL
DEFAULT_CHUNK_SIZE = config.DEFAULT_CHUNK_SIZE
DEFAULT_CHUNK_OVERLAP = config.DEFAULT_CHUNK_OVERLAP
DEFAULT_EMBEDDING_MODEL = config.DEFAULT_EMBEDDING_MODEL
EMBEDDING_REQUEST_TIMEOUT = config.EMBEDDING_REQUEST_TIMEOUT


def allowed_file(filename: str) -> bool:
    _, ext = os.path.splitext(filename.lower())
    return ext in ALLOWED_EXTENSIONS


@documents_bp.route('/documents')
def documents_page():
    username = session.get('nimbus_user')
    if not username:
        return redirect(url_for('login_get'))
    files = db_list_uploaded_files(username)
    return render_template('documents.html', username=username, files=files)


@documents_bp.route('/documents/upload', methods=['POST'])
def upload_document():
    username = session.get('nimbus_user')
    if not username:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'Not logged in'}), 401
        return redirect(url_for('login_get'))

    if 'file' not in request.files:
        print('No file part', 'error')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'No file provided'})
        return redirect(url_for('documents.documents_page'))

    file = request.files['file']
    if file.filename == '':
        print('No selected file', 'error')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'No file selected'})
        return redirect(url_for('documents.documents_page'))

    filename = secure_filename(file.filename)
    if not allowed_file(filename):
        print('File type not allowed', 'error')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': 'File type not allowed'})
        return redirect(url_for('documents.documents_page'))

    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    dest = UPLOADS_DIR / filename
    file.save(dest)

    # store in DB-backed store if available
    record = {
        'filename': filename,
        'uploader': username,
        'size': dest.stat().st_size,
        'enabled': False,
        'parsing_status': 'Unparsed',
        'file_path': str(dest),
    }

    db_save_metadata(record)
    print(f'Uploaded {filename}', 'success')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'filename': filename})
    return redirect(url_for('documents.documents_page'))


@documents_bp.route('/documents/enable/<filename>', methods=['POST'])
def enable_document(filename):
    username = session.get('nimbus_user')
    if not username:
        return redirect(url_for('login_get'))

    db_update_metadata(filename, {'enabled': True, 'parsing_status': 'Parsed'})
    print(f'Enabled {filename}', 'success')
    return redirect(url_for('documents.documents_page'))


@documents_bp.route('/documents/toggle_enable/<filename>', methods=['POST'])
def toggle_enable(filename):
    username = session.get('nimbus_user')
    if not username:
        return redirect(url_for('login_get'))

    rec = db_find_file(filename)
    if not rec:
        print('File not found', 'error')
        return redirect(url_for('documents.documents_page'))
    new_val = not rec.get('enabled', False)
    db_update_metadata(filename, {'enabled': new_val})
    
    print(f"Set enabled={new_val} for {filename}", 'success')
    # If request expects JSON (AJAX), return JSON
    if request.headers.get('Accept') == 'application/json' or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True, 'enabled': new_val})
    return redirect(url_for('documents.documents_page'))


@documents_bp.route('/documents/parse/<filename>', methods=['POST'])
def parse_document(filename):
    username = session.get('nimbus_user')
    if not username:
        return redirect(url_for('login_get'))

    # Accept parser selection from form data (default to pymupdf)
    parser_choice = request.form.get('parser', 'pymupdf')
    current_app.logger.info(f'=== PARSE REQUEST ===')
    current_app.logger.info(f'Filename: {filename}')
    current_app.logger.info(f'Parser choice from form: {parser_choice}')
    current_app.logger.info(f'All form data: {request.form}')
    current_app.logger.info(f'Request headers: {dict(request.headers)}')

    # Find file path
    file_path = None
    rec = db_find_file(filename)
    file_path = rec.get('file_path')
    current_app.logger.info(f'File path from DB: {file_path}')

    if parser_choice == 'pymupdf':
        from .parsers.pymupdf_parser import parse as parser_fn
        current_app.logger.info('Using PyMuPDF parser')
    elif parser_choice == 'unstructured':
        from .parsers.unstructured_parser import parse_document_unstructured
        parser_fn = lambda path: parse_document_unstructured(path)
        current_app.logger.info('Using Unstructured parser')
    elif parser_choice == 'ocr':
        from .parsers.ocr_parser import parse as ocr_parse
        parser_fn = ocr_parse
        current_app.logger.info('Using OCR parser for image-heavy documents')
    else:
        from .parsers.pdfplumber_parser import parse as parser_fn
        current_app.logger.info(f'Using pdfplumber parser')
        
    text = parser_fn(file_path)
    current_app.logger.info(f'Parsed text length: {len(text) if text else 0}')
    from .db_store import set_parsed_text
    saved = set_parsed_text(filename, text, parser_choice)
    import time
    time.sleep(1)  # simulate delay
    return redirect(url_for('documents.documents_page'))



@documents_bp.route('/documents/split/<filename>', methods=['POST'])
def split_document(filename):
    """Run a splitter over the parsed text for a file and store the splits."""
    username = session.get('nimbus_user')
    if not username:
        return redirect(url_for('login_get'))

    splitter_choice = request.form.get('splitter', 'recursive')
    print(f'Splitter choice--->: {splitter_choice}')

    try:
        max_chars = int(request.form.get('max_chars', DEFAULT_CHUNK_SIZE))
    except Exception:
        max_chars = DEFAULT_CHUNK_SIZE
    try:
        overlap = int(request.form.get('overlap', DEFAULT_CHUNK_OVERLAP))
    except Exception:
        overlap = DEFAULT_CHUNK_OVERLAP

    # Fetch parsed text
    parsed_text = None
    rec = db_find_file(filename)
    from .db_store import get_splits

    conn = current_app.get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT parsed_text FROM documents WHERE filename = %s LIMIT 1", (filename,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    parsed_text = row[0] if row else None

    if not parsed_text:
        print('No parsed text found for file. Parse first.', 'error')
        return redirect(url_for('documents.documents_page'))

    # choose splitter
    if splitter_choice == 'token':
        from .splitters.token_text_splitter import split as splitter_fn
        splits = splitter_fn(parsed_text, chunk_size=max_chars if max_chars else 200, chunk_overlap=overlap)
    elif splitter_choice == 'semantic':
        from .splitters.semantic_splitter import split_text_semantically
        # Semantic splitter doesn't use max_chars/overlap - it finds natural boundaries
        chunks = split_text_semantically(parsed_text, ollama_base_url=OLLAMA_URL, embedding_model=DEFAULT_EMBEDDING_MODEL)
        # Convert to expected format
        splits = [{'text': chunk} for chunk in chunks]
    else:
        from .splitters.recursive_splitter import split as splitter_fn
        splits = splitter_fn(parsed_text, max_chunk_chars=max_chars, overlap_chars=overlap)

    # store splits and record which splitter was used
    import json as _json
    from .db_store import set_splits_with_meta
    ok = set_splits_with_meta(filename, _json.dumps(splits), splitter_name=splitter_choice)

    if ok:
        print(f'Splits stored for {filename} using {splitter_choice}', 'success')
    else:
        print('Failed to store splits', 'error')
    return redirect(url_for('documents.documents_page'))



@documents_bp.route('/documents/embeddings/<filename>', methods=['POST'])
def embeddings_document(filename):
    username = session.get('nimbus_user')
    if not username:
        return jsonify({'success': False, 'error': 'unauthenticated'}), 401

    model_name = request.form.get('model', 'mxbai_embed_large')
    print(f'Generating embeddings using model: {model_name}')
    safe_model_name = model_name.lower().replace("-", "_")
    table_name = f"document_embeddings_{safe_model_name}"
    print(f'Using table: {table_name}')

    # get file splits from DB (adjust helper)
    from .db_store import get_splits
    splits = get_splits(filename)
    if not splits:
        return jsonify({'success': False, 'error': 'no_splits'}), 400

    # prepare Ollama endpoint
    ep = f"{OLLAMA_URL.rstrip('/')}/v1/embeddings"
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    embeddings = []
    for chunk in splits:
        text = chunk.get('text') if isinstance(chunk, dict) else str(chunk)
        vec = None

        payload = {'model': model_name.replace("_", "-"), 'input': text}
        try:
            resp = requests.post(ep, json=payload, timeout=EMBEDDING_REQUEST_TIMEOUT, headers=headers)
            if resp.ok:
                data = resp.json()
                # assume OpenAI-style
                vec = data['data'][0]['embedding']
        except Exception as e:
            current_app.logger.warning(f"Ollama failed: {e}")

        # fallback: deterministic mock
        if vec is None:
            h = hashlib.sha256(text.encode()).hexdigest()
            vec = [(int(h[i:i+8], 16) % 1000) / 1000.0 for i in range(0, 64, 8)]

        embeddings.append((filename, text, vec))

    # persist into document_embeddings_<model_name>
    conn = current_app.get_db_conn()
    with conn.cursor() as cur:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                id SERIAL PRIMARY KEY,
                filename TEXT,
                text TEXT,
                embedding VECTOR
            )
        """)
        for fn, txt, vec in embeddings:
            cur.execute(
                f"INSERT INTO {table_name} (filename, text, embedding) VALUES (%s, %s, %s)",
                (fn, txt, vec)
            )
    conn.commit()

    # update metadata (mark embeddings True and store model name)
    result = db_update_metadata(filename, {'embeddings': True, 'embeddings_model': model_name})
    print(f'Update metadata result: {result}')
    print(f'Embeddings stored for {filename} using {model_name}', 'success')    

    return redirect(url_for('documents.documents_page'))

@documents_bp.route('/documents/api/delete/<filename>', methods=['POST'])
def api_delete_document(filename):
    """AJAX-friendly delete endpoint that removes the file and metadata."""
    username = session.get('nimbus_user')
    if not username:
        return jsonify({'success': False, 'error': 'unauthenticated'}), 401

    deleted = False
    from .db_store import delete_file as db_delete
    deleted = db_delete(filename)
    fs_delete(filename)
    deleted = True

    if deleted:
        return jsonify({'success': True})
    return jsonify({'success': False}), 500


@documents_bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(str(UPLOADS_DIR), filename)


@documents_bp.route('/documents/delete/<filename>', methods=['POST'])
def delete_document(filename):
    username = session.get('nimbus_user')
    if not username:
        return redirect(url_for('login_get'))

    # remove from DB-backed store if available
    deleted = False
    from .db_store import delete_file as db_delete
    deleted = db_delete(filename)
    from .file_store import delete_file as fs_delete
    fs_delete(filename)
    deleted = True
    print(f'Deleted {filename}', 'success')
    return redirect(url_for('documents.documents_page'))


@documents_bp.route('/documents/preview/<filename>', methods=['GET'])
def preview_document(filename):
    """Serve the actual PDF/document file for viewing"""
    username = session.get('username')
    if not username:
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    conn = current_app.get_db_conn()
    cur = conn.cursor()
    
    # Verify user owns this document
    cur.execute("""
        SELECT size, filename, parsed_text, parsing_status 
        FROM documents 
        WHERE filename = %s AND uploader = %s
    """, (filename, username))
    
    result = cur.fetchone()
    cur.close()
    
    if not result:
        return jsonify({'success': False, 'message': 'Document not found'}), 404
    
    size, filename, parsed_text, parsing_status = result
    
    # Determine content type
    is_pdf = filename.lower().endswith('.pdf')
    
    if is_pdf:
        # Serve the actual PDF file
        file_path = UPLOADS_DIR / filename
        
        if not file_path.exists():
            return jsonify({'success': False, 'message': 'File not found on disk'}), 404
        
        return send_file(str(file_path), mimetype='application/pdf', as_attachment=False)
    else:
        # For non-PDF files (DOCX, TXT, etc.), return parsed text as JSON
        if parsing_status != 'Parsed' or not parsed_text:
            return jsonify({
                'success': False, 
                'message': 'Document not yet parsed. Please parse it first.'
            }), 400
        
        return jsonify({
            'success': True,
            'filename': filename,
            'text': parsed_text,
            'size': size,
            'is_pdf': False
        })
