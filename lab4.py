from flask import Blueprint, url_for, render_template, request
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