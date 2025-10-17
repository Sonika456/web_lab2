from flask import Blueprint, url_for, render_template, request, make_response, redirect
lab3 = Blueprint('lab3', __name__)


@lab3.route('/lab3/')
def lab33():
    index_url = url_for('index')
    name = request.cookies.get('name', 'Аноним')
    name_color = request.cookies.get('name_color', 'black')
    age = request.cookies.get('age', 'не указан')
    return render_template('/lab3/lab3.html', name=name, name_color=name_color, age=age, index_url=index_url)


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


smartphones = [
    {'name': 'Galaxy A54', 'price': 32000, 'brand': 'Samsung', 'color': 'White'},
    {'name': 'iPhone 13', 'price': 65000, 'brand': 'Apple', 'color': 'Starlight'},
    {'name': 'Redmi Note 12', 'price': 15000, 'brand': 'Xiaomi', 'color': 'Black'},
    {'name': 'Pixel 7a', 'price': 42000, 'brand': 'Google', 'color': 'Charcoal'},
    {'name': 'Galaxy S23 Ultra', 'price': 110000, 'brand': 'Samsung', 'color': 'Phantom Black'},
    {'name': 'iPhone 15 Pro', 'price': 135000, 'brand': 'Apple', 'color': 'Natural Titanium'},
    {'name': 'Poco X5 Pro', 'price': 25000, 'brand': 'Xiaomi', 'color': 'Blue'},
    {'name': 'Pixel 8', 'price': 68000, 'brand': 'Google', 'color': 'Mint'},
    {'name': 'OnePlus 11', 'price': 55000, 'brand': 'OnePlus', 'color': 'Green'},
    {'name': 'iPhone SE (2022)', 'price': 38000, 'brand': 'Apple', 'color': 'Red'},
    {'name': 'Galaxy Z Fold5', 'price': 180000, 'brand': 'Samsung', 'color': 'Cream'},
    {'name': 'Redmi 12', 'price': 12000, 'brand': 'Xiaomi', 'color': 'Silver'},
    {'name': 'Pixel Fold', 'price': 195000, 'brand': 'Google', 'color': 'Obsidian'},
    {'name': 'Nothing Phone (2)', 'price': 50000, 'brand': 'Nothing', 'color': 'Grey'},
    {'name': 'iPhone 14', 'price': 58000, 'brand': 'Apple', 'color': 'Purple'},
    {'name': 'Galaxy A34', 'price': 28000, 'brand': 'Samsung', 'color': 'Lime'},
    {'name': 'Xiaomi 13T', 'price': 48000, 'brand': 'Xiaomi', 'color': 'Black'},
    {'name': 'Pixel 6a', 'price': 35000, 'brand': 'Google', 'color': 'Sage'},
    {'name': 'Galaxy S21 FE', 'price': 40000, 'brand': 'Samsung', 'color': 'Lavender'},
    {'name': 'iPhone 12', 'price': 45000, 'brand': 'Apple', 'color': 'Blue'}
]


actual_min_price = min(item['price'] for item in smartphones)
actual_max_price = max(item['price'] for item in smartphones)


@lab3.route('/lab3/price_filter')
def price_filter():
    if request.args.get('reset') == '1':
        resp = make_response(redirect(url_for('lab3.price_filter')))
        resp.set_cookie('min_price', '', max_age=0)
        resp.set_cookie('max_price', '', max_age=0)
        return resp
    
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')
    
    if not min_price and not max_price:
        min_price = request.cookies.get('min_price')
        max_price = request.cookies.get('max_price')
    
    current_min = None
    current_max = None
    
    try:
        if min_price:
            current_min = int(min_price)
    except ValueError:
        pass
        
    try:
        if max_price:
            current_max = int(max_price)
    except ValueError:
        pass

    if current_min is not None and current_max is not None and current_min > current_max:
        current_min, current_max = current_max, current_min
    
    if request.args.get('min_price') or request.args.get('max_price'):
        resp = make_response(redirect(url_for('lab3.price_filter')))
        resp.set_cookie('min_price', str(current_min) if current_min is not None else '')
        resp.set_cookie('max_price', str(current_max) if current_max is not None else '')
        return resp
    
    filtered_items = []
    if current_min is None and current_max is None:
        filtered_items = smartphones
    else:
        for item in smartphones:
            price = item['price']
            min_ok = current_min is None or price >= current_min
            max_ok = current_max is None or price <= current_max
            
            if min_ok and max_ok:
                filtered_items.append(item)
    
    template_data = {
        'items': filtered_items,
        'count': len(filtered_items),
        'min_placeholder': actual_min_price,
        'max_placeholder': actual_max_price,
        'min_value': current_min if current_min is not None else '',
        'max_value': current_max if current_max is not None else '',
    }
    return render_template('/lab3/price_filter.html', **template_data)