from flask import Blueprint, url_for, render_template, request, session, redirect, current_app

lab9 = Blueprint('lab9', __name__)


@lab9.route('/lab9/')
def lab99():
    index_url = url_for('index')
    return render_template('/lab9/lab9.html', index_url=index_url)