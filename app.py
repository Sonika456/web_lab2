from flask import Flask, url_for, request, redirect, abort, render_template
import datetime
from lab1 import lab1

app = Flask(__name__)
app.register_blueprint(lab1)

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
    lab1_url = url_for('lab1.lab')
    lab2_url = url_for('lab2')
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


@app.route('/lab2/a')
def a():
    return 'без слэша'


@app.route('/lab2/a/')
def a2():
    return 'со слэшем'


LAB2_ROUTES = [
    ('a', '/lab2/a', 'Роут без слэша'),
    ('a2', '/lab2/a/', 'Роут со слэшем'),
    ('flowers', '/lab2/flowers/<int:flower_id>', 'Цветок по ID (0-3)'),
    ('add_flower', '/lab2/add_flower/<name>', 'Добавить цветок'),
    ('add_flower_no_name', '/lab2/add_flower/', 'Добавить цветок (ошибка 400)'),
    ('all_flowers', '/lab2/all_flowers', 'Все цветы'),
    ('clear_flowers', '/lab2/clear_flowers', 'Очистить список цветов'),
    ('example', '/lab2/example', 'Пример шаблона Jinja2'),
    ('filters', '/lab2/filters', 'Примеры фильтров Jinja2'),
    ('calc_params', '/lab2/calc/<int:a>/<int:b>', 'Калькулятор (два параметра)'),
    ('calc_default', '/lab2/calc/', 'Калькулятор (редирект на 1/1)'),
    ('calc_one_param', '/lab2/calc/<int:a>', 'Калькулятор (один параметр)'),
    ('book_list_view', '/lab2/books', 'Список книг (таблица)'),
    ('berry_view', '/lab2/berries', 'Список ягод (с картинками)'),
]

flower_list = ['Лилия', 'Тюльпан', 'Ирис', 'Незабудка']

@app.route('/lab2/flowers/<int:flower_id>')
def flowers(flower_id):
    all_flowers_url = url_for('all_flowers')
    if flower_id >= len(flower_list) or flower_id < 0:
        abort(404) 
    else:
        flower_name = flower_list[flower_id]
        return f'''
        <!doctype html>
        <html>
        <body>
            <h1>Цветок №{flower_id}</h1>
            <p>Название: <b>{flower_name}</b></p>
            <hr>
            <p><a href="{all_flowers_url}">Посмотреть все цветы</a></p>
        </body>
        </html>
        '''


@app.route('/lab2/add_flower/<name>')
def add_flower(name):
    flower_list.append(name)
    all_flowers_url = url_for('all_flowers')
    return f'''
    <!doctype html>
    <html>
        <body>
            <h1>Добавлен новый цветок</h1>
            <p>Название нового цветка: {name} </p>
            <p>Всего цветков: {len(flower_list)} </p>
            <p>Полный список: {flower_list} </p>
            <p><a href="{all_flowers_url}">Посмотреть все цветы</a></p>
        </body>
    </html>
'''


@app.route('/lab2/add_flower/')
def add_flower_no_name():
    abort(400)


@app.route('/lab2/all_flowers')
def all_flowers():
    clear_url = url_for('clear_flowers')
    if not flower_list:
        content = "<p>Список цветов пуст.</p>"
    else:
        flowers_html = "".join([f"<li>{i}: <a href=\"{url_for('flowers', flower_id=i)}\">{name}</a></li>" 
                                for i, name in enumerate(flower_list)])
        content = f'''
        <h2>Список цветов (всего: {len(flower_list)})</h2>
        <ul style="list-style-type: none;">
            {flowers_html}
        </ul>
        '''
    return f'''
    <!doctype html>
    <html>
        <body>
            <h1>Все цветы в списке</h1>
            {content}
            <hr>
            <p><a href="{clear_url}" style="color: red;">Очистить список цветов</a></p>
        </body>
    </html>
    '''


@app.route('/lab2/clear_flowers')
def clear_flowers():
    flower_list = []
    all_flowers_url = url_for('all_flowers')
    return f'''
    <!doctype html><html><body>
        <h1>Список цветов полностью очищен!</h1>
        <p>Теперь в списке: {len(flower_list)} цветков.</p>
        <p><a href="{all_flowers_url}">Посмотреть пустой список</a></p>
    </body></html>
    '''


@app.route('/lab2/example')
def example():
    name = 'Черевцова Софья'
    numlab = 2 
    group = 'ФБИ-34' 
    course = '3 курс' 
    fruits = [
        {'name': 'яблоки', 'price': 100},
        {'name': 'груши', 'price': 120},
        {'name': 'апельсины', 'price': 80},
        {'name': 'мандарины', 'price': 95},
        {'name': 'манго', 'price': 321}
    ]
    return render_template('example.html', name=name, numlab=numlab, group=group, course=course, fruits=fruits)


@app.route('/lab2/')
def lab2():
    route_list = [
        (name, address, desc)
        for name, address, desc in LAB2_ROUTES
    ]
    links = []
    links.append( (url_for('flowers', flower_id=0), '/lab2/flowers/0', 'Цветок №0') )
    links.append( (url_for('add_flower', name='Роза'), '/lab2/add_flower/Роза', 'Добавить "Роза"') )
    links.append( (url_for('calc_params', a=5, b=3), '/lab2/calc/5/3', 'Калькулятор 5 и 3') )
    for route_name, route_path, route_desc in LAB2_ROUTES:
        if route_name in ['flowers', 'add_flower', 'calc_params']:
            continue          
        try:
            url = url_for(route_name)
            links.append( (url, route_path, route_desc) )
        except Exception as e:
            links.append( (route_path, route_path, route_desc) )
    return render_template('lab2.html', lab2_links=links)


@app.route('/lab2/filters')
def filters():
    phrase = "О <b>сколько</b> <u>нам</u> <i>открытий</i> чудных..."
    return render_template('filter.html', phrase=phrase)


@app.route('/lab2/calc/<int:a>/<int:b>')
def calc_params(a, b):
    sum_res = a + b
    sub_res = a - b
    mul_res = a * b
    try:
        div_res = a / b
    except ZeroDivisionError:
        div_res = "Ошибка: деление на ноль"
    pow_res = a ** b  
    return f'''
    <!doctype html>
    <html>
    <body>
        <h1>Расчёт с параметрами: {a} и {b}</h1>
        <p>{a} + {b} = {sum_res}</p>
        <p>{a} - {b} = {sub_res}</p>
        <p>{a} &times; {b} = {mul_res}</p>
        <p>{a} / {b} = {div_res}</p>
        <p>{a}<sup>{b}</sup> = {pow_res}</p>
    </body>
    </html>
    '''


@app.route('/lab2/calc/')
def calc_default():
    return redirect(url_for('calc_params', a=1, b=1))


@app.route('/lab2/calc/<int:a>')
def calc_one_param(a):
    return redirect(url_for('calc_params', a=a, b=1))


book_list = [
    {"author": "Джон Толкин", "title": "Властелин колец", "genre": "Фэнтези", "pages": 1178},
    {"author": "Джейн Остин", "title": "Гордость и предубеждение", "genre": "Роман", "pages": 432},
    {"author": "Габриэль Гарсиа Маркес", "title": "Сто лет одиночества", "genre": "Магический реализм", "pages": 417},
    {"author": "Альбер Камю", "title": "Посторонний", "genre": "Философия", "pages": 159},
    {"author": "Уильям Шекспир", "title": "Гамлет", "genre": "Трагедия", "pages": 300},
    {"author": "Гарпер Ли", "title": "Убить пересмешника", "genre": "Художественная литература", "pages": 336},
    {"author": "Владимир Набоков", "title": "Лолита", "genre": "Роман", "pages": 368},
    {"author": "Эрих Мария Ремарк", "title": "Триумфальная арка", "genre": "Военный роман", "pages": 455},
    {"author": "Стивен Кинг", "title": "Сияние", "genre": "Ужасы", "pages": 447},
    {"author": "Роберт Стивенсон", "title": "Остров сокровищ", "genre": "Приключения", "pages": 288},
]

@app.route('/lab2/books')
def book_list_view():
    return render_template('books.html', books=book_list, count=len(book_list))


berry_list = [
    {"name": "Клубника", "description": "Одна из самых популярных садовых ягод, обладает ярким ароматом и сладким вкусом.", "img_url": "strawberry.jpg"},
    {"name": "Малина", "description": "Сладкая и сочная ягода, часто используется в народной медицине, особенно при простуде.", "img_url": "raspberry.jpg"},
    {"name": "Ежевика", "description": "Темная, почти черная ягода с терпким вкусом, богата антиоксидантами.", "img_url": "blackberry.jpg"},
    {"name": "Голубика", "description": "Мелкая синяя ягода, ценится за содержание витаминов и улучшение зрения.", "img_url": "blueberry.jpg"},
    {"name": "Черника", "description": "Темно-синяя ягода, часто пачкает руки и язык. Известна лечебными свойствами.", "img_url": "bilberry.jpg"},
    {"name": "Смородина красная", "description": "Кислая, ярко-красная ягода, идеальна для желе и морсов.", "img_url": "redcurrant.jpg"},
    {"name": "Смородина черная", "description": "Ароматная ягода с высоким содержанием витамина C.", "img_url": "blackcurrant.jpg"},
    {"name": "Крыжовник", "description": "Крупная, зеленая или красная ягода, часто с легким пушком. Используется для варенья.", "img_url": "gooseberry.jpg"},
    {"name": "Вишня", "description": "Сладкая или кисло-сладкая косточковая ягода, популярна в выпечке.", "img_url": "cherry.jpg"},
    {"name": "Черешня", "description": "Более крупная и обычно более сладкая версия вишни, красного или желтого цвета.", "img_url": "sweetcherry.jpg"},
    {"name": "Облепиха", "description": "Ягода оранжевого цвета, очень кислая, богата маслами и витаминами.", "img_url": "seabuckthorn.jpg"},
    {"name": "Клюква", "description": "Красная болотная ягода с очень кислым вкусом, известна как природный антисептик.", "img_url": "cranberry.jpg"},
    {"name": "Брусника", "description": "Красная лесная ягода с горчинкой, хорошо хранится.", "img_url": "lingonberry.jpg"},
    {"name": "Земляника", "description": "Дикая лесная ягода, ароматнее и мельче садовой клубники.", "img_url": "wildstrawberry.jpg"},
    {"name": "Арбуз", "description": "Гигантская ягода с сочной красной мякотью и черными семечками.", "img_url": "watermelon.jpg"},
    {"name": "Дыня", "description": "Крупная, сладкая ягода с волокнистой мякотью и мускусным ароматом.", "img_url": "melon.jpg"},
    {"name": "Кизил", "description": "Красная, овальная, кислая ягода, часто используется для приготовления соусов и настоек.", "img_url": "corneliancherry.jpg"},
    {"name": "Ирга", "description": "Сладкая, сине-черная ягода, похожая на чернику, растет на кустарниках.", "img_url": "shadbush.jpg"},
    {"name": "Калина", "description": "Ярко-красные горькие ягоды, которые собирают после первых морозов.", "img_url": "viburnum.jpg"},
    {"name": "Шелковица (тутовник)", "description": "Длинные, сочные ягоды белого, красного или черного цвета, очень сладкие.", "img_url": "mulberry.jpg"},
]


@app.route('/lab2/berries')
def berry_view():
    global berry_list
    return render_template('berries.html', berries=berry_list, count=len(berry_list))