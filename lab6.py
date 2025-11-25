from flask import Blueprint, url_for, render_template, request, session, current_app
import psycopg2
from psycopg2.extras import RealDictCursor
import sqlite3
from os import path

lab6 = Blueprint('lab6', __name__)

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


@lab6.route('/lab6/')
def lab66():
    index_url = url_for('index')
    current_login = session.get('login') 
    return render_template('/lab6/lab6.html', index_url=index_url, current_login=current_login)


@lab6.route('/lab6/json-rpc-api/', methods = ['POST'])
def api():
    data = request.json
    id = data['id']
    if data['method'] == 'info':
        conn, cur = db_connect()
        cur.execute("SELECT number, tenant, price FROM offices ORDER BY number;")
        offices_data = cur.fetchall()
        db_close(conn, cur)
        
        offices_list = [dict(office) for office in offices_data]
        
        return{
            'jsonrpc': '2.0',
            'result': offices_list,
            'id': id
        }
    
    login = session.get('login')
    if not login:
        return {
            'jsonrpc': '2.0',
            'error': {
                'code': 1,
                'message': 'Unauthorized (Не авторизован)'
            },
            'id': id
        }
        
    conn, cur = db_connect()

    if data['method'] == 'booking':
        office_number = data ['params']
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT tenant FROM offices WHERE number = %s;", (office_number,))
        else:
            cur.execute("SELECT tenant FROM offices WHERE number = ?;", (office_number,))
            
        office = cur.fetchone()
        
        if not office:
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32602,
                    'message': 'Office not found (Офис не найден)'
                },
                'id': id
            }

        if office['tenant'] != '':
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 2,
                    'message': 'Already booked (Уже арендован)'
                },
                'id': id
            }
            
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("UPDATE offices SET tenant = %s WHERE number = %s;", (login, office_number))
        else:
            cur.execute("UPDATE offices SET tenant = ? WHERE number = ?;", (login, office_number))
            
        db_close(conn, cur)
        
        return {
            'jsonrpc': '2.0',
            'result': 'success',
            'id': id
        }

    if data ['method'] == 'cancellation': 
        office_number = data ['params']
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("SELECT tenant FROM offices WHERE number = %s;", (office_number,))
        else:
            cur.execute("SELECT tenant FROM offices WHERE number = ?;", (office_number,))

        office_to_cancel = cur.fetchone()
        
        if not office_to_cancel:
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32602,
                    'message': 'Office not found (Офис не найден)'
                },
                'id': id
            }
        
        if office_to_cancel['tenant'] == '':
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 3,
                    'message': 'Not booked (Офис не арендован)'
                },
                'id': id
            }
            
        if office_to_cancel['tenant'] != login:
            db_close(conn, cur)
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 4,
                    'message': 'Not your booking (Это чужая аренда)'
                },
                'id': id
            }
            
        if current_app.config['DB_TYPE'] == 'postgres':
            cur.execute("UPDATE offices SET tenant = '' WHERE number = %s;", (office_number,))
        else:
            cur.execute("UPDATE offices SET tenant = '' WHERE number = ?;", (office_number,))
            
        db_close(conn, cur)
        
        return {
            'jsonrpc': '2.0',
            'result': 'success',
            'id': id
        }

    db_close(conn, cur) 
    return {
        'jsonrpc': '2.0',
        'error': {
            'code': -32601,
            'message': 'Method not found'
        },
        'id': id
    }
