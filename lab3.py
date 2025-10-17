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
