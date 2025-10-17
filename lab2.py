from flask import Blueprint, url_for, redirect, abort, render_template
lab2 = Blueprint('lab2', __name__)


@lab2.route('/lab2/a')
def a():
    return 'без слэша'


@lab2.route('/lab2/a/')
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

@lab2.route('/lab2/flowers/<int:flower_id>')
def flowers(flower_id):
    all_flowers_url = url_for('lab2.all_flowers')
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


@lab2.route('/lab2/add_flower/<name>')
def add_flower(name):
    flower_list.append(name)
    all_flowers_url = url_for('lab2.all_flowers')
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


@lab2.route('/lab2/add_flower/')
def add_flower_no_name():
    abort(400)


@lab2.route('/lab2/all_flowers')
def all_flowers():
    clear_url = url_for('lab2.clear_flowers')
    if not flower_list:
        content = "<p>Список цветов пуст.</p>"
    else:
        flowers_html = "".join([f"<li>{i}: <a href=\"{url_for('lab2.flowers', flower_id=i)}\">{name}</a></li>" 
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


@lab2.route('/lab2/clear_flowers')
def clear_flowers():
    global flower_list
    flower_list = []
    all_flowers_url = url_for('lab2.all_flowers')
    return f'''
    <!doctype html><html><body>
        <h1>Список цветов полностью очищен!</h1>
        <p>Теперь в списке: {len(flower_list)} цветков.</p>
        <p><a href="{all_flowers_url}">Посмотреть пустой список</a></p>
    </body></html>
    '''


@lab2.route('/lab2/example')
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


@lab2.route('/lab2/')
def lab22():
    route_list = [
        (name, address, desc)
        for name, address, desc in LAB2_ROUTES
    ]
    links = []
    links.append( (url_for('lab2.flowers', flower_id=0), '/lab2/flowers/0', 'Цветок №0') )
    links.append( (url_for('lab2.add_flower', name='Роза'), '/lab2/add_flower/Роза', 'Добавить "Роза"') )
    links.append( (url_for('lab2.calc_params', a=5, b=3), '/lab2/calc/5/3', 'Калькулятор 5 и 3') )
    for route_name, route_path, route_desc in LAB2_ROUTES:
        if route_name in ['flowers', 'add_flower', 'calc_params']:
            continue          
        try:
            url = url_for('lab2.' + route_name)
            links.append( (url, route_path, route_desc) )
        except Exception as e:
            links.append( (route_path, route_path, route_desc) )
    return render_template('lab2.html', lab2_links=links)


@lab2.route('/lab2/filters')
def filters():
    phrase = "О <b>сколько</b> <u>нам</u> <i>открытий</i> чудных..."
    return render_template('filter.html', phrase=phrase)


@lab2.route('/lab2/calc/<int:a>/<int:b>')
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


@lab2.route('/lab2/calc/')
def calc_default():
    return redirect(url_for('calc_params', a=1, b=1))


@lab2.route('/lab2/calc/<int:a>')
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

@lab2.route('/lab2/books')
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


@lab2.route('/lab2/berries')
def berry_view():
    global berry_list
    return render_template('berries.html', berries=berry_list, count=len(berry_list))