from flask import Blueprint, render_template, request, session, url_for, jsonify

lab9 = Blueprint('lab9', __name__)

opened_boxes = [False] * 10

presents = [
    {"text": "С Новым Годом! Пусть этот год принесет море счастья!", "img": "lab9/present_1.avif"},
    {"text": "Желаю крепкого здоровья и неиссякаемой энергии!", "img": "lab9/present_2.avif"},
    {"text": "Пусть удача сопутствует вам во всех начинаниях!", "img": "lab9/present_3.avif"},
    {"text": "Желаю ярких эмоций и незабываемых путешествий!", "img": "lab9/present_4.avif"},
    {"text": "Пусть в вашем доме всегда царит тепло и уют!", "img": "lab9/present_5.avif"},
    {"text": "Желаю профессиональных успехов и новых достижений!", "img": "lab9/present_6.avif"},
    {"text": "Пусть каждый день будет наполнен радостью и смехом!", "img": "lab9/present_7.avif"},
    {"text": "Желаю встретить этот год в кругу самых близких людей!", "img": "lab9/present_8.avif"},
    {"text": "Пусть сбываются даже самые смелые мечты!", "img": "lab9/present_9.avif"},
    {"text": "Желаю благополучия и финансового процветания!", "img": "lab9/present_10.avif"}
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
    if session.get('count', 0) >= 3:
        return jsonify({"error": "Вы уже открыли максимально доступное количество подарков (3)!"}), 400
    if opened_boxes[box_id]:
        return jsonify({"error": "Эту коробку уже кто-то забрал! Попробуйте другую."}), 400
    opened_boxes[box_id] = True
    session['count'] = session.get('count', 0) + 1
    remaining = opened_boxes.count(False)
    return jsonify({
        "present": presents[box_id],
        "remaining": remaining
    })