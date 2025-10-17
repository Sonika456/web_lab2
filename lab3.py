from flask import Blueprint, url_for, redirect, abort, render_template
lab3 = Blueprint('lab3', __name__)


@lab3.route('/lab3/')
def lab33():
    return render_template('/lab3/lab3.html')