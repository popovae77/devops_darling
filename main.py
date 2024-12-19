from flask import Flask, request, jsonify
import redis
import uuid

app = Flask(__name__)

redis_client = redis.Redis(host='redis', port=6379, db=0)


@app.route('/health', methods=['GET'])
def health_check():
    return "", 200

@app.route('/clients', methods=['POST'])
def add_client():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')

    if not name or not email:
        return jsonify({'error': 'Name and email are required'}), 400

    client_id = str(uuid.uuid4())
    client_data = {
        'name': name,
        'email': email,
        'phone': phone
    }

    redis_client.hset(f'client:{client_id}', mapping=client_data)

    return jsonify({'id': client_id, 'name': name, 'email': email, 'phone': phone}), 201

@app.route('/clients', methods=['GET'])
def get_clients():
    keys = redis_client.keys('client:*')
    clients = []

    for key in keys:
        client_data = redis_client.hgetall(key)
        clients.append({
            'id': key.decode().split(':')[1],
            'name': client_data[b'name'].decode(),
            'email': client_data[b'email'].decode(),
            'phone': client_data.get(b'phone', b'').decode()
        })

    return jsonify(clients)

@app.route('/clients/<client_id>', methods=['GET'])
def get_client(client_id):
    key = f'client:{client_id}'
    if not redis_client.exists(key):
        return jsonify({'error': 'Client not found'}), 404

    client_data = redis_client.hgetall(key)
    client = {
        'id': client_id,
        'name': client_data[b'name'].decode(),
        'email': client_data[b'email'].decode(),
        'phone': client_data.get(b'phone', b'').decode()
    }

    return jsonify(client)

@app.route('/clients/<client_id>', methods=['PUT'])
def update_client(client_id):
    key = f'client:{client_id}'
    if not redis_client.exists(key):
        return jsonify({'error': 'Client not found'}), 404

    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')

    updated_data = {}
    if name:
        updated_data['name'] = name
    if email:
        updated_data['email'] = email
    if phone:
        updated_data['phone'] = phone

    redis_client.hset(key, mapping=updated_data)
    client_data = redis_client.hgetall(key)

    client = {
        'id': client_id,
        'name': client_data[b'name'].decode(),
        'email': client_data[b'email'].decode(),
        'phone': client_data.get(b'phone', b'').decode()
    }

    return jsonify(client)

@app.route('/clients/<client_id>', methods=['DELETE'])
def delete_client(client_id):
    key = f'client:{client_id}'
    if not redis_client.exists(key):
        return jsonify({'error': 'Client not found'}), 404

    redis_client.delete(key)
    return jsonify({'message': 'Client deleted successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000, debug=True)