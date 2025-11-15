from flask import Blueprint, url_for, render_template


lab6 = Blueprint('lab6', __name__)


@lab6.route('/lab6/')
def lab66():
    index_url = url_for('index')
    return render_template('/lab6/lab6.html', index_url=index_url)
