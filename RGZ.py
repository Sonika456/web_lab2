from flask import Blueprint, render_template, request, jsonify, session
import sqlite3
import os
from werkzeug.security import check_password_hash, generate_password_hash
import re

RGZ = Blueprint('RGZ', __name__)

# --- РАБОТА С БАЗОЙ ДАННЫХ SQLite ---

def db_connect():
    db_path = os.path.join(os.path.dirname(__file__), 'database.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row # Позволяет обращаться row['column_name']
    return conn

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---
def is_admin():
    return session.get('user_login') == 'admin'

def get_current_user_id():
    return session.get('user_id')

# --- API МЕТОДЫ (JSON-RPC 2.0) ---

@RGZ.route('/RGZ/api', methods=['POST'])
def api():
    data = request.json
    method = data.get('method')
    params = data.get('params', {})
    rid = data.get('id')
    user_id = get_current_user_id()

    conn = db_connect()
    cur = conn.cursor()

    try:
        # 1. register
        if method == 'register':
            login = params.get('login')
            password = params.get('password')
            name = params.get('name')
            email = params.get('email')
            about_me = params.get('about_me', '')
            if not re.match(r"^[a-zA-Z0-9._!@#]+$", login):
                return jsonify({"jsonrpc":"2.0","error":{"message":"Неверный формат логина"},"id":rid})
            hash_pw = generate_password_hash(password)
            cur.execute("INSERT INTO users (login,password,name,email,about_me) VALUES (?,?,?,?,?)",
                        (login, hash_pw, name, email, about_me))
            conn.commit()
            return jsonify({"jsonrpc":"2.0","result":"success","id":rid})

        # 2. login
        elif method == 'login':
            login = params.get('login')
            password = params.get('password')
            user = cur.execute("SELECT * FROM users WHERE login = ?", (login,)).fetchone()
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['user_login'] = user['login']
                return jsonify({"jsonrpc":"2.0","result":"success","id":rid})
            return jsonify({"jsonrpc":"2.0","error":{"message":"Ошибка входа"},"id":rid})

        # 3. logout (API версия)
        elif method == 'logout':
            session.clear()
            return jsonify({"jsonrpc":"2.0","result":"success","id":rid})

        # 4. get_ads (Все объявления для главной)
        elif method == 'get_ads':
            conn = db_connect()
            cur = conn.cursor()
            # Проверьте, что названия таблиц и полей совпадают с init_db
            rows = cur.execute("""
                SELECT ads.id, ads.title, ads.content, users.login as author 
                FROM ads 
                JOIN users ON ads.user_id = users.id 
                ORDER BY ads.id DESC
            """).fetchall()
            conn.close()
            return jsonify({"jsonrpc": "2.0", "result": [dict(r) for r in rows], "id": rid})

        # 5. create_ad
        elif method == 'create_ad':
            if not user_id: return jsonify({"jsonrpc":"2.0","error":{"message":"Нужна авторизация"},"id":rid})
            cur.execute("INSERT INTO ads (user_id, title, content) VALUES (?,?,?)",
                        (user_id, params.get('title'), params.get('content')))
            conn.commit()
            return jsonify({"jsonrpc":"2.0","result":"success","id":rid})

        # 6. get_user_info
        elif method == 'get_user_info':
            if not user_id: return jsonify({"jsonrpc":"2.0","result":None,"id":rid})
            user = cur.execute("SELECT id, login, name, email, about_me FROM users WHERE id = ?", (user_id,)).fetchone()
            return jsonify({"jsonrpc":"2.0","result":dict(user),"id":rid})

        # 7. delete_account (Сам пользователь)
        elif method == 'delete_account':
            if not user_id: return jsonify({"jsonrpc":"2.0","error":{"message":"Нет доступа"},"id":rid})
            cur.execute("DELETE FROM ads WHERE user_id = ?", (user_id,))
            cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            session.clear()
            return jsonify({"jsonrpc":"2.0","result":"success","id":rid})

        # 8. get_my_ads
        elif method == 'get_my_ads':
            if not user_id: return jsonify({"jsonrpc":"2.0","result":[],"id":rid})
            rows = cur.execute("SELECT * FROM ads WHERE user_id = ? ORDER BY id DESC", (user_id,)).fetchall()
            return jsonify({"jsonrpc":"2.0","result":[dict(r) for r in rows],"id":rid})

        # 9. delete_ad (Автор или Админ)
        elif method == 'delete_ad':
            ad_id = params.get('id')
            ad = cur.execute("SELECT user_id FROM ads WHERE id = ?", (ad_id,)).fetchone()
            if ad and (ad['user_id'] == user_id or is_admin()):
                cur.execute("DELETE FROM ads WHERE id = ?", (ad_id,))
                conn.commit()
                return jsonify({"jsonrpc":"2.0","result":"success","id":rid})
            return jsonify({"jsonrpc":"2.0","error":{"message":"Отказ в доступе"},"id":rid})

        # 10. edit_ad
        elif method == 'edit_ad':
            ad_id = params.get('id')
            ad = cur.execute("SELECT user_id FROM ads WHERE id = ?", (ad_id,)).fetchone()
            if ad and ad['user_id'] == user_id:
                cur.execute("UPDATE ads SET title=?, content=? WHERE id=?", 
                            (params.get('title'), params.get('content'), ad_id))
                conn.commit()
                return jsonify({"jsonrpc":"2.0","result":"success","id":rid})
            return jsonify({"jsonrpc":"2.0","error":{"message":"Отказ"},"id":rid})

        # --- АДМИН МЕТОДЫ ---

        # 11. admin_get_users
        elif method == 'admin_get_users' and is_admin():
            rows = cur.execute("SELECT id, login, name, email, about_me FROM users").fetchall()
            return jsonify({"jsonrpc":"2.0","result":[dict(r) for r in rows],"id":rid})

        # 12. admin_get_ads
        elif method == 'admin_get_ads' and is_admin():
            rows = cur.execute("""
                SELECT ads.*, users.login FROM ads 
                JOIN users ON ads.user_id = users.id""").fetchall()
            return jsonify({"jsonrpc":"2.0","result":[dict(r) for r in rows],"id":rid})

        # 13. admin_edit_user
        elif method == 'admin_edit_user' and is_admin():
            cur.execute("UPDATE users SET name=?, email=?, about_me=? WHERE id=?",
                        (params.get('name'), params.get('email'), params.get('about_me'), params.get('user_id')))
            conn.commit()
            return jsonify({"jsonrpc":"2.0","result":"success","id":rid})

        # 14. delete_user (Админ)
        elif method == 'delete_user' and is_admin():
            target_id = params.get('user_id')
            cur.execute("DELETE FROM ads WHERE user_id = ?", (target_id,))
            cur.execute("DELETE FROM users WHERE id = ?", (target_id,))
            conn.commit()
            return jsonify({"jsonrpc":"2.0","result":"success","id":rid})

    except Exception as e:
        return jsonify({"jsonrpc":"2.0","error":{"message":str(e)},"id":rid})
    finally:
        conn.close()

    return jsonify({"jsonrpc":"2.0","error":{"message":"Метод не найден"},"id":rid})

@RGZ.route('/RGZ/')
def main():
    return render_template('/RGZ/index.html')

@RGZ.route('/RGZ/login')
def login():
    return render_template('/RGZ/login.html')

@RGZ.route('/RGZ/reg')
def reg():
    return render_template('/RGZ/reg.html')

@RGZ.route('/RGZ/create')
def create():
    return render_template('/RGZ/create.html')

@RGZ.route('/RGZ/profile')
def profile():
    return render_template('/RGZ/profile.html')

@RGZ.route('/RGZ/admin')
def admin():
    return render_template('/RGZ/admin.html')

@RGZ.route('/RGZ/logout')
def logout():
    session.clear()
    return render_template('/RGZ/index.html')