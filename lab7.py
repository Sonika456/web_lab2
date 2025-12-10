from flask import Blueprint, url_for, render_template, request, session, redirect, current_app

lab7 = Blueprint('lab7', __name__)

@lab7.route('/lab7/')
def lab77():
    index_url = url_for('index')
    return render_template('/lab5/lab5.html', index_url=index_url, login=session.get('login'))

