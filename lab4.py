from flask import Blueprint, url_for, render_template, request, redirect, session
lab4 = Blueprint('lab4', __name__)


@lab4.route('/lab4/')
def lab44():
    index_url = url_for('index')
    return render_template('/lab4/lab4.html', index_url=index_url)

@lab4.route('/lab4/div-form')
def div_form():
    return render_template('lab4/div-form.html')

@lab4.route('/lab4/div', methods = ['POST'])
def div():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    if x1 == '' or x2 == '':
        div_form_url = url_for('lab4.div_form')
        return render_template('lab4/div.html', error='Оба поля должны быть заполнены!', div_form_url=div_form_url)
    x1 = int(x1)
    x2 = int(x2)
    if x2 == 0:
        div_form_url = url_for('lab4.div_form') 
        error = f'Ошибка: на ноль делить нельзя! (Ваш делитель: {x2})'
        return render_template('lab4/div.html', error=error, div_form_url=div_form_url)
    result = x1 / x2
    div_form_url = url_for('lab4.div_form')
    return render_template('lab4/div.html', x1=x1, x2=x2, result=result, div_form_url=div_form_url)


@lab4.route('/lab4/sum-form')
def sum_form():
    return render_template('lab4/sum-form.html')

@lab4.route('/lab4/sum', methods = ['POST'])
def sum_numbers():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    x1 = int(x1) if x1 != '' else 0
    x2 = int(x2) if x2 != '' else 0
    result = x1 + x2
    sum_form_url = url_for('lab4.sum_form')
    return render_template('lab4/sum.html', x1=x1, x2=x2, result=result, sum_form_url=sum_form_url)


@lab4.route('/lab4/mult-form')
def mult_form():
    return render_template('lab4/mult-form.html')

@lab4.route('/lab4/mult', methods = ['POST'])
def mult_numbers():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    x1 = int(x1) if x1 != '' else 1
    x2 = int(x2) if x2 != '' else 1
    result = x1 * x2
    mult_form_url = url_for('lab4.mult_form')
    return render_template('lab4/mult.html', x1=x1, x2=x2, result=result, mult_form_url=mult_form_url)


@lab4.route('/lab4/sub-form')
def sub_form():
    return render_template('lab4/sub-form.html')

@lab4.route('/lab4/sub', methods = ['POST'])
def sub_numbers():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    sub_form_url = url_for('lab4.sub_form')
    if x1 == '' or x2 == '':
        return render_template('lab4/sub.html', error='Ошибка: Оба поля должны быть заполнены для вычитания!', sub_form_url=sub_form_url)
    x1 = int(x1)
    x2 = int(x2)
    result = x1 - x2
    return render_template('lab4/sub.html', x1=x1, x2=x2, result=result, sub_form_url=sub_form_url)


@lab4.route('/lab4/power-form')
def power_form():
    return render_template('lab4/power-form.html')

@lab4.route('/lab4/power', methods = ['POST'])
def power_numbers():
    x1 = request.form.get('x1')
    x2 = request.form.get('x2')
    power_form_url = url_for('lab4.power_form')
    if x1 == '' or x2 == '':
        return render_template('lab4/power.html', error='Ошибка: Оба поля должны быть заполнены для возведения в степень!', power_form_url=power_form_url)
    x1 = int(x1)
    x2 = int(x2)
    if x1 == 0 and x2 == 0:
        return render_template('lab4/power.html', error='Ошибка: выражение 0^0 является неопределенным! Пожалуйста, измените хотя бы одно число.', power_form_url=power_form_url)
    result = x1 ** x2
    return render_template('lab4/power.html', x1=x1, x2=x2, result=result, power_form_url=power_form_url)


tree_count=0
max_tree=10
@lab4.route('/lab4/tree', methods = ['GET', 'POST'])
def tree():
    global tree_count
    if request.method == 'GET':
        return render_template('lab4/tree.html', tree_count=tree_count, max_tree=max_tree)
    operation = request. form.get('operation')
    if operation == 'cut':
        if tree_count > 0:
            tree_count -= 1
    elif operation == 'plant':
        if tree_count < max_tree:
            tree_count += 1
    return redirect('/lab4/tree')


users = [
    {'login': 'alex', 'password': '123', 'name': 'Александр', 'gender': 'male'},
    {'login': 'bob', 'password': '555', 'name': 'Роберт', 'gender': 'male'},
    {'login': 'kate', 'password': '777', 'name': 'Екатерина', 'gender': 'female'},
    {'login': 'john', 'password': '999', 'name': 'Иоанн', 'gender': 'male'},
]
@lab4.route('/lab4/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'GET':
        if 'user_login' in session:
            current_user = next((u for u in users if u['login'] == session['user_login']), None)
            authorized = True
            name = current_user['name'] if current_user else session['user_login']
        else:
            authorized = False 
            name = ''
        register_url = url_for('lab4.register') 
        return render_template('lab4/login.html', authorized=authorized, name=name, register_url=register_url)
    login_input = request.form.get('login') 
    password = request.form.get('password')
    error = None
    if not login_input:
        error = 'Не введён логин'
    elif not password:
        error = 'Не введён пароль'
    if error:
        return render_template('lab4/login.html', error=error, authorized=False, saved_login=login_input)
    for user in users:
        if login_input == user['login'] and password == user['password']:
            session['user_login'] = user['login']
            session['user_name'] = user['name'] 
            return redirect(url_for('lab4.login'))
    error = 'Неверные логин и/или пароль'
    return render_template('lab4/login.html', error=error, authorized=False, saved_login=login_input)


@lab4.route('/lab4/logout', methods = ['POST'])
def logout():
    session.pop('user_login', None)
    session.pop('user_name', None)
    return redirect(url_for('lab4.login'))
    

@lab4.route('/lab4/register', methods = ['GET', 'POST'])
def register():
    register_url = url_for('lab4.register')
    if request.method == 'GET':
        return render_template('lab4/register.html')
    login_input = request.form.get('login') 
    name = request.form.get('name')
    password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')
    if not login_input or not name or not password or not password_confirm:
        error = 'Все поля должны быть заполнены!'
        return render_template('lab4/register.html', error=error, login=login_input, name=name)
    if password != password_confirm:
        error = 'Пароль и подтверждение не совпадают.'
        return render_template('lab4/register.html', error=error, login=login_input, name=name)
    if any(user['login'] == login_input for user in users):
        error = 'Этот логин уже занят.'
        return render_template('lab4/register.html', error=error, login=login_input, name=name)
    new_user = {
        'login': login_input,
        'password': password,
        'name': name,
        'gender': 'unknown' 
    }
    users.append(new_user)
    session['user_login'] = login_input
    session['user_name'] = name
    return redirect(url_for('lab4.login'))


@lab4.route('/lab4/users')
def users_list():
    if 'user_login' not in session:
        return redirect(url_for('lab4.login'))
    delete_url = url_for('lab4.delete_profile')
    edit_url = url_for('lab4.edit_profile')
    current_login = session['user_login']
    users_display = [{'login': u['login'], 'name': u['name']} for u in users]
    return render_template('lab4/users.html', users=users_display, current_login=current_login, delete_url=delete_url, edit_url=edit_url)


@lab4.route('/lab4/edit', methods = ['GET', 'POST'])
def edit_profile():
    if 'user_login' not in session:
        return redirect(url_for('lab4.login')) 
    current_login = session['user_login']
    user_index = next((i for i, u in enumerate(users) if u['login'] == current_login), -1)
    if user_index == -1:
        session.pop('user_login', None)
        session.pop('user_name', None)
        return redirect(url_for('lab4.login'))
    current_user = users[user_index]
    if request.method == 'GET':
        return render_template('lab4/edit_profile.html', 
                               login=current_user['login'], 
                               name=current_user['name'])
    new_login = request.form.get('login') 
    new_name = request.form.get('name')
    new_password = request.form.get('password')
    password_confirm = request.form.get('password_confirm')
    error = None
    if not new_login or not new_name:
        error = 'Логин и Имя не могут быть пустыми!'
    if new_password or password_confirm:
        if new_password != password_confirm:
            error = 'Пароль и подтверждение не совпадают.'
    if not error and new_login != current_login and any(u['login'] == new_login for u in users):
        error = 'Этот логин уже занят другим пользователем.'
    if error:
        return render_template('lab4/edit_profile.html', error=error, login=new_login, name=new_name)
    users[user_index]['name'] = new_name
    if new_password and new_password == password_confirm:
        users[user_index]['password'] = new_password
    if new_login != current_login:
        users[user_index]['login'] = new_login
        session['user_login'] = new_login
    session['user_name'] = new_name
    return redirect(url_for('lab4.users_list'))


@lab4.route('/lab4/delete', methods = ['POST'])
def delete_profile():
    if 'user_login' not in session:
        return redirect(url_for('lab4.login'))
    current_login = session['user_login']
    global users 
    users = [u for u in users if u['login'] != current_login]
    session.pop('user_login', None)
    session.pop('user_name', None)
    return redirect(url_for('lab4.login'))


@lab4.route('/lab4/fridge', methods = ['GET', 'POST'])
def fridge():
    fridge_form_url = url_for('lab4.fridge')
    if request.method == 'GET':
        return render_template('lab4/fridge.html', message=None)
    temp_str = request.form.get('temperature')
    message = ''
    snowflakes = ''
    if not temp_str:
        message = 'Ошибка: не задана температура'
        return render_template('lab4/fridge.html', message=message, saved_temp=temp_str) 
    try:
        temp = float(temp_str)
    except ValueError:
        message = 'Ошибка: введено некорректное значение температуры'
        return render_template('lab4/fridge.html', message=message, saved_temp=temp_str)
    if temp < -12:
        message = f'Не удалось установить температуру — слишком низкое значение ({temp}°С)'
    elif temp > -1:
        message = f'Не удалось установить температуру — слишком высокое значение ({temp}°С)'
    elif -12 <= temp <= -9:
        message = f'Установлена температура: {temp}°С'
        snowflakes = '❄️❄️❄️'
    elif -8 <= temp <= -5:
        message = f'Установлена температура: {temp}°С'
        snowflakes = '❄️❄️'
    elif -4 <= temp <= -1:
        message = f'Установлена температура: {temp}°С'
        snowflakes = '❄️'
    return render_template('lab4/fridge.html', message=message, snowflakes=snowflakes, saved_temp=temp_str, is_success=True if snowflakes else False)