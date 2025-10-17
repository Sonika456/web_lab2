from flask import Flask, url_for, request, redirect, abort, render_template
import datetime
from lab1 import lab1
from lab2 import lab2

app = Flask(__name__)
app.register_blueprint(lab1)
app.register_blueprint(lab2)

log_entries = []
@app.errorhandler(404)
def not_found(err):
    path = url_for("static", filename="6fcd6199-8445-459b-8d3e-2857d3762fdf.jpg")
    ip_address = request.remote_addr
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    requested_url = request.url
    log_string = f"[{timestamp}] пользователь {ip_address} зашёл на адрес: <u>{requested_url}</u>"
    log_entries.append(log_string)

    log_html_list = ""
    for entry in log_entries:
        log_html_list += f"<li>{entry}</li>"
    return '''
    <!doctype html>
    <html>
        <head>
            <title>НАЙН КАПУТ!</title>
            <style>
                body { 
                    font-family: 'Comic Sans MS', 'Trebuchet MS', sans-serif; 
                    text-align: center; 
                    padding-top: 50px; 
                    background-color: #fce4ec;
                    color: #e91e63;
                    font-size: 1.2em;
                }
                .container {
                    max-width: 600px;
                    margin: auto;
                    background-color: #fff;
                    padding: 20px;
                    border-radius: 15px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                }
                h1 {
                    font-size: 3em;
                    color: #880e4f;
                }
                img {
                    max-width: 100%;
                    height: auto;
                    margin-top: 20px;
                    border: 5px solid #ff79b9;
                    border-radius: 10px;
                }
                a {
                    color: #c51162;
                    text-decoration: none;
                    font-weight: bold;
                    display: block;
                    margin-top: 20px;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>НАЙН КАПУТ!</h1>
                <p>Такая страница не найдена... Что-то пошло не так, а-ля-ля-ля!</p>
                <img src="''' + path + '''">
                <p><strong>Ваш IP-адрес:</strong> ''' + ip_address + '''</p>
                <p><strong>Дата доступа:</strong> ''' + timestamp + '''</p>
                
                <h2>Журнал:</h2>
                <ul>
                    ''' + log_html_list + '''
                </ul>
                <a href="''' + url_for('index') + '''">Вернуться на главную</a>
            </div>
        </body>
    </html>
    ''', 404


@app.errorhandler(500)
def handle_internal_server_error(e):
    return '''
    <!doctype html>
    <html>
      <head>
        <title>Ошибка 500</title>
        <style>
            body { 
                font-family: sans-serif; 
                text-align: center; 
                padding-top: 50px; 
                background-color: #f4f4f4;
                color: #333;
            }
            .error-container {
                max-width: 600px;
                margin: auto;
                background-color: #fff;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #ff4136;
            }
        </style>
      </head>
      <body>
        <div class="error-container">
            <h1>Упс, ошибка!</h1>
            <p>Произошла внутренняя ошибка сервера. Приносим извинения за неудобства. Пожалуйста, попробуйте позже.</p>
        </div>
      </body>
    </html>
    ''', 500


@app.errorhandler(400)
def bad_request(error):
    if request.path.strip('/') == 'lab2/add_flower':
        error_message = "Вы не задали имя цветка"
    else:
        error_message = "Сервер не смог обработать ваш запрос из-за неверного синтаксиса."
    return '''
    <!doctype html>
    <html>
        <head>
            <title>Ошибка 400</title>
            <style>body { font-family: sans-serif; text-align: center; padding-top: 50px; }</style>
        </head>
        <body>
            <h1>Ошибка 400: Некорректный запрос</h1>
            <p>''' + error_message + '''</p>
        </body>
    </html>
    ''', 400


@app.route("/")
@app.route("/index")
def index():
    lab1_url = url_for('lab1.lab11')
    lab2_url = url_for('lab2.lab22')
    return '''
    <!doctype html>
    <html>
        <head>
            <title>НГТУ, ФБ, Лабораторные работы</title>
            <style>
                body { font-family: sans-serif; line-height: 1.6; padding: 20px; margin: 0 px; background-color: #f4f4f4; color: #333; }
                header { text-align: center; border-bottom: 2px solid #0056b3; padding-bottom: 10px; margin-bottom: 20px; }
                h1 { color: #0056b3; }
                ul { list-style-type: none; padding: 0; }
                li { margin-bottom: 10px; }
                a { color: #333; text-decoration: none; font-weight: bold; padding: 8px 12px; border: 1px solid #ccc; border-radius: 5px; display: inline-block; transition: background-color 0.3s; }
                nav a:hover { background-color: #e2e6ea; }
                footer { text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid #ccc; font-size: 0.9em; color: #666; position: fixed; bottom: 0; right: 0; left: 0;}
            </style>
        </head>
        <body>
            <header>
                <h1>НГТУ, ФБ, WEB-программирование, часть 2. Список лабораторных</h1>
            </header>
            <ul>
                <li><a href="''' + lab1_url + '''">Первая лабораторная</a></li>
                <a href="''' + lab2_url + '''">Вторая лабораторная</a>
            </ul>
            <footer>
                <p>Черевцова Софья, ФБИ-34, 3 курс, 2025</p>
            </footer>
        </body>
    </html>
    '''
