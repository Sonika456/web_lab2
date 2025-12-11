from flask import Blueprint, url_for, render_template, request, session, redirect, current_app

lab8 = Blueprint('lab8', __name__)


@lab8.route('/lab8/')
def lab88():
    index_url = url_for('index')
    return render_template('/lab8/lab8.html', index_url=index_url)