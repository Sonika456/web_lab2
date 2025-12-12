import random
from flask import Blueprint, url_for, render_template, request, jsonify, session, redirect

lab9 = Blueprint('lab9', __name__)

GIFT_BOXES = {}

MAX_ALLOWED_OPENS = 3

PRESENTS_DATA = {
    1: {"message": "С Новым годом! Желаем тебе ярких впечатлений и чудесных моментов!", "present_img": "present_1.avif"},
    2: {"message": "Пусть этот год принесет удачу и исполнит самые заветные желания!", "present_img": "present_2.avif"},
    3: {"message": "Поздравляем! Настоящее сокровище — это время, проведенное с близкими!", "present_img": "present_3.avif"},
    4: {"message": "Счастья, здоровья и бесконечной энергии для новых свершений!", "present_img": "present_4.avif"},
    5: {"message": "Пусть каждый день будет наполнен радостью и успехом!", "present_img": "present_5.avif"},
    6: {"message": "Желаем тепла и уюта в доме, а в душе — праздничного настроения!", "present_img": "present_6.avif"},
    7: {"message": "С Рождеством и Новым годом! Пусть сбудутся все мечты!", "present_img": "present_7.avif"},
    8: {"message": "Получи свой заряд позитива на весь год!", "present_img": "present_8.avif"},
    9: {"message": "Желаем вдохновения и креатива в каждом деле!", "present_img": "present_9.avif"},
    10: {"message": "Поздравляем! Открой свое сердце для волшебства!", "present_img": "present_10.avif"},
}

BOX_IMAGE_PATHS = {
    1: "box_closed_1.jpg", 2: "box_closed_2.jpg", 3: "box_closed_3.jpg",
    4: "box_closed_4.jpg", 5: "box_closed_5.jpg", 8: "box_closed_8.jpg",
    9: "box_closed_9.jpg", 6: "box_closed_6.webp", 7: "box_closed_7.webp",
    10: "box_closed_10.webp",
}

NUM_BOXES = 10 

def initialize_boxes():
    if not GIFT_BOXES:
        present_ids = list(PRESENTS_DATA.keys())
        random.shuffle(present_ids) 
        for i in range(1, NUM_BOXES + 1):
            gift_id = present_ids.pop()
            box_image_path = BOX_IMAGE_PATHS[gift_id]
            GIFT_BOXES[i] = {
                "is_open": False,
                "gift_id": gift_id, 
                "image": box_image_path,
                "data": PRESENTS_DATA[gift_id]
            }
initialize_boxes()


@lab9.route('/lab9/')
def lab99():
    if 'opened_count' not in session:
        session['opened_count'] = 0
    closed_count = sum(1 for box in GIFT_BOXES.values() if not box['is_open'])
    index_url = url_for('index')
    return render_template('/lab9/lab9.html', index_url=index_url, boxes=GIFT_BOXES, closed_count=closed_count, max_opens=MAX_ALLOWED_OPENS)

@lab9.route('/lab9/reset_session')
def reset_session():
    session.pop('opened_count', None)
    return redirect(url_for('lab9.lab99'))


@lab9.route('/lab9/api/open_box', methods=['POST'])
def open_box_api():
    try:
        data = request.json
        box_id = int(data.get('box_id'))
    except Exception:
        return jsonify({"success": False, "message": "Неверный формат запроса (box_id не найден)."})

    if box_id not in GIFT_BOXES:
        return jsonify({"success": False, "message": "Коробка с таким ID не существует."})
    box = GIFT_BOXES[box_id]
    if box['is_open']:
        return jsonify({
            "success": False,
            "message": "Эта коробка уже была открыта и пуста. Вы не можете открыть её повторно."
        })
    if 'opened_count' not in session:
        session['opened_count'] = 0
        
    if session['opened_count'] >= MAX_ALLOWED_OPENS:
        return jsonify({
            "success": False, 
            "message": f"Вы уже открыли максимальное количество ({MAX_ALLOWED_OPENS}) коробок! Больше нельзя."
        })
    box['is_open'] = True
    session['opened_count'] += 1
    closed_count = sum(1 for b in GIFT_BOXES.values() if not b['is_open'])
    return jsonify({
        "success": True,
        "message": box['data']['message'],
        "present_img_url": url_for('static', filename=f'lab9/{box["data"]["present_img"]}'),
        "new_closed_count": closed_count,
        "new_opened_count": session['opened_count']
    })