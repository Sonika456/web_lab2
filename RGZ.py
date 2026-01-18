from flask import Blueprint, render_template, request, jsonify, session, current_app
from werkzeug.security import check_password_hash, generate_password_hash
import re
import sqlite3
from os import path

RGZ = Blueprint('RGZ', __name__)

def db_connect():
    """Подключение к базе данных в зависимости от типа"""
    if current_app.config.get('DB_TYPE') == 'postgres':
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(
            host='127.0.0.1',
            database='sonia_base',
            user='sonia_base',
            password='+Vkk1'
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
    else:
        # SQLite
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "rgz_database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
    return conn, cur

def db_close(conn, cur):
    """Закрытие соединения с базой данных"""
    conn.commit()
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

        pattern = r"^[a-zA-Z0-9._!@#]+$"
        if not re.match(pattern, login):
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Логин должен содержать только латиницу и цифры"}, "id": id})

        if not password or len(password) < 6:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Пароль слишком короткий"}, "id": id})

        hashed_password = generate_password_hash(password)

        conn, cur = db_connect()

        try:
            execute_query(cur, "SELECT login FROM users WHERE login = %s", (login,))
            if cur.fetchone():
                return jsonify({"jsonrpc": "2.0", "error": {"message": "Такой логин уже занят"}, "id": id})

            execute_query(cur,
                "INSERT INTO users (login, password, name, email, about_me) VALUES (%s, %s, %s, %s, %s)",
                (login, hashed_password, name, email, about_me)
            )
            conn.commit()
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})
        
        except Exception as e:
            conn.rollback()
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
                
                return jsonify({
                    "jsonrpc": "2.0", 
                    "result": {"login": user['login'], "name": user['name']}, 
                    "id": id
                })
            else:
                return jsonify({
                    "jsonrpc": "2.0", 
                    "error": {"message": "Неверный логин или пароль"}, 
                    "id": id
                })
        finally:
            db_close(conn, cur)
    
    if method == 'logout':
        session.clear()
        return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})
    
    if method == 'get_ads':
        conn, cur = db_connect()
        execute_query(cur, '''
            SELECT a.*, u.login as author_login, u.name as author_name, u.email as author_email 
            FROM ads a 
            JOIN users u ON a.user_id = u.id 
            ORDER BY a.created_at DESC
        ''')
        ads = cur.fetchall()
        
        # Преобразуем результат для единообразного доступа
        processed_ads = []
        for ad in ads:
            ad_dict = dict(ad)
            if 'created_at' in ad_dict and ad_dict['created_at']:
                ad_dict['created_at'] = ad_dict['created_at'].strftime('%d.%m.%Y %H:%M')
            if 'user_id' not in session:
                ad_dict['author_email'] = None
            processed_ads.append(ad_dict)
            
        db_close(conn, cur)
        return jsonify({"jsonrpc": "2.0", "result": processed_ads, "id": id})
    
    if method == 'create_ad':
        if 'user_id' not in session:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Вы должны войти в систему"}, "id": id})

        title = params.get('title')
        content = params.get('content')
        user_id = session['user_id']

        if not title or not content:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Заполните все поля"}, "id": id})

        conn, cur = db_connect()
        try:
            execute_query(cur,
                "INSERT INTO ads (user_id, title, content) VALUES (%s, %s, %s)",
                (user_id, title, content)
            )
            conn.commit()
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})
        except Exception as e:
            conn.rollback()
            return jsonify({"jsonrpc": "2.0", "error": {"message": str(e)}, "id": id})
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
            # Переименовываем about_me в bio для фронтенда
            if 'about_me' in user_dict:
                user_dict['bio'] = user_dict.pop('about_me')
                
            return jsonify({"jsonrpc": "2.0", "result": user_dict, "id": id})
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
            execute_query(cur, "DELETE FROM ads WHERE user_id = %s", (user_id,))
            execute_query(cur, "DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            session.clear()
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})
        except Exception as e:
            conn.rollback()
            return jsonify({"jsonrpc": "2.0", "error": {"message": str(e)}, "id": id})
        finally:
            db_close(conn, cur)

    if method == 'get_my_ads':
        if 'user_id' not in session:
            return jsonify({"jsonrpc": "2.0", "result": [], "id": id})
            
        conn, cur = db_connect()
        try:
            execute_query(cur, "SELECT id, title, content, created_at FROM ads WHERE user_id = %s ORDER BY created_at DESC", (session['user_id'],))
            ads = cur.fetchall()
            
            processed_ads = []
            for ad in ads:
                ad_dict = dict(ad)
                if ad_dict.get('created_at'):
                    ad_dict['created_at'] = ad_dict['created_at'].strftime('%d.%m.%Y %H:%M')
                else:
                    ad_dict['created_at'] = ''
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
        user_login = session.get('user_login')

        conn, cur = db_connect()
        
        if user_login == 'admin':
            execute_query(cur, "DELETE FROM ads WHERE id = %s", (ad_id,))
        else:
            execute_query(cur, "DELETE FROM ads WHERE id = %s AND user_id = %s", (ad_id, user_id))
        
        conn.commit()
        db_close(conn, cur)
        return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})

    if method == 'delete_user':
        target_user_id = params.get('user_id')
        current_user_id = session.get('user_id')
        current_user_login = session.get('user_login')

        if not current_user_id:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Нужна авторизация"}, "id": id})

        if current_user_login == 'admin' or str(target_user_id) == str(current_user_id):
            conn, cur = db_connect()
            try:
                execute_query(cur, "DELETE FROM ads WHERE user_id = %s", (target_user_id,))
                execute_query(cur, "DELETE FROM users WHERE id = %s", (target_user_id,))
                conn.commit()
                
                if str(target_user_id) == str(current_user_id):
                    session.clear()
                
                return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})
            except Exception as e:
                conn.rollback()
                return jsonify({"jsonrpc": "2.0", "error": {"message": str(e)}, "id": id})
            finally:
                db_close(conn, cur)
        else:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Нет прав для удаления этого аккаунта"}, "id": id})
        
    if method == 'edit_ad':
        if 'user_id' not in session:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Нужна авторизация"}, "id": id})
        
        ad_id = params.get('id')
        title = params.get('title')
        content = params.get('content')
        user_id = session['user_id']
        user_login = session.get('user_login')

        if not title or not content:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Поля не могут быть пустыми"}, "id": id})

        conn, cur = db_connect()
        
        try:
            if user_login == 'admin':
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

    if method == 'admin_get_users' and is_admin:
        conn, cur = db_connect()
        execute_query(cur, "SELECT id, login, name, email, about_me FROM users ORDER BY id DESC")
        users = cur.fetchall()
        users_list = [dict(user) for user in users]
        db_close(conn, cur)
        return jsonify({"jsonrpc": "2.0", "result": users_list, "id": id})

    if method == 'admin_get_ads' and is_admin:
        conn, cur = db_connect()
        execute_query(cur, """
            SELECT ads.*, users.login 
            FROM ads 
            JOIN users ON ads.user_id = users.id 
            ORDER BY ads.id DESC
        """)
        ads = cur.fetchall()
        ads_list = [dict(ad) for ad in ads]
        db_close(conn, cur)
        return jsonify({"jsonrpc": "2.0", "result": ads_list, "id": id})

    if method == 'admin_edit_user' and is_admin:
        user_id = params.get('user_id')
        name = params.get('name')
        email = params.get('email')
        about_me = params.get('about_me')

        conn, cur = db_connect()
        try:
            execute_query(cur, """
                UPDATE users 
                SET name = %s, email = %s, about_me = %s 
                WHERE id = %s
            """, (name, email, about_me, user_id))
            conn.commit()
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})
        except Exception as e:
            return jsonify({"jsonrpc": "2.0", "error": {"message": str(e)}, "id": id})
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