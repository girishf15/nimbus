from flask import render_template, request, session, redirect, url_for, flash, jsonify, current_app
from . import users_bp
from .utils import create_user, delete_user, update_user_password


@users_bp.route('/user_management')
def user_management():
    username = session.get('nimbus_user')
    role = session.get('role')
    if not username:
        return redirect(url_for('login_get'))
    if role != 'admin':
        flash('Access denied: admin only', 'error')
        return redirect(url_for('chat.chat_page'))

    users = []
    try:
        conn = current_app.get_db_conn()
        cur = conn.cursor()
        cur.execute('SELECT username, role FROM users ORDER BY username')
        rows = cur.fetchall()
        for r in rows:
            users.append({'username': r[0], 'role': r[1]})
        cur.close()
        conn.close()
    except Exception as e:
        flash(f'Error fetching users: {e}', 'error')
    return render_template('user_management.html', users=users)


@users_bp.route('/admin/create_user', methods=['POST'])
def admin_create_user():
    # admin_required check
    if session.get('role') != 'admin':
        flash('Admin access required', 'error')
        return redirect(url_for('chat.chat_page'))
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role', 'user')
    if not username or not password:
        flash('Username and password are required', 'error')
        return redirect(url_for('users.user_management'))
    if create_user(username, password, role):
        flash('User created successfully', 'success')
    else:
        flash('Failed to create user (maybe exists)', 'error')
    return redirect(url_for('users.user_management'))


@users_bp.route('/admin/reset_password/<username>', methods=['POST'])
def admin_reset_password(username):
    if session.get('role') != 'admin':
        flash('Admin access required', 'error')
        return redirect(url_for('chat.chat_page'))
    newpw = request.form.get('new_password')
    if not newpw:
        flash('New password required', 'error')
        return redirect(url_for('users.user_management'))
    if update_user_password(username, newpw):
        flash(f'Password reset for {username}', 'success')
    else:
        flash('Failed to reset password', 'error')
    return redirect(url_for('users.user_management'))


@users_bp.route('/admin/delete_user/<username>', methods=['POST'])
def admin_delete_user(username):
    if session.get('role') != 'admin':
        flash('Admin access required', 'error')
        return redirect(url_for('chat.chat_page'))
    if username == 'admin':
        flash('Cannot delete admin user', 'error')
        return redirect(url_for('users.user_management'))
    if delete_user(username):
        flash(f'User {username} deleted', 'success')
    else:
        flash('Failed to delete user', 'error')
    return redirect(url_for('users.user_management'))


@users_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    username = session.get('nimbus_user')
    if not username:
        return redirect(url_for('login_get'))

    if request.method == 'POST':
        current = request.form.get('current_password')
        newpw = request.form.get('new_password')
        confirm = request.form.get('confirm_password')
        if not current or not newpw or not confirm:
            flash('All fields are required', 'error')
            return redirect(url_for('users.change_password'))
        if newpw != confirm:
            flash('New password and confirmation do not match', 'error')
            return redirect(url_for('users.change_password'))

        try:
            conn = current_app.get_db_conn()
            cur = conn.cursor()
            cur.execute('SELECT password_hash FROM users WHERE username = %s', (username,))
            row = cur.fetchone()
            if not row:
                flash('User not found', 'error')
                cur.close()
                conn.close()
                return redirect(url_for('chat.chat_page'))
            pw_hash = row[0]
            if not current_app.pwd_context.verify(current, pw_hash):
                flash('Current password is incorrect', 'error')
                cur.close()
                conn.close()
                return redirect(url_for('users.change_password'))
            new_hash = current_app.pwd_context.hash(newpw)
            cur.execute('UPDATE users SET password_hash = %s WHERE username = %s', (new_hash, username))
            conn.commit()
            cur.close()
            conn.close()
            flash('Password changed successfully', 'success')
            return redirect(url_for('chat.chat_page'))
        except Exception as e:
            flash(f'Error changing password: {e}', 'error')
            return redirect(url_for('users.change_password'))

    return render_template('change_password.html')
