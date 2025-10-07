from flask import current_app


def create_user(username, password, role='user'):
    try:
        conn = current_app.get_db_conn()
        cur = conn.cursor()
        pw_hash = current_app.pwd_context.hash(password)
        cur.execute('INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)', (username, pw_hash, role))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception:
        return False


def delete_user(username):
    try:
        conn = current_app.get_db_conn()
        cur = conn.cursor()
        cur.execute('DELETE FROM users WHERE username = %s AND username != %s', (username, 'admin'))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception:
        return False


def update_user_password(username, new_password):
    try:
        conn = current_app.get_db_conn()
        cur = conn.cursor()
        new_hash = current_app.pwd_context.hash(new_password)
        cur.execute('UPDATE users SET password_hash = %s WHERE username = %s', (new_hash, username))
        conn.commit()
        cur.close()
        conn.close()
        return True
    except Exception:
        return False
