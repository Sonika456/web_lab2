from flask import Flask, url_for, request, redirect
import datetime
app = Flask(__name__)

@app.errorhandler(404)
def not_found(err):
    path = url_for("static", filename="6fcd6199-8445-459b-8d3e-2857d3762fdf.jpg")
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
                <a href="''' + url_for('index') + '''">Вернуться на главную</a>
            </div>
        </body>
    </html>
    ''', 404
@app.route("/")
@app.route("/index")
def index():
    lab1_url = url_for('lab1')
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
            </ul>
            <footer>
                <p>Черевцова Софья, ФБИ-34, 25 курс, 2025</p>
            </footer>
        </body>
    </html>
    '''

@app.route("/lab1")
def lab1():
    index_url = url_for('index')
    return '''
    <!doctype html>
    <html>
        <head>
            <title>Лабораторная 1</title>
            <style>
                body { font-family: sans-serif; line-height: 1.6; padding: 20px; margin: auto; background-color: #f4f4f4; color: #333; }
                p { font-size: 1.1em; }
                a { color: #0056b3; text-decoration: none; font-weight: bold; }
                a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>Основы Flask</h1>
            <p>
                Flask — фреймворк для создания веб-приложений на языке программирования Python, использующий набор инструментов
                Werkzeug, а также шаблонизатор Jinja2. Относится к категории так называемых микрофреймворков — минималистичных 
                каркасов веб-приложений, сознательно предоставляющих лишь самые базовые возможности.
            </p>
            <a href="''' + index_url + '''">На главную страницу</a>
        </body>
    </html>
    '''
@app.route("/lab1/web")
def web():
    return """<!doctype html>
        <html>
           <body>
               <h1>web-сервер на flask</h1>
               <a href="/author">author</a>
           </body>
        </html>""", 200, {
            'X-Server': 'sample',
            'Content-Type': 'text/plain; charset=utf-8'
        }

@app.route("/lab1/author")
def author():
    name = "Черевцова Софья Константиновна"
    group = "ФБИ-34"
    faculty = "ФБ"

    return """<!doctype html>
        <html>
           <body>
               <p>Студент: """ + name + """</p>
               <p>Группа: """ + group + """</p>
               <p>Факультет: """ + faculty + """</p>
               <a href="/web">web</a>
           </body>
        </html>"""
@app.route("/lab1/image")
def image():
    image_path = url_for("static", filename="oak.jpg")
    css_path = url_for("static", filename="lab1.css")
    return '''
    <!doctype html>
    <html>
      <head>
        <title>Дуб</title>
        <link rel="stylesheet" href="''' + css_path + '''">
      </head>
      <body>
        <div class="container">
          <h1>Дуб</h1>
          <img src="''' + image_path + '''" alt="Дуб">
        </div>
      </body>
    </html>
    '''
count = 0
@app.route("/lab1/counter")
def counter():
    global count
    count += 1
    time = datetime.datetime.today()
    url = request.url
    client_ip = request.remote_addr
    reset_url = url_for('/lab1/reset_counter')
    return '''
    <!doctype html>
    <html>
        <head>
            <title>Счетчик</title>
            <style>
            body { font-family: sans-serif; line-height: 1.6; padding: 20px; }
            .info { border: 1px solid #ccc; padding: 15px; border-radius: 8px; margin-top: 20px; }
            a { color: #007bff; text-decoration: none; }
            a:hover { text-decoration: underline; }
            </style>
        </head>
        <body>
            <h1>Счетчик посещений</h1>
            <p>Сколько раз вы сюда заходили: <b>''' + str(count) + '''</b></p>
            <hr>
            <a href="''' + reset_url + '''">Очистить счетчик</a>

            <div class="info">
            Дата и время: ''' + str(time) + '''<br>
            Запрошенный адрес: ''' + url + '''<br>
            Ваш IP-адрес: ''' + client_ip + '''<br>
            </div>
        </body>
    </html>
    '''
@app.route("/lab1/reset_counter")
def reset_counter():
    global count
    count = 0
    return redirect(url_for('/lab1/counter'))
@app.route("/lab1/info")
def info():
    return redirect("/lab1/author")
@app.route("/lab1/created")
def created():
    return '''
    <!doctype html>
    <html>
        <body>
            <h1>Создано успешно</h1>
            <div><i>что-то создано...</i></div>
        </body>
    </html>
    ''', 201
@app.route("/status/400")
def status_400():
    return '''
    <!doctype html>
    <html>
        <head>
            <title>Ошибка 400</title>
            <style>body { font-family: sans-serif; text-align: center; padding-top: 50px; }</style>
        </head>
        <body>
            <h1>Ошибка 400: Некорректный запрос</h1>
            <p>Сервер не смог обработать ваш запрос из-за неверного синтаксиса.</p>
        </body>
    </html>
    ''', 400

@app.route("/status/401")
def status_401():
    return '''
    <!doctype html>
    <html>
        <head>
            <title>Ошибка 401</title>
            <style>body { font-family: sans-serif; text-align: center; padding-top: 50px; }</style>
        </head>
        <body>
            <h1>Ошибка 401: Не авторизован</h1>
            <p>Для доступа к этой странице требуется аутентификация.</p>
        </body>
    </html>
    ''', 401

@app.route("/status/402")
def status_402():
    return '''
    <!doctype html>
    <html>
      <head>
        <title>Ошибка 402</title>
        <style>body { font-family: sans-serif; text-align: center; padding-top: 50px; }</style>
      </head>
      <body>
        <h1>Ошибка 402: Требуется оплата</h1>
        <p>Этот код зарезервирован для будущего использования.</p>
      </body>
    </html>
    ''', 402

@app.route("/status/403")
def status_403():
    return '''
    <!doctype html>
    <html>
      <head>
        <title>Ошибка 403</title>
        <style>body { font-family: sans-serif; text-align: center; padding-top: 50px; }</style>
      </head>
      <body>
        <h1>Ошибка 403: Доступ запрещен</h1>
        <p>У вас нет прав для просмотра этой страницы.</p>
      </body>
    </html>
    ''', 403

@app.route("/status/405")
def status_405():
    return '''
    <!doctype html>
    <html>
      <head>
        <title>Ошибка 405</title>
        <style>body { font-family: sans-serif; text-align: center; padding-top: 50px; }</style>
      </head>
      <body>
        <h1>Ошибка 405: Метод не поддерживается</h1>
        <p>Использованный метод запроса не поддерживается для данного ресурса.</p>
      </body>
    </html>
    ''', 405

@app.route("/status/418")
def status_418():
    return '''
    <!doctype html>
    <html>
      <head>
        <title>Ошибка 418</title>
        <style>body { font-family: sans-serif; text-align: center; padding-top: 50px; }</style>
      </head>
      <body>
        <h1>Ошибка 418: Я — чайник</h1>
        <p>Сервер отказывается заваривать кофе, потому что он чайник.</p>
      </body>
    </html>
    ''', 418
@app.route("/error")
def cause_error():
    result = 1 / 0
    return "Этого не может быть"
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