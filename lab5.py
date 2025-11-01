from flask import Blueprint, url_for, render_template
lab5 = Blueprint('lab5', __name__)


@lab5.route('/lab5/')
def lab55():
    index_url = url_for('index')
    return render_template('/lab5/lab5.html', index_url=index_url)


