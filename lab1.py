from flask import Blueprint, url_for, request, redirect
import datetime
lab1 = Blueprint('lab1', __name__)

@lab1.route("/lab1")
def lab():
    web_url = url_for('lab1.web')
    author_url = url_for('lab1.author')
    image_url = url_for('lab1.image')
    counter_url = url_for('lab1.counter')
    reset_url = url_for('lab1.reset_counter')
    info_url = url_for('lab1.info')
    created_url = url_for('lab1.created')
    status_401_url = url_for('lab1.status_401')
    status_402_url = url_for('lab1.status_402')
    status_403_url = url_for('lab1.status_403')
    status_405_url = url_for('lab1.status_405')
    status_418_url = url_for('lab1.status_418')
    error_url = url_for('lab1.cause_error')
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
                .route-list { margin-top: 30px; }
                .route-list h2 { color: #0056b3; }
                .route-list ul { list-style-type: none; padding: 0; }
                .route-list li { margin-bottom: 5px; }
                .route-list a { padding: 5px 10px; border: 1px solid #ccc; border-radius: 5px; display: inline-block; }
                .route-list a:hover { background-color: #e2e6ea; }
            </style>
        </head>
        <body>
            <h1>Основы Flask</h1>
            <p>
                Flask — фреймворк для создания веб-приложений на языке программирования Python, использующий набор инструментов
                Werkzeug, а также шаблонизатор Jinja2. Относится к категории так называемых микрофреймворков — минималистичных 
                каркасов веб-приложений, сознательно предоставляющих лишь самые базовые возможности.
            </p>

            <div class="route-list">
                <h2>Список роутов</h2>
                <ul>
                    <li><a href="''' + web_url + '''">/lab1/web</a></li>
                    <li><a href="''' + author_url + '''">/lab1/author</a></li>
                    <li><a href="''' + image_url + '''">/lab1/image</a></li>
                    <li><a href="''' + counter_url + '''">/lab1/counter</a></li>
                    <li><a href="''' + reset_url + '''">/lab1/reset_counter</a></li>
                    <li><a href="''' + info_url + '''">/lab1/info</a></li>
                    <li><a href="''' + created_url + '''">/lab1/created</a></li>
                    <li><a href="''' + status_401_url + '''">/status/401</a></li>
                    <li><a href="''' + status_402_url + '''">/status/402</a></li>
                    <li><a href="''' + status_403_url + '''">/status/403</a></li>
                    <li><a href="''' + status_405_url + '''">/status/405</a></li>
                    <li><a href="''' + status_418_url + '''">/status/418</a></li>
                    <li><a href="''' + error_url + '''">/error</a></li>
                </ul>
            </div>
        </body>
    </html>
    '''


@lab1.route("/lab1/web")
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


@lab1.route("/lab1/author")
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


@lab1.route("/lab1/image")
def image():
    image_path = url_for("static", filename="oak.jpg")
    css_path = url_for("static", filename="lab1.css")
    headers = {
        'Content-Language': 'ru',
        'X-Generator': 'Flask-lab1',
        'X-Custom-Header': 'This is a custom header value'
    }
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
    ''', 200, headers


count = 0
@lab1.route("/lab1/counter")
def counter():
    global count
    count += 1
    time = datetime.datetime.today()
    url = request.url
    client_ip = request.remote_addr
    reset_url = url_for('reset_counter')
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


@lab1.route("/lab1/reset_counter")
def reset_counter():
    global count
    count = 0
    return redirect(url_for('counter'))


@lab1.route("/lab1/info")
def info():
    return redirect("/lab1/author")


@lab1.route("/lab1/created")
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

@lab1.route("/status/401")
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


@lab1.route("/status/402")
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


@lab1.route("/status/403")
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


@lab1.route("/status/405")
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


@lab1.route("/status/418")
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
   
   
@lab1.route("/error")
def cause_error():
    result = 0 / 1
    return "Этого не может быть"