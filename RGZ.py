from flask import Blueprint, render_template, request, jsonify, session, redirect
import sqlite3
import os
from werkzeug.security import check_password_hash, generate_password_hash
import re

RGZ = Blueprint('RGZ', __name__)

# --- ПОДКЛЮЧЕНИЕ ---

def db_connect():
    # Путь к файлу database.db в той же директории, что и этот скрипт
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    conn = sqlite3.connect(db_path)
    # Позволяет обращаться к колонкам по именам: row['login']
    conn.row_factory = sqlite3.Row 
    return conn

# --- API МЕТОДЫ (JSON-RPC) ---

@RGZ.route('/RGZ/api', methods=['POST'])
def api():
    data = request.json
    if not data:
        return jsonify({"jsonrpc": "2.0", "error": {"message": "Empty request"}, "id": None})

    method = data.get('method')
    params = data.get('params', {})
    rid = data.get('id')
    user_id = session.get('user_id')

    conn = db_connect()
    cur = conn.cursor()

    try:
        # 1. Регистрация (учитываем NOT NULL поля)
        if method == 'register':
            login = params.get('login')
            password = params.get('password')
            name = params.get('name') or login # Если имя не ввели, берем логин
            email = params.get('email')
            
            if not email or '@' not in email:
                return jsonify({"jsonrpc": "2.0", "error": {"message": "Некорректный email"}, "id": rid})

            hash_pw = generate_password_hash(password)
            cur.execute("""
                INSERT INTO users (login, password, name, email, about_me) 
                VALUES (?, ?, ?, ?, ?)
            """, (login, hash_pw, name, email, params.get('about_me', '')))
            conn.commit()
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": rid})

        # 2. Вход
        elif method == 'login':
            login = params.get('login')
            password = params.get('password')
            user = cur.execute("SELECT * FROM users WHERE login = ?", (login,)).fetchone()
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['user_login'] = user['login']
                return jsonify({"jsonrpc": "2.0", "result": "success", "id": rid})
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Ошибка входа"}, "id": rid})

        # 3. Выход
        elif method == 'logout':
            session.clear()
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": rid})

        # 4. Получение всех объявлений (ГЛАВНАЯ)
        elif method == 'get_ads':
            # Обязательно берем name из таблицы users как author
            rows = cur.execute("""
                SELECT ads.id, ads.title, ads.content, ads.created_at, users.name as author 
                FROM ads 
                JOIN users ON ads.user_id = users.id 
                ORDER BY ads.id DESC
            """).fetchall()
            return jsonify({"jsonrpc": "2.0", "result": [dict(r) for r in rows], "id": rid})

        # 5. Создание объявления
        elif method == 'create_ad':
            if not user_id: 
                return jsonify({"jsonrpc": "2.0", "error": {"message": "Нужна авторизация"}, "id": rid})
            cur.execute("INSERT INTO ads (user_id, title, content) VALUES (?, ?, ?)",
                        (user_id, params.get('title'), params.get('content')))
            conn.commit()
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": rid})

        # 6. Мои объявления (ПРОФИЛЬ - СПРАВА)
        elif method == 'get_my_ads':
            if not user_id: return jsonify({"jsonrpc": "2.0", "result": [], "id": rid})
            rows = cur.execute("SELECT * FROM ads WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
            return jsonify({"jsonrpc": "2.0", "result": [dict(r) for r in rows], "id": rid})

        # 7. Инфо о пользователе (ПРОФИЛЬ - СЛЕВА)
        elif method == 'get_user_info':
            if not user_id: return jsonify({"jsonrpc": "2.0", "result": None, "id": rid})
            user = cur.execute("SELECT id, login, name, email, about_me FROM users WHERE id = ?", (user_id,)).fetchone()
            return jsonify({"jsonrpc": "2.0", "result": dict(user), "id": rid})

        # 8. Удаление аккаунта
        elif method == 'delete_account':
            if not user_id: return jsonify({"jsonrpc": "2.0", "error": {"message": "Отказ"}, "id": rid})
            cur.execute("DELETE FROM ads WHERE user_id = ?", (user_id,))
            cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            session.clear()
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": rid})

        # 9. Удаление объявления
        elif method == 'delete_ad':
            ad_id = params.get('id')
            # Админ удаляет всё, юзер только своё
            if session.get('user_login') == 'admin':
                cur.execute("DELETE FROM ads WHERE id = ?", (ad_id,))
            else:
                cur.execute("DELETE FROM ads WHERE id = ? AND user_id = ?", (ad_id, user_id))
            conn.commit()
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": rid})

        # 10. Редактирование объявления
        elif method == 'edit_ad':
            cur.execute("UPDATE ads SET title=?, content=? WHERE id=? AND user_id=?",
                        (params.get('title'), params.get('content'), params.get('id'), user_id))
            conn.commit()
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": rid})

        # --- АДМИНСКИЕ МЕТОДЫ ---
        elif method == 'admin_get_users' and session.get('user_login') == 'admin':
            rows = cur.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
            return jsonify({"jsonrpc": "2.0", "result": [dict(r) for r in rows], "id": rid})

        elif method == 'admin_get_ads' and session.get('user_login') == 'admin':
            rows = cur.execute("""
                SELECT ads.*, users.login as author_login FROM ads 
                JOIN users ON ads.user_id = users.id ORDER BY ads.id DESC
            """).fetchall()
            return jsonify({"jsonrpc": "2.0", "result": [dict(r) for r in rows], "id": rid})

        elif method == 'admin_edit_user' and session.get('user_login') == 'admin':
            cur.execute("UPDATE users SET name=?, email=?, about_me=? WHERE id=?",
                        (params.get('name'), params.get('email'), params.get('about_me'), params.get('user_id')))
            conn.commit()
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": rid})

        elif method == 'delete_user' and session.get('user_login') == 'admin':
            t_id = params.get('user_id')
            cur.execute("DELETE FROM ads WHERE user_id = ?", (t_id,))
            cur.execute("DELETE FROM users WHERE id = ?", (t_id,))
            conn.commit()
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": rid})

        # Если ни одно условие не сработало
        else:
            return jsonify({"jsonrpc": "2.0", "error": {"message": f"Метод {method} не найден"}, "id": rid})

    except Exception as e:
        return jsonify({"jsonrpc": "2.0", "error": {"message": str(e)}, "id": rid})
    finally:
        conn.close()

# --- МАРШРУТЫ СТРАНИЦ ---

@RGZ.route('/RGZ/')
def main():
    return render_template('/RGZ/index.html')

@RGZ.route('/RGZ/login')
def login_page():
    return render_template('/RGZ/login.html')

@RGZ.route('/RGZ/reg')
def reg_page():
    return render_template('/RGZ/reg.html')

@RGZ.route('/RGZ/profile')
def profile_page():
    if not session.get('user_id'):
        return redirect('/RGZ/login')
    return render_template('/RGZ/profile.html')

@RGZ.route('/RGZ/admin')
def admin_page():
    if session.get('user_login') != 'admin':
        return "403 Forbidden", 403
    return render_template('/RGZ/admin.html')

@RGZ.route('/RGZ/logout')
def logout_view():
    session.clear()
    return redirect('/RGZ/')