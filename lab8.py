from flask import Blueprint, url_for, render_template, request, redirect, abort
from werkzeug.security import generate_password_hash, check_password_hash
from db import db
from db.models import users, articles
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy import or_, func

lab8 = Blueprint('lab8', __name__)


@lab8.route('/lab8/')
def lab88():
    index_url = url_for('index')
    return render_template('/lab8/lab8.html', index_url=index_url, current_user=current_user )


@lab8.route('/lab8/register/', methods = ['GET', 'POST']) 
def register():
    if request.method == 'GET':
        return render_template('lab8/register.html')

    login_form = request.form.get('login')
    password_form = request.form.get('password')

    if not login_form or login_form.strip() == '':
        return render_template('lab8/register.html', error = 'Имя пользователя не может быть пустым!')
    if not password_form:
        return render_template('lab8/register.html', error = 'Пароль не может быть пустым!')

    login_exists = users.query.filter_by(login = login_form).first()
    if login_exists:
        return render_template('lab8/register.html', error = 'Такой пользователь уже существует')
    password_hash = generate_password_hash(password_form)
    new_user = users(login = login_form, password = password_hash)
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user, remember=False)
    return redirect('/lab8/')


@lab8.route('/lab8/login', methods = ['GET', 'POST']) 
def login():
    if request.method == 'GET': 
        return render_template('lab8/login.html')
    login_form = request.form.get('login')
    password_form = request.form.get('password')

    if not login_form or login_form.strip() == '':
        return render_template('/lab8/login.html', error = 'Логин не может быть пустым!')
    if not password_form:
        return render_template('/lab8/login.html', error = 'Пароль не может быть пустым!')
    
    remember_me = request.form.get('remember_me') == 'on'
    user = users.query.filter_by(login = login_form).first()
    if user:
        if check_password_hash(user.password, password_form):
            login_user(user, remember = remember_me) 
            return redirect('/lab8/')
    return render_template('/lab8/login.html', error = 'Ошибка входа: логин и/или пароль неверны')


@lab8.route('/lab8/articles/') 
def article_list(): 
    search_query = request.args.get('q', '').strip()
    author_logins = {u.id: u.login for u in users.query.all()}
    visibility_condition = (articles.is_public == True)
    if current_user.is_authenticated:
        visibility_condition = or_(articles.is_public == True, articles.login_id == current_user.id)

    all_visible_articles = articles.query.filter(visibility_condition).all()

    search_results = None
    if search_query:
        search_pattern = f'%{search_query.lower()}%'
        search_condition = (func.lower(articles.title).like(search_pattern))  
        search_results = articles.query.filter(visibility_condition, search_condition).all()
    return render_template('lab8/articles.html', articles=all_visible_articles, search_results=search_results, search_query=search_query, current_user=current_user, author_logins=author_logins)

@lab8.route('/lab8/create', methods=['GET', 'POST'])
@login_required 
def create_article():
    if request.method == 'GET':
        return render_template('lab8/create_edit.html', article=None)
    
    title_form = request.form.get('title')
    text_form = request.form.get('article_text')
    
    is_favorite_form = request.form.get('is_favorite') == 'on'
    is_public_form = request.form.get('is_public') == 'on'

    if not title_form or title_form.strip() == '':
        return render_template('lab8/create.html', error='Заголовок не может быть пустым!')
        
    if not text_form or text_form.strip() == '':
        return render_template('lab8/create.html', error='Текст статьи не может быть пустым!')

    new_article = articles(
        login_id = current_user.id,
        title = title_form,
        article_text = text_form,
        is_favorite = is_favorite_form,
        is_public = is_public_form,
        likes = 0
    )
    db.session.add(new_article)
    db.session.commit()
    return redirect('/lab8/articles') 


@lab8.route('/lab8/edit/<int:article_id>', methods=['GET', 'POST'])
@login_required 
def edit_article(article_id):
    article = articles.query.get_or_404(article_id)
    
    if article.login_id != current_user.id:
        abort(403) 
    if request.method == 'GET':
        return render_template('lab8/create_edit.html', article=article)

    title_form = request.form.get('title')
    text_form = request.form.get('article_text')
    
    is_favorite_form = request.form.get('is_favorite') == 'on'
    is_public_form = request.form.get('is_public') == 'on'

    if not title_form or title_form.strip() == '':
        return render_template('lab8/create_edit.html', article=article, error='Заголовок не может быть пустым!')
        
    if not text_form or text_form.strip() == '':
        return render_template('lab8/create_edit.html', article=article, error='Текст статьи не может быть пустым!')

    article.title = title_form
    article.article_text = text_form
    article.is_favorite = is_favorite_form
    article.is_public = is_public_form

    db.session.commit()
    return redirect('/lab8/articles')


@lab8.route('/lab8/delete/<int:article_id>', methods=['POST'])
@login_required 
def delete_article(article_id):
    article = articles.query.get_or_404(article_id)
    if article.login_id != current_user.id:
        abort(403) 
    db.session.delete(article)
    db.session.commit()
    return redirect('/lab8/articles')


@lab8.route('/lab8/logout/') 
@login_required 
def logout(): 
    logout_user()
    return redirect('/lab8/')