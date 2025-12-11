from flask import Blueprint, url_for, render_template, abort, request
from datetime import datetime

lab7 = Blueprint('lab7', __name__)

@lab7.route('/lab7/')
def lab77():
    index_url = url_for('index')
    return render_template('/lab7/lab7.html', index_url=index_url)

films = [
    {
        "title": "Interstellar",
        "title_ru": "Интерстеллар ",
        "year": 2014,
        "description": "Когда засуха, пыльные бури и вымирание растений приводят человечество к продовольственному кризису, \
            коллектив исследователей и учёных отправляется сквозь червоточину (которая предположительно соединяет области \
            пространства-времени через большое расстояние) в путешествие, чтобы превзойти прежние ограничения для космических \
            путешествий человека и найти планету с подходящими для человечества условиями."
    },
    {
        "title": "The Shawshank Redemption",
        "title_ru": "Побег из Шоушенка",
        "year": 1994,
        "description": "Бухгалтер Энди Дюфрейн обвинён в убийстве собственной жены и её любовника. Оказавшись в тюрьме под \
            названием Шоушенк, он сталкивается с жестокостью и беззаконием, царящими по обе стороны решётки. Каждый, кто попадает \
            в эти стены, становится их рабом до конца жизни. Но Энди, обладающий живым умом и доброй душой, находит подход как к \
            заключённым, так и к охранникам, добиваясь их особого к себе расположения."
    },
    {
        "title": "The Green Mile",
        "title_ru": "Зеленая миля",
        "year": 1999,
        "description": "Пол Эджкомб — начальник блока смертников в тюрьме «Холодная гора», каждый из узников которого однажды \
            проходит «зеленую милю» по пути к месту казни. Пол повидал много заключённых и надзирателей за время работы. Однако \
            гигант Джон Коффи, обвинённый в страшном преступлении, стал одним из самых необычных обитателей блока."
    },
    {
        "title": "Gone Girl",
        "title_ru": "Исчезнувшая ",
        "year": 2014,
        "description": "Всё было готово для празднования пятилетия супружеской жизни, когда вдруг необъяснимо пропала виновница \
            торжества. Остались следы борьбы в доме, кровь, которую явно пытались стереть, и цепочка подсказок в игре «охота за \
            сокровищами» - жена ежегодно устраивала её для своего обожаемого мужа. И похоже, что эти подсказки дают шанс \
            пролить свет на судьбу исчезнувшей."
    },
    {
        "title": "Maleficen",
        "title_ru": "Малефисента",
        "year": 2014,
        "description": "Юная волшебница Малефисента вела уединенную жизнь в зачарованном лесу, окруженная сказочными существами, \
            но однажды все изменилось… В её мир вторглись люди, которые принесли с собой разрушение и хаос, и Малефисенте пришлось \
                встать на защиту своих подданных, призвав на помощь могущественные тёмные силы."
    },
]

@lab7.route('/lab7/rest-api/films/', methods=['GET'])
def get_films():
    return films


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['GET'])
def get_film(id):
    films_count = len(films)
    if id >= 0 and id < films_count:
        return films[id]
    else:
        abort(404)


@lab7.route('/lab7/rest-api/films/<int:id>', methods=['DELETE']) 
def del_film(id): 
    films_count = len(films)
    if id >= 0 and id < films_count:
        del films[id]
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
    films_count = len(films)
    if id >= 0 and id < films_count:
        film = request.get_json()
        validation_errors = validate_film(film)
        if validation_errors:
            return validation_errors, 400
        if not film.get('title') and film.get('title_ru'):
            film['title'] = film['title_ru']
        films[id] = film
        return films[id]
    else:
        abort(404)


@lab7.route('/lab7/rest-api/films/', methods=['POST'])
def add_films():
    new_film_data = request.get_json()
    if not new_film_data:
        abort(400) 
    validation_errors = validate_film(new_film_data)
    if validation_errors:
        return validation_errors, 400
    if not new_film_data.get('title') and new_film_data.get('title_ru'):
        new_film_data['title'] = new_film_data['title_ru']
    films.append(new_film_data)
    new_film_id = len(films) - 1
    return {'id': new_film_id}
