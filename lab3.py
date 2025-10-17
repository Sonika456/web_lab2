from flask import Blueprint, url_for, render_template, request, make_response, redirect
lab3 = Blueprint('lab3', __name__)


@lab3.route('/lab3/')
def lab33():
    name = request.cookies.get('name', 'Аноним')
    name_color = request.cookies.get('name_color', 'black')
    age = request.cookies.get('age', 'не указан')
    return render_template('/lab3/lab3.html', name=name, name_color=name_color, age=age)


@lab3.route('/lab3/cookie')
def cookie():
    resp = make_response(redirect('/lab3/'))
    resp.set_cookie('name', 'Sonya', max_age=5)
    resp.set_cookie('age', '20')
    resp.set_cookie('name_color', 'magenta')
    return resp


@lab3.route('/lab3/del_cookie')
def del_cookie():
    resp = make_response(redirect('/lab3/'))
    resp.set_cookie('name')
    resp.set_cookie('age')
    resp.set_cookie('name_color')
    return resp


@lab3.route('/lab3/form1')
def form1():
    errors = {}
    user = request.args.get('user')
    if user == '':
        errors['user'] = 'Заполните поле!'
    age = request.args.get('age')
    if age == '':
        errors['age'] = 'Заполните поле!'
    sex = request.args.get('sex')
    return render_template('/lab3/form1.html', user=user, age=age, sex=sex, errors=errors)


menu = {
    'cofee': {'name': 'Кофе', 'price': 120},
    'black-tea': {'name': 'Чёрный чай', 'price': 80},
    'green-tea': {'name': 'Зелёный чай', 'price': 70}
}
additives = {
    'milk': {'name': 'Молоко', 'price': 30},
    'sugar': {'name': 'Сахар', 'price': 10}
}


@lab3.route('/lab3/order')
def order():
    return render_template('/lab3/order.html', menu=menu, additives=additives)


@lab3.route('/lab3/pay')
def pay():
    price = 0
    drink_id = request.args.get('drink')

    drink_data = menu.get(drink_id)
    if drink_data:
        price = drink_data['price']
    else:
        price = 70 

    for additive_id, data in additives.items():
        if request.args.get(additive_id) == 'on':
            price += data['price']
    return render_template('/lab3/pay.html', price=price)


@lab3.route('/lab3/success')
def success():
    total_price = request.args.get('price', 'N/A')
    return render_template('/lab3/success.html', price=total_price)


@lab3.route('/lab3/settings')
def settings():
    color = request.args.get('color')
    background_color = request.args.get('background_color')
    font_size = request.args.get('font_size')
    main_border_style = request.args.get('main_border_style')
    
    if color or background_color or font_size or main_border_style:
        resp = make_response(redirect(url_for('lab3.settings')))
        if color:
            resp.set_cookie('color', color)
        
        if background_color:
            resp.set_cookie('background_color', background_color)
            
        if font_size:
            resp.set_cookie('font_size', font_size)
            
        if main_border_style:
            resp.set_cookie('main_border_style', main_border_style)
        return resp
        
    color = request.cookies.get('color')
    background_color = request.cookies.get('background_color')
    font_size = request.cookies.get('font_size')
    main_border_style = request.cookies.get('main_border_style')
    
    resp = make_response(render_template('lab3/settings.html', color=color, background_color=background_color, 
                                         font_size=font_size, main_border_style=main_border_style))
    return resp


@lab3.route('/lab3/reset_settings')
def reset_settings():  
    resp = make_response(redirect(url_for('lab3.settings')))
    resp.set_cookie('color', '', max_age=0)
    resp.set_cookie('background_color', '', max_age=0)
    resp.set_cookie('font_size', '', max_age=0)
    resp.set_cookie('main_border_style', '', max_age=0)
    return resp


@lab3.route('/lab3/train_ticket')
def train_ticket():
    if not request.args:
        return render_template('/lab3/train_ticket_form.html')
    
    fio = request.args.get('fio', '').strip()
    shelf = request.args.get('shelf')
    age_str = request.args.get('age', '').strip()
    departure = request.args.get('departure', '').strip()
    destination = request.args.get('destination', '').strip()
    date = request.args.get('date', '').strip()
    
    with_linen = request.args.get('with_linen') == 'on'
    with_baggage = request.args.get('with_baggage') == 'on'
    with_insurance = request.args.get('with_insurance') == 'on'
    
    errors = []
    
    if not all([fio, shelf, age_str, departure, destination, date]):
        errors.append("Все поля (ФИО, полка, возраст, пункты, дата) должны быть заполнены.")

    try:
        age = int(age_str)
        if not (1 <= age <= 120):
            errors.append("Возраст должен быть от 1 до 120 лет.")
    except ValueError:
        errors.append("Возраст должен быть целым числом.")
    
    if errors:
        return render_template('/lab3/train_ticket_form.html', errors=errors, fio=fio, shelf=shelf, age=age_str, 
                               departure=departure, destination=destination, date=date,
                               with_linen=with_linen, with_baggage=with_baggage, with_insurance=with_insurance)

    is_child = age < 18
    ticket_type = "Детский билет" if is_child else "Взрослый билет"
    
    total_price = 700 if is_child else 1000
    
    if shelf in ['lower', 'lower_side']:
        total_price += 100
    if with_linen:
        total_price += 75
    if with_baggage:
        total_price += 250
    if with_insurance:
        total_price += 150
    
    ticket_data = {
        'fio': fio,
        'age': age,
        'ticket_type': ticket_type,
        'shelf': shelf,
        'departure': departure,
        'destination': destination,
        'date': date,
        'with_linen': with_linen,
        'with_baggage': with_baggage,
        'with_insurance': with_insurance,
        'total_price': total_price
    }
    return render_template('/lab3/train_ticket.html', **ticket_data)