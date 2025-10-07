from flask import current_app
import uuid
from datetime import datetime
import json
import psycopg2.extras


def ensure_table():
    """Create documents table if it doesn't exist."""
    conn = current_app.get_db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    id TEXT PRIMARY KEY,
                    filename TEXT NOT NULL,
                    uploader TEXT,
                    created_at TIMESTAMP,
                    enabled BOOLEAN DEFAULT FALSE,
                    parsing_status TEXT,
                    size INTEGER,
                    file_path TEXT,
                    parser_name TEXT,
                    parsed_text TEXT,
                    splitter_name TEXT,
                    splits JSON,
                    embeddings_model TEXT,
                    embeddings BOOLEAN DEFAULT FALSE
                )
                """
            )
        conn.commit()
    finally:
        conn.close()


def list_uploaded_files(username):
    ensure_table()
    conn = current_app.get_db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, filename, uploader, created_at, enabled, parsing_status, size, file_path, parser_name, splitter_name, embeddings_model, splits, embeddings FROM documents WHERE uploader = %s ORDER BY created_at DESC",
                (username,)
            )
            rows = cur.fetchall()
    finally:
        conn.close()
    files = []
    for r in rows:
        id, filename, uploader, created_at, enabled, parsing_status, size, file_path, parser_name, splitter_name, embeddings_model, splits, embeddings = r
        files.append({
            'id': id,
            'filename': filename,
            'uploader': uploader,
            'created_at': created_at.isoformat() if created_at else None,
            'enabled': enabled,
            'parsing_status': parsing_status,
            'size': size,
            'file_path': file_path,
            'parser_name': parser_name,
            'splitter_name': splitter_name,
            'embeddings_model': embeddings_model,
            'has_splits': bool(splits),
            'has_embeddings': bool(embeddings),
        })
    return files


def set_parsed_text(filename: str, text: str, parser_name: str = None):
    ensure_table()
    conn = current_app.get_db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE documents SET parsing_status = %s, file_path = file_path, parser_name = %s, parsed_text = %s WHERE filename = %s RETURNING id", ('Parsed', parser_name, text, filename))
            row = cur.fetchone()
        conn.commit()
        return bool(row)
    finally:
        conn.close()


def set_splits(filename: str, splits_json: str):
    """Store splits (JSON string) into the splits column."""
    ensure_table()
    conn = current_app.get_db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE documents SET splits = %s WHERE filename = %s RETURNING id", (splits_json, filename))
            row = cur.fetchone()
        conn.commit()
        return bool(row)
    finally:
        conn.close()


def set_splits_with_meta(filename: str, splits_json: str, splitter_name: str = None):
    """Store splits and optionally record which splitter was used."""
    ensure_table()
    conn = current_app.get_db_conn()
    try:
        with conn.cursor() as cur:
            if splitter_name:
                cur.execute("UPDATE documents SET splits = %s, splitter_name = %s WHERE filename = %s RETURNING id", (splits_json, splitter_name, filename))
            else:
                cur.execute("UPDATE documents SET splits = %s WHERE filename = %s RETURNING id", (splits_json, filename))
            row = cur.fetchone()
        conn.commit()
        return bool(row)
    finally:
        conn.close()

def get_embeddings(filename: str):
    ensure_table()
    conn = current_app.get_db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT embeddings FROM documents WHERE filename = %s LIMIT 1", (filename,))
            row = cur.fetchone()
        if not row:
            return None
        return row[0]
    finally:
        conn.close()


def get_splits(filename: str):
    ensure_table()
    conn = current_app.get_db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT splits FROM documents WHERE filename = %s LIMIT 1", (filename,))
            row = cur.fetchone()
        if not row:
            return None
        return row[0]
    finally:
        conn.close()


def save_metadata(record: dict):
    ensure_table()
    conn = current_app.get_db_conn()
    try:
        new_id = record.get('id') or str(uuid.uuid4())
        created_at = record.get('created_at') or datetime.utcnow()
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO documents (id, filename, uploader, created_at, enabled, parsing_status, size, file_path) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                (
                    new_id,
                    record.get('filename'),
                    record.get('uploader'),
                    created_at,
                    record.get('enabled', False),
                    record.get('parsing_status', 'Unparsed'),
                    record.get('size'),
                    record.get('file_path'),
                ),
            )
        conn.commit()
        return new_id
    finally:
        conn.close()


def find_file(filename: str):
    ensure_table()
    conn = current_app.get_db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, filename, uploader, created_at, enabled, parsing_status, size, file_path, parser_name, splitter_name, embeddings_model, splits, embeddings FROM documents WHERE filename = %s LIMIT 1",
                (filename,),
            )
            row = cur.fetchone()
    finally:
        conn.close()
    if not row:
        return None
    id, filename, uploader, created_at, enabled, parsing_status, size, file_path, parser_name, splitter_name, embeddings_model, splits, embeddings = row
    return {
        'id': id,
        'filename': filename,
        'uploader': uploader,
        'created_at': created_at.isoformat() if created_at else None,
        'enabled': enabled,
        'parsing_status': parsing_status,
        'size': size,
        'file_path': file_path,
        'parser_name': parser_name,
        'splitter_name': splitter_name,
        'embeddings_model': embeddings_model,
        'has_splits': bool(splits),
        'has_embeddings': bool(embeddings),
    }


def update_metadata(filename: str, patch: dict):
    ensure_table()
    allowed = {'filename', 'uploader', 'enabled', 'parsing_status', 'size', 'file_path', 'embeddings', 'embeddings_model'}
    sets = []
    vals = []
    for k, v in patch.items():
        if k in allowed:
            sets.append(f"{k} = %s")
            vals.append(v)
    if not sets:
        return None
    vals.append(filename)
    sql = f"UPDATE documents SET {', '.join(sets)} WHERE filename = %s RETURNING id, filename, uploader, created_at, enabled, parsing_status, size, file_path, embeddings"
    conn = current_app.get_db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, tuple(vals))
            row = cur.fetchone()
        conn.commit()
        return bool(row)
    finally:
        conn.close()


def delete_file(filename: str):
    """Delete file record, remove local file, and cascade delete embeddings from all embedding tables."""
    ensure_table()
    conn = current_app.get_db_conn()
    try:
        with conn.cursor() as cur:
            # Get file path for physical deletion
            cur.execute("SELECT file_path FROM documents WHERE filename = %s LIMIT 1", (filename,))
            row = cur.fetchone()
            if row and row[0]:
                try:
                    import os
                    fp = row[0]
                    if os.path.exists(fp):
                        os.remove(fp)
                except Exception:
                    # ignore file removal errors
                    pass
            
            # CASCADE DELETE: Dynamically find all embedding tables and remove embeddings
            # This future-proofs against new embedding models being added
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE 'document_embeddings_%'
            """)
            embedding_tables = [row[0] for row in cur.fetchall()]
            
            total_deleted = 0
            for table in embedding_tables:
                try:
                    # Delete embeddings for this filename
                    cur.execute(f"DELETE FROM {table} WHERE filename = %s", (filename,))
                    deleted_count = cur.rowcount
                    total_deleted += deleted_count
                    if deleted_count > 0:
                        current_app.logger.info(f"Deleted {deleted_count} embeddings from {table} for {filename}")
                except Exception as e:
                    current_app.logger.warning(f"Failed to delete embeddings from {table}: {e}")
                    # Continue with other tables even if one fails
            
            if total_deleted > 0:
                current_app.logger.info(f"Total embeddings deleted: {total_deleted} across {len(embedding_tables)} tables")
            
            # Delete the document record
            cur.execute("DELETE FROM documents WHERE filename = %s RETURNING id", (filename,))
            deleted = cur.fetchone()
        conn.commit()
        return bool(deleted)
    finally:
        conn.close()
