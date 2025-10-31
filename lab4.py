from flask import Blueprint, url_for, render_template, request, redirect
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
@lab4.route('/lab4/tree', methods = ['GET', 'POST'])
def tree():
    global tree_count
    if request.method == 'GET':
        return render_template('lab4/tree.html', tree count=tree count)
    operation = request. form.get('operation')
    if operation == 'cut':
        tree_count -= 1
    elif operation == 'plant':
        tree_count += 1
    return redirect('/lab4/tree')