from flask import Blueprint, url_for, render_template, request, session
lab6 = Blueprint('lab6', __name__)

offices = []
for i in range(1, 11):
    offices.append({"number": i, "tenant": "", "price": 1000})

@lab6.route('/lab6/')
def lab66():
    index_url = url_for('index')
    current_login = session.get('login') 
    return render_template('/lab6/lab6.html', index_url=index_url, current_login=current_login)


@lab6.route('/lab6/json-rpc-api/', methods = ['POST'])
def api():
    data = request.json
    id = data['id']
    if data['method'] == 'info':
        return{
            'jsonrpc': '2.0',
            'result': offices,
            'id': id
        }
    
    login = session.get('login')
    if not login:
        return {
            'jsonrpc': '2.0',
            'error': {
                'code': 1,
                'message': 'Unauthorized'
            },            
            'id': id
        }
    if data['method'] == 'booking':
        office_number = data ['params']
        for office in offices:
            if office['number'] == office_number:
                if office ['tenant'] != '':
                    return {
                        'jsonrpc': '2.0',
                        'error': {
                            'code': 2,
                            'message': 'Already booked'
                        },
                        'id': id
                    }
                office['tenant'] = login
                return {
                    'jsonrpc': '2.0',
                    'result': 'success',
                    'id': id
                }

    if data ['method'] == 'cancellation': 
        office_number = data ['params']
        office_to_cancel = None
        for office in offices:
            if office['number'] == office_number:
                office_to_cancel = office
                break

        if not office_to_cancel:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': -32602,
                    'message': 'Office not found (Офис не найден)'
                },
                'id': id
            }
        if office_to_cancel['tenant'] == '':
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 3,
                    'message': 'Not booked (Офис не арендован)'
                },
                'id': id
            }
        if office_to_cancel['tenant'] != login:
            return {
                'jsonrpc': '2.0',
                'error': {
                    'code': 4,
                    'message': 'Not your booking (Это чужая аренда)'
                },
                'id': id
            }
        office_to_cancel['tenant'] = ''
        return {
            'jsonrpc': '2.0',
            'result': 'success',
            'id': id
        }

    return {
        'jsonrpc': '2.0',
        'error': {
            'code': -32601,
            'message': 'Method not found'
        },
        'id': id
    }
