from flask import Blueprint, render_template, request, jsonify, session, current_app
from werkzeug.security import check_password_hash, generate_password_hash
import re
import sqlite3
from os import path
from datetime import datetime

RGZ = Blueprint('RGZ', __name__)

def db_connect():
    if current_app.config.get('DB_TYPE') == 'postgres':
        import psycopg2
        from psycopg2.extras import RealDictCursor
        conn = psycopg2.connect(host='127.0.0.1', database='sonia_base', user='sonia_base', password='+Vkk1')
        cur = conn.cursor(cursor_factory=RealDictCursor)
    else:
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "rgz_database.db")
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON;") # Важно для работы связей 
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
    return conn, cur

def db_close(conn, cur):
    """Закрытие соединения"""
    cur.close()
    conn.close()

def execute_query(cur, query, params=None):
    """Универсальный метод выполнения запросов"""
    if params is None:
        params = ()
    
    if current_app.config.get('DB_TYPE') == 'postgres':
        cur.execute(query, params)
    else:
        # Заменяем %s на ? для SQLite
        query = query.replace('%s', '?')
        cur.execute(query, params)


def format_date(date_val):
    if not date_val:
        return ''
    if isinstance(date_val, str):
        try:
            # Убираем миллисекунды, если они есть (часто бывает в SQLite/Postgres)
            clean_date = date_val.split('.')[0]
            dt = datetime.strptime(clean_date, '%Y-%m-%d %H:%M:%S')
            return dt.strftime('%d.%m.%Y %H:%M')
        except Exception:
            # Если формат совсем другой, возвращаем как есть, чтобы не упало
            return date_val
    return date_val.strftime('%d.%m.%Y %H:%M')



@RGZ.route('/RGZ/api', methods=['POST'])
def api():
    data = request.json
    method = data.get('method')
    params = data.get('params')
    id = data.get('id')

    if method == 'register':
        login = params.get('login')
        password = params.get('password')
        name = params.get('name')
        email = params.get('email')
        about_me = params.get('about_me')

        if not re.match(r"^[a-zA-Z0-9._!@#]+$", login):
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Неверный логин"}, "id": id})
        if not password or len(password) < 6:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Пароль короткий"}, "id": id})

        hashed_password = generate_password_hash(password)
        conn, cur = db_connect()
        try:
            execute_query(cur, "SELECT login FROM users WHERE login = %s", (login,))
            if cur.fetchone():
                return jsonify({"jsonrpc": "2.0", "error": {"message": "Логин занят"}, "id": id})

            execute_query(cur,
                "INSERT INTO users (login, password, name, email, about_me) VALUES (%s, %s, %s, %s, %s)",
                (login, hashed_password, name, email, about_me)
            )
            conn.commit()
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})
        except Exception as e:
            return jsonify({"jsonrpc": "2.0", "error": {"message": str(e)}, "id": id})
        finally:
            db_close(conn, cur)

    if method == 'login':
        login = params.get('login')
        password = params.get('password')
        conn, cur = db_connect()
        try:
            execute_query(cur, "SELECT * FROM users WHERE login = %s", (login,))
            user = cur.fetchone()
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['user_login'] = user['login']
                session['user_name'] = user['name']
                return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Ошибка входа"}, "id": id})
        finally:
            db_close(conn, cur)
    
    if method == 'get_ads':
        conn, cur = db_connect()
        try:
            # Используем LEFT JOIN, чтобы объявления не пропадали при ошибках связей
            execute_query(cur, '''
                SELECT a.*, u.login as author_login, u.name as author_name, u.email as author_email 
                FROM ads a 
                LEFT JOIN users u ON a.user_id = u.id 
                ORDER BY a.created_at DESC
            ''')
            ads = cur.fetchall()
            
            processed_ads = []
            for ad in ads:
                ad_dict = dict(ad)
                ad_dict['created_at'] = format_date(ad_dict.get('created_at'))
                if 'user_id' not in session:
                    ad_dict['author_email'] = None
                processed_ads.append(ad_dict)
            
            return jsonify({"jsonrpc": "2.0", "result": processed_ads, "id": id})
        finally:
            db_close(conn, cur)
    
    if method == 'create_ad':
        if 'user_id' not in session:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Нужен вход"}, "id": id})
        conn, cur = db_connect()
        try:
            execute_query(cur, "INSERT INTO ads (user_id, title, content) VALUES (%s, %s, %s)",
                        (session['user_id'], params.get('title'), params.get('content')))
            conn.commit()
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})
        finally:
            db_close(conn, cur)

    if method == 'get_user_info':
        if 'user_id' not in session:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Не авторизован"}, "id": id})
        
        conn, cur = db_connect()
        try:
            execute_query(cur, "SELECT login, name, email, about_me FROM users WHERE id = %s", (session['user_id'],))
            user = cur.fetchone()
            if not user:
                return jsonify({"jsonrpc": "2.0", "error": {"message": "Пользователь не найден"}, "id": id})
            
            user_dict = dict(user)
            # Фронтенд ожидает 'bio' вместо 'about_me'
            user_dict['bio'] = user_dict.pop('about_me') or ""
            return jsonify({"jsonrpc": "2.0", "result": user_dict, "id": id})
        finally:
            db_close(conn, cur)

    if method == 'update_profile':
        if 'user_id' not in session:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Не авторизован"}, "id": id})
        
        # Получаем данные из params
        name = params.get('name')
        email = params.get('email')
        about_me = params.get('about_me') # JavaScript пришлет это имя

        conn, cur = db_connect()
        try:
            # Используем %s или ?, в зависимости от вашей execute_query
            execute_query(cur, "UPDATE users SET name = %s, email = %s, about_me = %s WHERE id = %s", 
                          (name, email, about_me, session['user_id']))
            conn.commit() # БЕЗ ЭТОГО НЕ СОХРАНИТСЯ
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})
        except Exception as e:
            return jsonify({"jsonrpc": "2.0", "error": {"message": str(e)}, "id": id})
        finally:
            db_close(conn, cur)

    if method == 'delete_account':
        if 'user_id' not in session:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Ошибка доступа"}, "id": id})
        
        user_id = session['user_id']
        conn, cur = db_connect()
        try:
            # Сначала удаляем объявления пользователя (каскад)
            execute_query(cur, "DELETE FROM ads WHERE user_id = %s", (user_id,))
            # Затем самого пользователя
            execute_query(cur, "DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            session.clear() # Выходим из системы
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})
        except Exception as e:
            return jsonify({"jsonrpc": "2.0", "error": {"message": str(e)}, "id": id})
        finally:
            db_close(conn, cur)

    if method == 'get_my_ads':
        if 'user_id' not in session:
            return jsonify({"jsonrpc": "2.0", "result": [], "id": id})
            
        conn, cur = db_connect()
        try:
            # Принудительно приводим к числу, так как SQLite чувствителен к типам 
            u_id = int(session['user_id']) 
            execute_query(cur, "SELECT id, title, content, created_at FROM ads WHERE user_id = %s ORDER BY created_at DESC", (u_id,))
            ads = cur.fetchall()
            
            processed_ads = []
            for ad in ads:
                ad_dict = dict(ad)
                ad_dict['created_at'] = format_date(ad_dict.get('created_at'))
                processed_ads.append(ad_dict)
                    
            return jsonify({"jsonrpc": "2.0", "result": processed_ads, "id": id})
        except Exception as e:
            return jsonify({"jsonrpc": "2.0", "error": {"message": str(e)}, "id": id})
        finally:
            db_close(conn, cur)
    
    if method == 'delete_ad':
        if 'user_id' not in session:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Нужна авторизация"}, "id": id})
        
        ad_id = params.get('id')
        user_id = session['user_id']
        is_admin = session.get('user_login') == 'admin'

        conn, cur = db_connect()
        try:
            if is_admin:
                # Админ удаляет любое
                execute_query(cur, "DELETE FROM ads WHERE id = %s", (ad_id,))
            else:
                # Юзер только своё
                execute_query(cur, "DELETE FROM ads WHERE id = %s AND user_id = %s", (ad_id, user_id))
            conn.commit()
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})
        finally:
            db_close(conn, cur)

    if method == 'delete_user':
        target_user_id = params.get('user_id')
        current_user_login = session.get('user_login')

        if current_user_login != 'admin':
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Только для администратора"}, "id": id})

        conn, cur = db_connect()
        try:
            # Удаляем все связанные данные
            execute_query(cur, "DELETE FROM ads WHERE user_id = %s", (target_user_id,))
            execute_query(cur, "DELETE FROM users WHERE id = %s", (target_user_id,))
            conn.commit()
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})
        except Exception as e:
            return jsonify({"jsonrpc": "2.0", "error": {"message": str(e)}, "id": id})
        finally:
            db_close(conn, cur)
        
    if method == 'edit_ad':
        if 'user_id' not in session:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Нужна авторизация"}, "id": id})
        
        ad_id = params.get('id')
        title = params.get('title')
        content = params.get('content')
        user_id = session['user_id']
        is_admin = session.get('user_login') == 'admin'

        if not title or not content:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Поля не могут быть пустыми"}, "id": id})

        conn, cur = db_connect()
        try:
            if is_admin:
                execute_query(cur, "UPDATE ads SET title = %s, content = %s WHERE id = %s", (title, content, ad_id))
            else:
                execute_query(cur, "UPDATE ads SET title = %s, content = %s WHERE id = %s AND user_id = %s", 
                            (title, content, ad_id, user_id))
            conn.commit()
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})
        except Exception as e:
            return jsonify({"jsonrpc": "2.0", "error": {"message": str(e)}, "id": id})
        finally:
            db_close(conn, cur)

    is_admin = session.get('user_login') == 'admin'

    if method == 'admin_get_users' and session.get('user_login') == 'admin':
        conn, cur = db_connect()
        try:
            execute_query(cur, "SELECT id, login, name, email, about_me FROM users ORDER BY id DESC")
            users = cur.fetchall()
            return jsonify({"jsonrpc": "2.0", "result": [dict(u) for u in users], "id": id})
        finally:
            db_close(conn, cur)

    if method == 'admin_get_ads':
        conn, cur = db_connect()
        try:
            # Используем JOIN, чтобы достать логин автора из таблицы users
            execute_query(cur, '''
                SELECT a.id, a.title, a.content, u.login 
                FROM ads a 
                JOIN users u ON a.user_id = u.id 
                ORDER BY a.created_at DESC
            ''')
            ads = cur.fetchall()
            
            # Превращаем в список словарей для JSON
            processed_ads = [dict(ad) for ad in ads]
            return jsonify({"jsonrpc": "2.0", "result": processed_ads, "id": id})
        except Exception as e:
            return jsonify({"jsonrpc": "2.0", "error": {"message": str(e)}, "id": id})
        finally:
            db_close(conn, cur)

    if method == 'admin_edit_user' and session.get('user_login') == 'admin':
        conn, cur = db_connect()
        try:
            execute_query(cur, """
                UPDATE users SET name = %s, email = %s, about_me = %s WHERE id = %s
            """, (params.get('name'), params.get('email'), params.get('about_me'), params.get('user_id')))
            conn.commit()
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})
        finally:
            db_close(conn, cur)

    return jsonify({"jsonrpc": "2.0", "error": {"message": "Unknown method"}, "id": id})


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