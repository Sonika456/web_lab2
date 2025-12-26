from flask import Blueprint, url_for, render_template, request, redirect, jsonify, session
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import re
from os import path

RGZ = Blueprint('RGZ', __name__)


def db_connect():
    conn = psycopg2.connect(
        host='127.0.0.1',
        database='sonia_base',
        user='sonia_base',
        password='+Vkk1'
    )
    return conn


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
        avatar_url = params.get('avatar')

        pattern = r"^[a-zA-Z0-9._!@#]+$"
        # 1. Валидация (только латиница и цифры для логина)
        if not re.match(pattern, login):
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Логин должен содержать только латиницу и цифры"}, "id": id})

        if not password or len(password) < 6:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Пароль слишком короткий"}, "id": id})

        # 2. Хеширование пароля
        hashed_password = generate_password_hash(password)

        conn = db_connect()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        try:
            # 3. Проверка на уникальность логина
            cur.execute("SELECT login FROM users WHERE login = %s", (login,))
            if cur.fetchone():
                return jsonify({"jsonrpc": "2.0", "error": {"message": "Такой логин уже занят"}, "id": id})

            # 4. Вставка в БД
            cur.execute(
                "INSERT INTO users (login, password, name, email, about_me, avatar) VALUES (%s, %s, %s, %s, %s)",
                (login, hashed_password, name, email, about_me, avatar_url)
            )
            conn.commit()
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})
        
        except Exception as e:
            conn.rollback()
            return jsonify({"jsonrpc": "2.0", "error": {"message": str(e)}, "id": id})
        finally:
            cur.close()
            conn.close()

    
    if method == 'login':
        login = params.get('login')
        password = params.get('password')

        conn = db_connect()
        cur = conn.cursor(cursor_factory=RealDictCursor)

        try:
            # 1. Ищем пользователя по логину
            cur.execute("SELECT * FROM users WHERE login = %s", (login,))
            user = cur.fetchone()

            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['user_login'] = user['login']
                session['user_name'] = user['name']
                session['user_avatar'] = user.get('avatar')
                
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
            cur.close()
            conn.close()
        
    if method == 'logout':
        session.clear() # Очищаем все данные сессии
        return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})
    
    if method == 'get_ads':
        conn = db_connect()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # Соединяем таблицы, чтобы получить логин и имя автора
        cur.execute('''
            SELECT a.*, u.login as author_login, u.name as author_name, u.email as author_email 
            FROM ads a 
            JOIN users u ON a.user_id = u.id 
            ORDER BY a.created_at DESC
        ''')
        ads = cur.fetchall()
        for ad in ads:
            ad['created_at'] = ad['created_at'].strftime('%d.%m.%Y %H:%M')
            # Скрываем email от неавторизованных (согласно заданию)
            if 'user_id' not in session:
                ad['author_email'] = None
                
        cur.close()
        conn.close()
        return jsonify({"jsonrpc": "2.0", "result": ads, "id": id})
            
    if method == 'create_ad':
        # Проверка авторизации
        if 'user_id' not in session:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Вы должны войти в систему"}, "id": id})

        title = params.get('title')
        content = params.get('content')
        user_id = session['user_id']

        # Простейшая валидация
        if not title or not content:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Заполните все поля"}, "id": id})

        conn = db_connect()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO ads (user_id, title, content) VALUES (%s, %s, %s)",
                (user_id, title, content)
            )
            conn.commit()
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})
        except Exception as e:
            conn.rollback()
            return jsonify({"jsonrpc": "2.0", "error": {"message": str(e)}, "id": id})
        finally:
            cur.close()
            conn.close()
        
    # 1. Получение данных текущего пользователя
    if method == 'get_user_info':
        if 'user_id' not in session:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Не авторизован"}, "id": id})
        
        conn = db_connect()
        # Используем RealDictCursor, чтобы данные возвращались как словарь {'name': '...', 'email': '...'}
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Убедитесь, что имена столбцов (login, name, email, bio) совпадают с вашей БД
            cur.execute("SELECT login, name, email, about_me FROM users WHERE id = %s", (session['user_id'],))
            user = cur.fetchone()
            
            if not user:
                user['bio'] = user.pop('about_me')
                return jsonify({"jsonrpc": "2.0", "error": {"message": "Пользователь не найден"}, "id": id})
            
            return jsonify({"jsonrpc": "2.0", "result": user, "id": id})
        except Exception as e:
            return jsonify({"jsonrpc": "2.0", "error": {"message": str(e)}, "id": id})
        finally:
            cur.close()
            conn.close()

    # 2. Удаление аккаунта
    if method == 'delete_account':
        if 'user_id' not in session:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Ошибка доступа"}, "id": id})
        
        user_id = session['user_id']
        conn = db_connect()
        cur = conn.cursor()
        try:
            # Сначала удаляются объявления пользователя (из-за Foreign Key), затем сам пользователь
            cur.execute("DELETE FROM ads WHERE user_id = %s", (user_id,))
            cur.execute("DELETE FROM users WHERE id = %s", (user_id,))
            conn.commit()
            session.clear() # Выход из системы после удаления
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})
        except Exception as e:
            conn.rollback()
            return jsonify({"jsonrpc": "2.0", "error": {"message": str(e)}, "id": id})
        finally:
            cur.close()
            conn.close()

    # 3. Список только моих объявлений
    if method == 'get_my_ads':
        if 'user_id' not in session:
            return jsonify({"jsonrpc": "2.0", "result": [], "id": id})
            
        conn = db_connect()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute("SELECT id, title, content, created_at FROM ads WHERE user_id = %s ORDER BY created_at DESC", (session['user_id'],))
            ads = cur.fetchall()
            
            for ad in ads:
                # Превращаем дату в строку, иначе JSON её не "переварит"
                if ad['created_at']:
                    ad['created_at'] = ad['created_at'].strftime('%d.%m.%Y %H:%M')
                else:
                    ad['created_at'] = ''
                    
            return jsonify({"jsonrpc": "2.0", "result": ads, "id": id})
        except Exception as e:
            return jsonify({"jsonrpc": "2.0", "error": {"message": str(e)}, "id": id})
        finally:
            cur.close()
            conn.close()
    
    # Метод удаления объявления
    if method == 'delete_ad':
        if 'user_id' not in session:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Нужна авторизация"}, "id": id})
        
        ad_id = params.get('id')
        user_id = session['user_id']
        user_login = session.get('user_login') # Получаем логин из сессии

        conn = db_connect()
        cur = conn.cursor()
        
        if user_login == 'admin':
            # Админ может удалить любое объявление
            cur.execute("DELETE FROM ads WHERE id = %s", (ad_id,))
        else:
            # Обычный юзер — только своё
            cur.execute("DELETE FROM ads WHERE id = %s AND user_id = %s", (ad_id, user_id))
        
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})

    # Метод удаления пользователя (для страницы профиля или админки)
    if method == 'delete_user':
        target_user_id = params.get('user_id')
        current_user_id = session.get('user_id')
        current_user_login = session.get('user_login')

        if not current_user_id:
            return jsonify({"jsonrpc": "2.0", "error": {"message": "Нужна авторизация"}, "id": id})

        # Проверка: либо это сам пользователь, либо это admin
        if current_user_login == 'admin' or str(target_user_id) == str(current_user_id):
            conn = db_connect()
            cur = conn.cursor()
            try:
                # Удаляем все объявления пользователя, затем его самого
                cur.execute("DELETE FROM ads WHERE user_id = %s", (target_user_id,))
                cur.execute("DELETE FROM users WHERE id = %s", (target_user_id,))
                conn.commit()
                
                # Если удалил сам себя — чистим сессию
                if str(target_user_id) == str(current_user_id):
                    session.clear()
                
                return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})
            except Exception as e:
                conn.rollback()
                return jsonify({"jsonrpc": "2.0", "error": {"message": str(e)}, "id": id})
            finally:
                cur.close()
                conn.close()
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

        conn = db_connect()
        cur = conn.cursor()
        
        try:
            if user_login == 'admin':
                # Админ может редактировать всё
                cur.execute("UPDATE ads SET title = %s, content = %s WHERE id = %s", (title, content, ad_id))
            else:
                # Пользователь — только своё
                cur.execute("UPDATE ads SET title = %s, content = %s WHERE id = %s AND user_id = %s", 
                            (title, content, ad_id, user_id))
            
            conn.commit()
            return jsonify({"jsonrpc": "2.0", "result": "success", "id": id})
        except Exception as e:
            return jsonify({"jsonrpc": "2.0", "error": {"message": str(e)}, "id": id})
        finally:
            cur.close()
            conn.close()
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