from flask import Blueprint, url_for, render_template, request, session, redirect, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from os import path

lab5 = Blueprint('lab5', __name__)


@lab5.route('/lab5/')
def lab55():
    index_url = url_for('index')
    return render_template('/lab5/lab5.html', index_url=index_url, login=session.get('login'))


def db_connect():
    if current_app.config['DB_TYPE'] == 'postgres':
        conn = psycopg2.connect(
            host = '127.0.0.1',
            database = 'cherevtsova_knowledge_base',
            user = 'cherevtsova_knowledge_base',
            password = '@R1am1584VT%'
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
    else:
        dir_path = path.dirname(path.realpath(__file__))
        db_path = path.join(dir_path, "database.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
    return conn, cur

def db_close(conn, cur):
    conn.commit()
    cur.close()
    conn.close()


@lab5.route('/lab5/register/', methods = ['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('/lab5/register.html') 
    login = request.form.get('login')
    password = request.form.get('password')
    real_name = request.form.get('real_name') 
    if not (login and password and real_name):
        return render_template('/lab5/register.html', error='Заполните все поля')
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT login FROM users WHERE login=%s;", (login,))
    else:
        cur.execute("SELECT login FROM users WHERE login=?;", (login,))
    if cur.fetchone():
        db_close(conn, cur)
        return render_template('/lab5/register.html', error="Такой пользователь уже существует")
    password_hash = generate_password_hash(password)
    data = (login, password_hash, real_name)
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute ("INSERT INTO users (login, password, real_name) VALUES (%s, %s, %s);", data) 
    else: 
        cur.execute ("INSERT INTO users (login, password, real_name) VALUES (?, ?, ?);", data)
    db_close(conn, cur)
    return render_template('lab5/success.html', login=login)


@lab5.route('/lab5/login/', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('/lab5/login.html')
    login = request.form.get('login')
    password = request.form.get('password')
    if not (login or password):
        return render_template('/lab5/login.html', error='Заполните поля')
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT * FROM users WHERE login=%s;", (login,))
    else:
        cur.execute("SELECT * FROM users WHERE login=?;", (login,))
    user = cur.fetchone()
    if not user:
        db_close(conn, cur)
        return render_template('/lab5/login.html', error="Логин и/или пароль неверны")
    if not check_password_hash(user['password'], password):
        db_close(conn, cur)
        return render_template('/lab5/login.html', error="Логин и/или пароль неверны")  
    session['login'] = login
    db_close(conn, cur)
    return render_template('/lab5/success_login.html', login=login)


@lab5.route('/lab5/logout/')
def logout():
    session.pop('login', None)
    return redirect(url_for('lab5.lab55'))


@lab5.route('/lab5/users')
def list_users():
    conn, cur = db_connect()
    cur.execute("SELECT login, real_name FROM users;")
    users = cur.fetchall()
    db_close(conn, cur)
    return render_template('/lab5/users_list.html', users=users)


@lab5.route('/lab5/profile', methods=['GET', 'POST'])
def profile():
    login = session.get('login')
    if not login:
        return redirect(url_for('lab5.login'))
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT real_name FROM users WHERE login=%s;", (login,))
    else:
        cur.execute("SELECT real_name FROM users WHERE login=?;", (login,))
    user = cur.fetchone()
    current_name = user['real_name'] if user and 'real_name' in user else login
    if request.method == 'GET':
        db_close(conn, cur)
        return render_template('/lab5/profile.html', current_name=current_name, login=login)
    new_name = request.form.get('real_name')
    new_password = request.form.get('new_password')
    confirm_password = request.form.get('confirm_password')
    error = None
    success = None
    if new_name and new_name != current_name:
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("UPDATE users SET real_name = %s WHERE login = %s;", (new_name, login))
        else:
            cur.execute("UPDATE users SET real_name = ? WHERE login = ?;", (new_name, login))
        current_name = new_name
        success = 'Имя пользователя успешно обновлено.'
    if new_password or confirm_password:
        if new_password and confirm_password and new_password == confirm_password:
            new_password_hash = generate_password_hash(new_password)
            if current_app.config['DB_TYPE'] == 'postgres':
                cur.execute("UPDATE users SET password = %s WHERE login = %s;", (new_password_hash, login))
            else:
                cur.execute("UPDATE users SET password = ? WHERE login = ?;", (new_password_hash, login))
            success = (success if success else '') + ' Пароль успешно обновлен.'
        else:
            error = (error if error else '') + ' Пароли не совпадают или не заполнены.'
    db_close(conn, cur)
    return render_template('/lab5/profile.html', current_name=current_name, login=login, error=error, success=success)


@lab5.route('/lab5/create', methods = ['GET', 'POST'])
def create():
    login=session.get('login')
    if not login: 
        return redirect(url_for('lab5.login'))
    if request.method == 'GET': 
        return render_template('/lab5/create_article.html', error=None)
    title = request.form.get('title') 
    article_text = request.form.get('article_text')
    is_favorite_form = request.form.get('is_favorite')
    is_public_form = request.form.get('is_public')
    if current_app.config['DB_TYPE'] == 'postgres':
        is_favorite = True if is_favorite_form == 'on' else False
        is_public = True if is_public_form == 'on' else False
    else:
        is_favorite = 1 if is_favorite_form == 'on' else 0
        is_public = 1 if is_public_form == 'on' else 0
    if not title or not article_text:
        return render_template('/lab5/create_article.html', error='Заполните и тему, и текст статьи!')
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute ("SELECT id FROM users WHERE login=%s;", (login, )) 
    else:
        cur.execute ("SELECT id FROM users WHERE login=?;", (login, )) 
    user_id = cur.fetchone() ["id"]
    data = (user_id, title, article_text, is_favorite, is_public)
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("INSERT INTO articles (user_id, title, article_text, is_favorite, is_public) VALUES (%s, %s, %s, %s, %s);", data)
    else:
        cur.execute("INSERT INTO articles (user_id, title, article_text, is_favorite, is_public) VALUES (?, ?, ?, ?, ?);", data)
    db_close(conn, cur)
    return redirect(url_for('lab5.list'))


@lab5.route('/lab5/list')
def list(): 
    login = session.get('login') 
    conn, cur = db_connect()
    if login:
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute ("SELECT id FROM users WHERE login=%s;", (login,))
            user_id = cur.fetchone()["id"]
        else:
            cur.execute ("SELECT id FROM users WHERE login=?;", (login,))
            user_id = cur.fetchone()["id"]
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute ("""
                SELECT 
                    a.id, a.title, a.article_text, a.is_favorite, a.is_public, u.login as author_login
                FROM articles a 
                JOIN users u ON a.user_id = u.id
                WHERE a.user_id = %s OR a.is_public = TRUE
                ORDER BY a.is_favorite DESC, a.id DESC;
            """, (user_id,))
        else:
            cur.execute ("""
                SELECT 
                    a.id, a.title, a.article_text, a.is_favorite, a.is_public, u.login as author_login
                FROM articles a 
                JOIN users u ON a.user_id = u.id
                WHERE a.user_id = ? OR a.is_public = 1
                ORDER BY a.is_favorite DESC, a.id DESC;
            """, (user_id,)) 
    else:
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute ("""
                SELECT 
                    a.id, a.title, a.article_text, a.is_favorite, a.is_public, u.login as author_login
                FROM articles a 
                JOIN users u ON a.user_id = u.id
                WHERE a.is_public = TRUE
                ORDER BY a.id DESC;
            """)
        else:
            cur.execute ("""
                SELECT 
                    a.id, a.title, a.article_text, a.is_favorite, a.is_public, u.login as author_login
                FROM articles a 
                JOIN users u ON a.user_id = u.id
                WHERE a.is_public = 1
                ORDER BY a.id DESC;
            """)
    articles = cur.fetchall()
    db_close(conn, cur)
    return render_template('/lab5/articles.html', articles=articles, login=login)


@lab5.route('/lab5/edit/<int:article_id>', methods=['GET', 'POST'])
def edit(article_id):
    login = session.get('login')
    if not login:
        return redirect(url_for('lab5.login'))
    conn, cur = db_connect()
    if request.method == 'GET':
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute(
                "SELECT a.id, a.title, a.article_text, a.is_favorite, a.is_public FROM articles a JOIN users u ON a.user_id = u.id WHERE a.id = %s AND u.login = %s;",
                (article_id, login))
        else:
            cur.execute(
                "SELECT a.id, a.title, a.article_text, a.is_favorite, a.is_public FROM articles a JOIN users u ON a.user_id = u.id WHERE a.id = ? AND u.login = ?;",
                (article_id, login))
        article = cur.fetchone()
        if not article:
            db_close(conn, cur)
            return redirect(url_for('lab5.list')) 
        db_close(conn, cur)
        return render_template('/lab5/edit_article.html', article=article)
    title = request.form.get('title')
    article_text = request.form.get('article_text')
    is_favorite_form = request.form.get('is_favorite')
    is_public_form = request.form.get('is_public')
    if current_app.config['DB_TYPE'] == 'postgres':
        is_favorite = True if is_favorite_form == 'on' else False
        is_public = True if is_public_form == 'on' else False
    else:
        is_favorite = 1 if is_favorite_form == 'on' else 0
        is_public = 1 if is_public_form == 'on' else 0
    if not title or not article_text:
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT a.id, a.title, a.article_text, a.is_favorite, a.is_public FROM articles a JOIN users u ON a.user_id = u.id WHERE a.id = %s AND u.login = %s;", (article_id, login))
        else:
            cur.execute("SELECT a.id, a.title, a.article_text, a.is_favorite, a.is_public FROM articles a JOIN users u ON a.user_id = u.id WHERE a.id = ? AND u.login = ?;", (article_id, login))
        article_for_error = cur.fetchone()
        db_close(conn, cur)
        return render_template('/lab5/edit_article.html', article=article_for_error, error='Заполните и тему, и текст статьи!')
    data = (title, article_text, is_favorite, is_public, article_id)
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("UPDATE articles SET title = %s, article_text = %s, is_favorite = %s, is_public = %s WHERE id = %s;", data)
    else:
        cur.execute("UPDATE articles SET title = ?, article_text = ?, is_favorite = ?, is_public = ? WHERE id = ?;", data)
    db_close(conn, cur)
    return redirect(url_for('lab5.list'))


@lab5.route('/lab5/delete/<int:article_id>', methods=['POST'])
def delete(article_id):
    login = session.get('login')
    if not login:
        return redirect(url_for('lab5.login'))
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id FROM users WHERE login=%s;", (login,))
    else:
        cur.execute("SELECT id FROM users WHERE login=?;", (login,))
    user_id = cur.fetchone()["id"]
    data = (article_id, user_id)
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("DELETE FROM articles WHERE id = %s AND user_id = %s;", data)
    else:
        cur.execute("DELETE FROM articles WHERE id = ? AND user_id = ?;", data)
    db_close(conn, cur)
    return redirect(url_for('lab5.list'))