from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

users = {}
messages = []
public_notes = []

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name', 'Alex Cool')
    code = f"#SCHOOL-{random.randint(1000, 9999)}"
    while code in users:
        code = f"#SCHOOL-{random.randint(1000, 9999)}"
    users[code] = {"name": name, "bio": "School Ninja 🥷", "friends": []}
    return jsonify({"code": code, "user": users[code]})

@app.route('/api/user/<code>', methods=['GET'])
def get_user(code):
    if code in users:
        return jsonify({"exists": True, "user": users[code]})
    return jsonify({"exists": False}), 404

@app.route('/api/regenerate-code', methods=['POST'])
def regenerate_code():
    data = request.json
    old_code = data.get('code')
    if old_code not in users:
        return jsonify({"error": "User not found"}), 404
    new_code = f"#SCHOOL-{random.randint(1000, 9999)}"
    while new_code in users:
        new_code = f"#SCHOOL-{random.randint(1000, 9999)}"
    users[new_code] = users.pop(old_code)
    for friend_code in users[new_code]['friends']:
        if friend_code in users:
            friend_list = users[friend_code]['friends']
            if old_code in friend_list:
                friend_list[friend_list.index(old_code)] = new_code
    for msg in messages:
        if msg['sender'] == old_code:
            msg['sender'] = new_code
        if msg['receiver'] == old_code:
            msg['receiver'] = new_code
    return jsonify({"success": True, "new_code": new_code, "user": users[new_code]})

@app.route('/api/profile', methods=['POST'])
def update_profile():
    data = request.json
    code = data.get('code')
    if code in users:
        users[code]['name'] = data.get('name', users[code]['name'])
        users[code]['bio'] = data.get('bio', users[code]['bio'])
        return jsonify({"success": True, "user": users[code]})
    return jsonify({"error": "User not found"}), 404

@app.route('/api/add-friend', methods=['POST'])
def add_friend():
    data = request.json
    my_code = data.get('my_code')
    friend_code = data.get('friend_code')
    if my_code not in users:
        return jsonify({"success": False, "error": "Your session expired. Please refresh the page to get a new code."}), 400
    if friend_code not in users:
        return jsonify({"success": False, "error": "Invalid friend code. Make sure you typed it correctly."}), 400
    if my_code == friend_code:
        return jsonify({"success": False, "error": "You cannot add yourself!"}), 400
    if friend_code not in users[my_code]['friends']:
        users[my_code]['friends'].append(friend_code)
    if my_code not in users[friend_code]['friends']:
        users[friend_code]['friends'].append(my_code)
    return jsonify({"success": True, "friend_name": users[friend_code]['name'], "friend_code": friend_code})

@app.route('/api/remove-friend', methods=['POST'])
def remove_friend():
    data = request.json
    my_code = data.get('my_code')
    friend_code = data.get('friend_code')
    if my_code not in users:
        return jsonify({"success": False, "error": "Your session expired."}), 400
    if friend_code not in users:
        return jsonify({"success": False, "error": "Friend not found."}), 400
    if friend_code in users[my_code]['friends']:
        users[my_code]['friends'].remove(friend_code)
    if my_code in users[friend_code]['friends']:
        users[friend_code]['friends'].remove(my_code)
    return jsonify({"success": True})

@app.route('/api/friends', methods=['POST'])
def get_friends():
    data = request.json
    my_code = data.get('code')
    if my_code not in users:
        return jsonify([])
    friend_list = []
    for f_code in users[my_code]['friends']:
        last_msg = "No messages yet"
        for msg in reversed(messages):
            if (msg['sender'] == my_code and msg['receiver'] == f_code) or (msg['sender'] == f_code and msg['receiver'] == my_code):
                last_msg = msg['text']
                break
        friend_list.append({"code": f_code, "name": users[f_code]['name'], "last_message": last_msg})
    return jsonify(friend_list)

@app.route('/api/send-message', methods=['POST'])
def send_message():
    data = request.json
    sender = data.get('sender')
    receiver = data.get('receiver')
    if sender not in users or receiver not in users:
        return jsonify({"success": False, "error": "Invalid sender or receiver"}), 400
    messages.append({"sender": sender, "receiver": receiver, "text": data.get('text'), "timestamp": data.get('timestamp')})
    return jsonify({"success": True})

@app.route('/api/messages', methods=['POST'])
def get_messages():
    data = request.json
    user1 = data.get('user1')
    user2 = data.get('user2')
    chat_history = [msg for msg in messages if (msg['sender'] == user1 and msg['receiver'] == user2) or (msg['sender'] == user2 and msg['receiver'] == user1)]
    return jsonify(chat_history)

@app.route('/api/notes', methods=['GET', 'POST'])
def handle_notes():
    if request.method == 'POST':
        data = request.json
        public_notes.insert(0, {"author_name": data.get('author_name'), "text": data.get('text'), "timestamp": data.get('timestamp')})
        return jsonify({"success": True})
    return jsonify(public_notes)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)