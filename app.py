from flask import Flask, url_for, request, redirect
import datetime
app = Flask(__name__)

@app.errorhandler(404)
def not_found(err):
    return "нет такой страницы", 404
@app.route("/")
@app.route("/web")
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

@app.route("/author")
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
@app.route("/image")
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
@app.route("/counter")
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
@app.route("/reset_counter")
def reset_counter():
    global count
    count = 0
    return redirect(url_for('counter'))
@app.route("/info")
def info():
    return redirect("/author")
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