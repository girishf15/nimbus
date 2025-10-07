from flask import render_template, request, session, current_app as app, jsonify, redirect, url_for
from . import chat_bp
import requests
import os
import json
import hashlib
import re
import config

# Import configurations from centralized config module
OLLAMA_URL = config.OLLAMA_URL
STRICT_DOCS_INSTRUCTION = config.STRICT_DOCS_INSTRUCTION
EMBEDDING_MODELS = config.EMBEDDING_MODELS
MODEL_EMBEDDING_TABLE_MAP = config.MODEL_EMBEDDING_TABLE_MAP
RAG_TOP_K_PER_MODEL = config.RAG_TOP_K_PER_MODEL
RAG_TOP_K_OVERALL = config.RAG_TOP_K_OVERALL
RAG_SNIPPET_MAX_CHARS = config.RAG_SNIPPET_MAX_CHARS
CHAT_MAX_HISTORY = config.CHAT_MAX_HISTORY
CHAT_REQUEST_TIMEOUT = config.CHAT_REQUEST_TIMEOUT
EMBEDDING_REQUEST_TIMEOUT = config.EMBEDDING_REQUEST_TIMEOUT
MODELS_REQUEST_TIMEOUT = config.MODELS_REQUEST_TIMEOUT

def is_chat_model(model_name: str) -> bool:
    """Check if a model is suitable for chat (not an embedding-only model)."""
    model_lower = model_name.lower()
    # Filter out known embedding models
    for emb in EMBEDDING_MODELS:
        if emb in model_lower:
            return False
    # Additional heuristics: embedding models often have 'embed' in the name
    if 'embed' in model_lower and 'llama' not in model_lower:
        return False
    return True


@chat_bp.route('/chat')
def chat_page():
    username = session.get('nimbus_user')
    if not username:
        return redirect(url_for('login_get'))
    return render_template('chat.html', username=username)


@chat_bp.route('/chat/sessions', methods=['GET'])
def get_chat_sessions():
    """Get all chat sessions for the current user."""
    username = session.get('nimbus_user')
    if not username:
        return jsonify({'error': 'unauthenticated'}), 401
    
    try:
        conn = app.get_db_conn()
        with conn.cursor() as cur:
            cur.execute("""
                SELECT session_id, title, created_at, updated_at, message_count
                FROM chat_sessions
                WHERE username = %s
                ORDER BY updated_at DESC
                LIMIT %s
            """, (username, CHAT_MAX_HISTORY))
            rows = cur.fetchall()
            sessions = []
            for row in rows:
                sessions.append({
                    'session_id': str(row[0]),
                    'title': row[1],
                    'created_at': row[2].isoformat() if row[2] else None,
                    'updated_at': row[3].isoformat() if row[3] else None,
                    'message_count': row[4]
                })
        conn.close()
        return jsonify({'sessions': sessions})
    except Exception as e:
        app.logger.exception('Error fetching chat sessions')
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/chat/sessions', methods=['POST'])
def create_chat_session():
    """Create a new chat session."""
    username = session.get('nimbus_user')
    if not username:
        print("❌ Session creation failed: No username in session")
        return jsonify({'error': 'unauthenticated'}), 401
    
    try:
        print(f"📝 Creating new chat session for user: {username}")
        conn = app.get_db_conn()
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO chat_sessions (username, title)
                VALUES (%s, %s)
                RETURNING session_id
            """, (username, 'New Chat'))
            session_id = cur.fetchone()[0]
            conn.commit()
        conn.close()
        print(f"✅ Chat session created successfully: {session_id}")
        return jsonify({'session_id': str(session_id)})
    except Exception as e:
        app.logger.exception('Error creating chat session')
        print(f"❌ Error creating chat session: {e}")
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/chat/sessions/<session_id>', methods=['GET'])
def get_chat_session(session_id):
    """Get messages for a specific chat session."""
    username = session.get('nimbus_user')
    if not username:
        return jsonify({'error': 'unauthenticated'}), 401
    
    try:
        conn = app.get_db_conn()
        with conn.cursor() as cur:
            # Verify session belongs to user
            cur.execute("""
                SELECT username FROM chat_sessions WHERE session_id = %s
            """, (session_id,))
            row = cur.fetchone()
            if not row or row[0] != username:
                return jsonify({'error': 'session not found or unauthorized'}), 404
            
            # Get messages
            cur.execute("""
                SELECT role, content, model, created_at, metadata
                FROM chat_messages
                WHERE session_id = %s
                ORDER BY created_at ASC
            """, (session_id,))
            rows = cur.fetchall()
            messages = []
            for row in rows:
                messages.append({
                    'role': row[0],
                    'content': row[1],
                    'model': row[2],
                    'created_at': row[3].isoformat() if row[3] else None,
                    'metadata': row[4]
                })
        conn.close()
        return jsonify({'messages': messages})
    except Exception as e:
        app.logger.exception('Error fetching chat session')
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/chat/sessions/<session_id>', methods=['DELETE'])
def delete_chat_session(session_id):
    """Delete a chat session."""
    username = session.get('nimbus_user')
    if not username:
        return jsonify({'error': 'unauthenticated'}), 401
    
    try:
        conn = app.get_db_conn()
        with conn.cursor() as cur:
            # Verify and delete
            cur.execute("""
                DELETE FROM chat_sessions
                WHERE session_id = %s AND username = %s
                RETURNING session_id
            """, (session_id, username))
            result = cur.fetchone()
            conn.commit()
            if not result:
                return jsonify({'error': 'session not found'}), 404
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        app.logger.exception('Error deleting chat session')
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/chat/models')
def chat_models():
    # production: require no dev bypass here; models endpoint is public but page requires login
    try:
        resp = requests.get(f"{OLLAMA_URL}/v1/models", timeout=MODELS_REQUEST_TIMEOUT)
        resp.raise_for_status()
        try:
            models = resp.json()
        except ValueError:
            models = resp.text
        ids = None
        try:
            if isinstance(models, dict) and 'data' in models and isinstance(models['data'], list):
                # Filter out embedding-only models
                all_ids = [(m.get('id') or m.get('name')) for m in models['data']]
                ids = [mid for mid in all_ids if mid and is_chat_model(mid)]
        except Exception:
            ids = None
        result = {'models': models}
        if ids is not None:
            result['ids'] = ids
        return jsonify(result)
    except requests.exceptions.RequestException as re:
        app.logger.exception('Error contacting Ollama /models')
        resp = getattr(re, 'response', None)
        detail = None
        if resp is not None:
            try:
                detail = resp.text
            except Exception:
                detail = None
        return jsonify({'error': str(re), 'detail': detail}), 502
    except Exception as e:
        app.logger.exception('Unexpected error in chat_models')
        return jsonify({'error': str(e)}), 500


@chat_bp.route('/chat/message', methods=['POST'])
def chat_message():
    if not session.get('nimbus_user'):
        return jsonify({'error': 'unauthenticated'}), 401

    if request.is_json:
        body = request.get_json()
    else:
        body = request.form.to_dict()

    # allow caller to opt-out of strict-document behavior by passing strict=false
    strict_flag = str(body.get('strict', 'true')).lower()

    model = body.get('model')
    message = body.get('message')
    image_b64 = body.get('image')
    history = body.get('history', [])  # Get conversation history from client
    session_id = body.get('session_id')  # Optional: session ID for persistence

    # Debug logging
    username = session.get('nimbus_user')
    print(f"=== CHAT MESSAGE DEBUG ===")
    print(f"Username: {username}")
    print(f"Model: {model}")
    print(f"Message length: {len(message) if message else 0}")
    print(f"Session ID: {session_id}")
    print(f"History length: {len(history)}")
    print(f"========================")

    if not model or not message:
        return jsonify({'error': 'model and message required'}), 400

    if image_b64:
        message = f"{message}\n\n[IMAGE_BASE64]\n{image_b64}"

    # Attempt to compute message embedding and retrieve nearest document chunks
    system_context = None
    try:
        mappings = MODEL_EMBEDDING_TABLE_MAP.get(model) or []
        
        # Before computing embeddings, check whether the user has any enabled documents
        username = session.get('nimbus_user')
        # fetch enabled filenames for this user
        enabled_files = []
        try:
            conn = app.get_db_conn()
            with conn.cursor() as cur:
                cur.execute("SELECT filename FROM documents WHERE uploader = %s AND enabled = TRUE", (username,))
                rows = cur.fetchall()
                enabled_files = [r[0] for r in rows]
            conn.close()
        except Exception:
            app.logger.exception('Failed to query enabled documents')

        print(f"Metadata: username: {username}, enabled_files={enabled_files}")

        # just proxy the chat request to Ollama normally
        if not enabled_files:
            print("No enabled documents; skipping retrieval and proxying chat directly")
            url = f"{OLLAMA_URL}/v1/chat/completions"
            # Build messages from history (exclude the last user message as we'll add current one)
            messages = []
            if history and len(history) > 1:
                # Add all messages except the last one (which is the current message)
                messages = history[:-1]
            # Add current message
            messages.append({'role': 'user', 'content': message})
            payload = {'model': model, 'messages': messages}
            headers = {'Content-Type': 'application/json'}
            resp = requests.post(url, json=payload, headers=headers, timeout=CHAT_REQUEST_TIMEOUT)
            resp.raise_for_status()
            result = resp.json()
            
            # Save messages to database if session_id provided
            if session_id:
                try:
                    username = session.get('nimbus_user')
                    print(f"💾 Saving messages to DB for session: {session_id}")
                    conn = app.get_db_conn()
                    with conn.cursor() as cur:
                        # First verify the session exists and belongs to the user
                        cur.execute("""
                            SELECT username FROM chat_sessions WHERE session_id = %s
                        """, (session_id,))
                        session_row = cur.fetchone()
                        
                        if not session_row:
                            print(f"⚠️ Session {session_id} not found in database - creating new session")
                            # Create the session if it doesn't exist
                            cur.execute("""
                                INSERT INTO chat_sessions (session_id, username, title)
                                VALUES (%s, %s, %s)
                            """, (session_id, username, 'New Chat'))
                            print(f"✅ Created missing session: {session_id}")
                        elif session_row[0] != username:
                            print(f"❌ Session {session_id} belongs to different user: {session_row[0]} != {username}")
                            raise Exception(f"Session does not belong to current user")
                        
                        # Save user message
                        cur.execute("""
                            INSERT INTO chat_messages (session_id, role, content, model)
                            VALUES (%s, %s, %s, %s)
                        """, (session_id, 'user', message, model))
                        print(f"✅ Saved user message")
                        
                        # Extract and save assistant response
                        assistant_reply = ''
                        if result.get('choices') and result['choices'][0].get('message'):
                            assistant_reply = result['choices'][0]['message'].get('content', '')
                        
                        if assistant_reply:
                            cur.execute("""
                                INSERT INTO chat_messages (session_id, role, content, model)
                                VALUES (%s, %s, %s, %s)
                            """, (session_id, 'assistant', assistant_reply, model))
                            print(f"✅ Saved assistant message")
                        
                        conn.commit()
                        print(f"✅ Database commit successful")
                    conn.close()
                except Exception as e:
                    app.logger.exception('Error saving chat messages to database (no docs path)')
                    print(f"❌ Error saving to database: {e}")
                    # Don't fail the request if saving fails
            else:
                print(f"⚠️ No session_id provided - messages NOT saved to database")
            
            return jsonify(result)

        print("Found enabled documents; proceeding with multi-model retrieval")
        
        # NEW APPROACH: Query each embedding model independently and merge results
        all_results = []
        seen_texts = set()
        
        conn = app.get_db_conn()
        with conn.cursor() as cur:
            for entry in mappings:
                table_name = entry.get('table')
                emb_model = entry.get('embedding_model')
                
                print(f"Querying table {table_name} with model {emb_model}")
                
                # Check if table exists first
                try:
                    cur.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_schema = 'public' 
                            AND table_name = %s
                        )
                    """, (table_name,))
                    table_exists = cur.fetchone()[0]
                    
                    if not table_exists:
                        print(f"  ⚠️ Table {table_name} does not exist, skipping")
                        continue
                except Exception as e:
                    print(f"  ⚠️ Error checking table existence: {e}")
                    continue
                
                # Compute embedding for this specific model
                try:
                    emb_ep = f"{OLLAMA_URL.rstrip('/')}/v1/embeddings"
                    emb_payload = {'model': emb_model, 'input': message}
                    emb_headers = {'Content-Type': 'application/json'}
                    eresp = requests.post(emb_ep, json=emb_payload, headers=emb_headers, timeout=EMBEDDING_REQUEST_TIMEOUT)
                    eresp.raise_for_status()
                    edata = eresp.json()
                    
                    vec = None
                    if isinstance(edata, dict) and 'data' in edata and isinstance(edata['data'], list):
                        vec = edata['data'][0].get('embedding')
                    
                    if vec:
                        vector_str = '[' + ','.join([str(float(x)) for x in vec]) + ']'
                        # Get top K from this embedding model's table
                        sql = f"SELECT filename, text, embedding <-> %s::vector AS distance FROM {table_name} WHERE filename = ANY(%s) ORDER BY distance ASC LIMIT %s"
                        cur.execute(sql, (vector_str, enabled_files, RAG_TOP_K_PER_MODEL))
                        rows = cur.fetchall()
                        
                        for r in rows:
                            fn, txt, dist = r[0], r[1], r[2]
                            # Deduplicate based on text content (first 1000 chars)
                            key = (fn, (txt or '')[:1000])
                            if key in seen_texts:
                                continue
                            seen_texts.add(key)
                            # Track which model found this chunk
                            all_results.append((fn, txt or '', dist, emb_model))
                            print(f"  Found chunk from {fn} (distance: {dist:.4f}, model: {emb_model})")
                    else:
                        print(f"  No embedding vector returned for model {emb_model}")
                        
                except Exception as e:
                    print(f"  Error querying with model {emb_model}: {e}")
                    app.logger.exception(f'Failed to retrieve with model {emb_model}')
                    continue
        
        conn.close()

        # Sort all results by distance and take top K overall
        if all_results:
            all_results.sort(key=lambda x: x[2])  # Sort by distance
            top = all_results[:RAG_TOP_K_OVERALL]
            snippets = []
            print(f"Selected top {len(top)} chunks from {len(all_results)} total results:")
            for fn, txt, dist, emb_model in top:
                snippet = txt[:RAG_SNIPPET_MAX_CHARS]
                # Don't include model metadata in LLM context - just the content
                snippets.append(f"[Source: {fn}]\n{snippet}")
                # But log it for debugging
                print(f"  - {fn} (distance: {dist:.4f}, model: {emb_model})")
            system_context = "\n\n--- Retrieved documents:\n" + "\n\n".join(snippets)
        else:
            print("⚠️ No results found from any embedding model - some tables may not exist yet")
            print("💡 Tip: Generate embeddings for your enabled documents first")
            
    except Exception:
        # don't fail chat if retrieval fails; just continue without context
        app.logger.exception('Failed to compute embeddings or retrieve documents')

    try:
        url = f"{OLLAMA_URL}/v1/chat/completions"
        messages = []
        
        # Add conversation history (exclude the last user message which we'll add separately)
        if history and len(history) > 1:
            # Add all previous messages except the last one
            for msg in history[:-1]:
                messages.append({'role': msg.get('role'), 'content': msg.get('content')})
        
        # Add system context if documents are enabled
        if system_context:
            # if strict flag isn't explicitly 'false', prepend a strict system instruction
            if strict_flag != 'false':
                messages.insert(0, {'role': 'system', 'content': STRICT_DOCS_INSTRUCTION})
            messages.insert(1 if strict_flag != 'false' else 0, {'role': 'system', 'content': system_context})
        
        # Add current user message
        messages.append({'role': 'user', 'content': message})
        
        payload = {'model': model, 'messages': messages}
        headers = {'Content-Type': 'application/json'}
        resp = requests.post(url, json=payload, headers=headers, timeout=CHAT_REQUEST_TIMEOUT)
        resp.raise_for_status()
        result = resp.json()
        
        # Save messages to database if session_id provided
        if session_id:
            try:
                username = session.get('nimbus_user')
                print(f"💾 Saving messages to DB (RAG path) for session: {session_id}")
                conn = app.get_db_conn()
                with conn.cursor() as cur:
                    # First verify the session exists and belongs to the user
                    cur.execute("""
                        SELECT username FROM chat_sessions WHERE session_id = %s
                    """, (session_id,))
                    session_row = cur.fetchone()
                    
                    if not session_row:
                        print(f"⚠️ Session {session_id} not found in database - creating new session")
                        # Create the session if it doesn't exist
                        cur.execute("""
                            INSERT INTO chat_sessions (session_id, username, title)
                            VALUES (%s, %s, %s)
                        """, (session_id, username, 'New Chat'))
                        print(f"✅ Created missing session: {session_id}")
                    elif session_row[0] != username:
                        print(f"❌ Session {session_id} belongs to different user: {session_row[0]} != {username}")
                        raise Exception(f"Session does not belong to current user")
                    
                    # Save user message
                    cur.execute("""
                        INSERT INTO chat_messages (session_id, role, content, model)
                        VALUES (%s, %s, %s, %s)
                    """, (session_id, 'user', message, model))
                    print(f"✅ Saved user message (RAG)")
                    
                    # Extract and save assistant response
                    assistant_reply = ''
                    if result.get('choices') and result['choices'][0].get('message'):
                        assistant_reply = result['choices'][0]['message'].get('content', '')
                    
                    if assistant_reply:
                        cur.execute("""
                            INSERT INTO chat_messages (session_id, role, content, model)
                            VALUES (%s, %s, %s, %s)
                        """, (session_id, 'assistant', assistant_reply, model))
                        print(f"✅ Saved assistant message (RAG)")
                    
                    conn.commit()
                    print(f"✅ Database commit successful (RAG)")
                conn.close()
            except Exception as e:
                app.logger.exception('Error saving chat messages to database')
                print(f"❌ Error saving to database (RAG): {e}")
                # Don't fail the request if saving fails
        else:
            print(f"⚠️ No session_id provided (RAG path) - messages NOT saved to database")
        
        return jsonify(result)
    except requests.exceptions.RequestException as re:
        app.logger.exception('Error proxying to Ollama /v1/chat/completions')
        resp = getattr(re, 'response', None)
        detail = None
        if resp is not None:
            try:
                detail = resp.text
            except Exception:
                detail = None
        return jsonify({'error': str(re), 'detail': detail}), 502
    except Exception as e:
        app.logger.exception('Unexpected error in chat_message')
        return jsonify({'error': str(e)}), 500
