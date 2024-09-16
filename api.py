from flask import Flask, request, jsonify
import face_recognition
import sqlite3
import numpy as np
import pickle
from datetime import datetime

app = Flask(__name__)

def connect_db():
    return sqlite3.connect('session.db', timeout=10)

def create_or_update_table():
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            NAME TEXT,
            entry_time TEXT,
            exit_time TEXT,
            encoding BLOB
        )
        ''')
        conn.commit()
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def encode_face(face_encoding):
    return pickle.dumps(face_encoding)

def decode_face(encoded_str):
    return pickle.loads(encoded_str)

@app.route('/check_in_or_out', methods=['POST'])
def check_in_or_out():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400

    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    try:
        image = face_recognition.load_image_file(image_file)
        face_encodings = face_recognition.face_encodings(image)
        if not face_encodings:
            return jsonify({'error': 'No faces found in the image'}), 400
        
        face_encoding = face_encodings[0]
        name = find_matching_face(face_encoding)

        if name:
            when_exit(name)
            return jsonify({'message': f'{name} checked out successfully'}), 200
        else:
            actual_name = request.form.get('name')
            if not actual_name:
                return jsonify({'error': 'Name parameter is required'}), 400
            When_entry(actual_name, face_encoding)
            return jsonify({'message': f'{actual_name} checked in successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/attendance', methods=['GET'])
def get_attendance():
    name = request.args.get('name')
    if not name:
        return jsonify({'error': 'Name parameter is required'}), 400

    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT entry_time, exit_time FROM attendance WHERE NAME = ?", (name,))
    record = cursor.fetchone()
    conn.close()

    if record:
        return jsonify({'entry_time': record[0], 'exit_time': record[1]}), 200
    else:
        return jsonify({'error': 'No records found for this name'}), 404

def find_matching_face(face_encoding):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT NAME, encoding FROM attendance")
        all_faces = cursor.fetchall()

        for stored_name, stored_encoding_blob in all_faces:
            if stored_encoding_blob: 
                try:
                    stored_encoding = decode_face(stored_encoding_blob)
                    matches = face_recognition.compare_faces([stored_encoding], face_encoding)
                    if matches[0]: 
                        return stored_name
                except Exception as e:
                    print(f"Error decoding face encoding: {e}")
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
    finally:
        conn.close()
    return None

def When_entry(name, encoding):
    try:
        if isinstance(encoding, np.ndarray):
            encoding_data = encode_face(encoding)
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            conn = connect_db()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO attendance (NAME, entry_time, encoding) VALUES (?, ?, ?)", 
                           (name, current_time, sqlite3.Binary(encoding_data)))
            conn.commit()
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def when_exit(name):
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("UPDATE attendance SET exit_time = ? WHERE NAME = ? AND exit_time IS NULL", 
                       (current_time, name))
        conn.commit()
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    create_or_update_table()
    app.run(debug=True)
