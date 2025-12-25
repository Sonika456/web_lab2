from flask import Blueprint, render_template, request, session, url_for, jsonify
from flask_login import current_user, login_required

lab9 = Blueprint('lab9', __name__)

opened_boxes = [False] * 10

presents = [
    {"text": "С Новым Годом! (VIP подарок)", "img": "lab9/present_1.avif", "is_vip": True},
    {"text": "Желаю крепкого здоровья!", "img": "lab9/present_2.avif", "is_vip": False},
    {"text": "Пусть удача сопутствует вам!", "img": "lab9/present_3.avif", "is_vip": False},
    {"text": "Желаю ярких эмоций!", "img": "lab9/present_4.avif", "is_vip": False},
    {"text": "Тепла и уюта вашему дому!", "img": "lab9/present_5.avif", "is_vip": False},
    {"text": "Профессиональных успехов! (VIP подарок)", "img": "lab9/present_6.avif", "is_vip": True},
    {"text": "Радости и смеха!", "img": "lab9/present_7.avif", "is_vip": False},
    {"text": "Встретьте год с близкими!", "img": "lab9/present_8.avif", "is_vip": False},
    {"text": "Пусть сбываются мечты!", "img": "lab9/present_9.avif", "is_vip": False},
    {"text": "Благополучия! (VIP подарок)", "img": "lab9/present_10.avif", "is_vip": True}
]

@lab9.route('/lab9/')
def lab99():
    if 'count' not in session:
        session['count'] = 0
    remaining = opened_boxes.count(False)
    return render_template('lab9/lab9.html', remaining=remaining, opened_boxes=opened_boxes)


@lab9.route('/lab9/open_box', methods=['POST'])
def open_box():
    data = request.json
    box_id = data.get('id')
    if presents[box_id]['is_vip'] and not current_user.is_authenticated:
        return jsonify({"error": "Этот подарок только для авторизованных пользователей! Пожалуйста, войдите в систему."}), 403
    if session.get('count', 0) >= 3:
        return jsonify({"error": "Вы уже открыли 3 коробки! Больше нельзя."}), 400
    if opened_boxes[box_id]:
        return jsonify({"error": "Эту коробку уже забрали!"}), 400
    opened_boxes[box_id] = True
    session['count'] = session.get('count', 0) + 1
    return jsonify({
        "present": presents[box_id],
        "remaining": opened_boxes.count(False)
    })


@lab9.route('/lab9/reset', methods=['POST'])
@login_required 
def reset_boxes():
    global opened_boxes
    opened_boxes = [False] * 10 
    session['count'] = 0 
    return jsonify({"success": True, "remaining": 10})