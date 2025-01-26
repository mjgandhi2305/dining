from flask import Flask, request, jsonify, render_template, Response
from datetime import datetime, timedelta
import csv
import json
import os
import cv2
from pyzbar.pyzbar import decode

app = Flask(__name__)

# Load the CSV file into a dictionary
def load_users(csv_file):
    users = {}
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            users[row['username']] = {
                'TeamName': row['TeamName'],
                'Breakfast': 0,
                'Lunch': 0,
                'Dinner': 0,
                'last_scan': None
            }
    return users

users = load_users('users.csv')

# Get the current meal based on the time
def get_current_meal():
    now = datetime.now()
    if now.hour >= 7 and now.hour < 10:
        return 'Breakfast'
    elif now.hour >= 12 and now.hour < 15:
        return 'Lunch'
    elif now.hour >= 19 and now.hour < 22:
        return 'Dinner'
    return None

# Save users data to a new CSV file
def save_users(csv_file, users):
    with open(csv_file, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['username', 'TeamName', 'Breakfast', 'Lunch', 'Dinner', 'last_scan'])
        for username, data in users.items():
            writer.writerow([username, data['TeamName'], data['Breakfast'], data['Lunch'], data['Dinner'], data['last_scan']])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scan', methods=['POST'])
def scan_qr():
    username = request.form['username']
    meal = get_current_meal()
    if meal is None:
        return jsonify({'message': 'Not meal time.'})

    if username in users:
        user = users[username]
        if user['last_scan'] and datetime.now() < user['last_scan'] + timedelta(hours=2):
            return jsonify({'message': 'QR code is deactivated. Please try again later.'})

        user[meal] += 1
        user['last_scan'] = datetime.now()
        save_users('new_users.csv', users)
        return jsonify({'message': f'{meal} counted for {username}. Total {meal}: {user[meal]}'})
    return jsonify({'message': 'User not found.'})

@app.route('/reactivate', methods=['POST'])
def reactivate_qr():
    admin_username = request.form['admin_username']
    target_username = request.form['target_username']
    
    if admin_username != 'admin':  # Replace with actual admin validation
        return jsonify({'message': 'Invalid admin credentials.'})

    if target_username in users:
        user = users[target_username]
        user['last_scan'] = None
        save_users('new_users.csv', users)
        return jsonify({'message': f'Deactivation reset for {target_username}.'})
    return jsonify({'message': 'User not found.'})

def gen_frames():
    cap = cv2.VideoCapture(0)  # Capture video from camera
    while True:
        success, frame = cap.read()
        if not success:
            break
        else:
            for obj in decode(frame):
                data = json.loads(obj.data.decode('utf-8'))
                if 'username' in data:
                    username = data['username']
                    scan_qr_code_handler(username)
                    cv2.putText(frame, f'Scanned: {username}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def scan_qr_code_handler(username):
    meal = get_current_meal()
    if meal is None:
        return jsonify({'message': 'Not meal time.'})

    if username in users:
        user = users[username]
        if user['last_scan'] and datetime.now() < user['last_scan'] + timedelta(hours=2):
            return jsonify({'message': 'QR code is deactivated. Please try again later.'})

        user[meal] += 1
        user['last_scan'] = datetime.now()
        save_users('new_users.csv', users)
        return jsonify({'message': f'{meal} counted for {username}. Total {meal}: {user[meal]}'})
    return jsonify({'message': 'User not found.'})

if __name__ == '__main__':
    app.run(debug=True)
