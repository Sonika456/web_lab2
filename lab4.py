from flask import Blueprint, url_for, render_template, request, make_response, redirect
lab4 = Blueprint('lab4', __name__)


@lab4.route('/lab4/')
def lab44():
    index_url = url_for('index')
    return render_template('/lab4/lab4.html', index_url=index_url)