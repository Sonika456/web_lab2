from flask import Blueprint, url_for, render_template, abort, request, current_app
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from os import path

lab7 = Blueprint('lab7', __name__)

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


@lab7.route('/lab7/')
def lab77():
    index_url = url_for('index')
    return render_template('/lab7/lab7.html', index_url=index_url)


@lab7.route('/lab7/rest-api/films/', methods=['GET'])
def get_films():
    conn, cur = db_connect()
    cur.execute("SELECT id, title, title_ru, year, description FROM films ORDER BY id DESC;")
    films = cur.fetchall()
    db_close(conn, cur)
    return [dict(f) for f in films]


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_film(id):
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("SELECT id, title, title_ru, year, description FROM films WHERE id = %s;", (id,))
    else:
        cur.execute("SELECT id, title, title_ru, year, description FROM films WHERE id = ?;", (id,))
        
    film = cur.fetchone()
    db_close(conn, cur)
    
    if film:
        return dict(film)
    else:
        abort(404)


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE']) 
def del_film(id): 
    conn, cur = db_connect()
    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute("DELETE FROM films WHERE id = %s;", (id,))
    else:
        cur.execute("DELETE FROM films WHERE id = ?;", (id,))
        
    rows_deleted = cur.rowcount
    db_close(conn, cur)
    
    if rows_deleted > 0:
        return '', 204
    else:
        abort(404)


def validate_film(film_data):
    errors = {}
    title_ru = film_data.get('title_ru', '').strip()
    title = film_data.get('title', '').strip()
    year_str = film_data.get('year')
    description = film_data.get('description', '').strip()

    if not title_ru:
        errors['title_ru'] = 'Русское название должно быть заполнено.'
    if not title_ru and not title:
        errors['title'] = 'Должно быть заполнено либо русское, либо оригинальное название.'
    
    MAX_YEAR = datetime.now().year
    MIN_YEAR = 1895
    
    if year_str is not None:
        year_str = str(year_str).strip()
    
    if not year_str:
        errors['year'] = 'Год должен быть указан.'
    elif not year_str.isdigit():
        errors['year'] = 'Год должен быть целым числом.'
    else:
        year = int(year_str)
        if year < MIN_YEAR or year > MAX_YEAR:
            errors['year'] = f'Год должен быть в диапазоне от {MIN_YEAR} до {MAX_YEAR}.'

    if not description:
        errors['description'] = 'Описание не может быть пустым.'
    elif len(description) > 2000:
        errors['description'] = f'Описание не может превышать 2000 символов (сейчас: {len(description)}).'
    return errors if errors else None


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['PUT']) 
def put_film(id):
    film = request.get_json()
    validation_errors = validate_film(film)
    if validation_errors:
        return validation_errors, 400

    conn, cur = db_connect()
    
    if not film.get('title') and film.get('title_ru'):
        film['title'] = film['title_ru']

    data = (
        film['title_ru'].strip(), 
        film['title'].strip(), 
        int(film['year']), 
        film['description'].strip(),
        id 
    )

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute(
            """
            UPDATE films SET 
                title_ru = %s, title = %s, year = %s, description = %s
            WHERE id = %s;
            """, data
        )
    else:
        cur.execute(
            """
            UPDATE films SET 
                title_ru = ?, title = ?, year = ?, description = ?
            WHERE id = ?;
            """, data
        )
    
    rows_updated = cur.rowcount
    db_close(conn, cur)
    
    if rows_updated == 0:
        abort(404)
    film['id'] = id 
    return film


@lab7.route('/lab7/rest-api/films/', methods=['POST'])
def add_films():
    new_film_data = request.get_json()
    if not new_film_data:
        abort(400) 
    validation_errors = validate_film(new_film_data)
    if validation_errors:
        return validation_errors, 400
    conn, cur = db_connect()
    if not new_film_data.get('title') and new_film_data.get('title_ru'):
        new_film_data['title'] = new_film_data['title_ru']
    data = (
        new_film_data['title_ru'].strip(), 
        new_film_data['title'].strip(), 
        int(new_film_data['year']), 
        new_film_data['description'].strip()
    )

    if current_app.config['DB_TYPE'] == 'postgres':
        cur.execute(
            """INSERT INTO films (title_ru, title, year, description) VALUES (%s, %s, %s, %s) RETURNING id;""", data
        )
        new_id = cur.fetchone()['id']
    else:
        cur.execute(
            """INSERT INTO films (title_ru, title, year, description) VALUES (?, ?, ?, ?);""", data
        )
        new_id = cur.lastrowid

    db_close(conn, cur)
    return {'id': new_id}