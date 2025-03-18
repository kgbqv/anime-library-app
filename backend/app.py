# app.py
from flask import Flask, jsonify, g, request
from flask_cors import CORS  # Import Flask-CORS
from datetime import datetime
import os
import sqlite3

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Path to SQLite database file
DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'library.db')

def get_db():
    """Opens a new database connection if there is none yet for the current application context."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # to access columns by name
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Closes the database connection at the end of the request."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database and create tables if they don't exist."""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Sach (
            MaSach INTEGER PRIMARY KEY AUTOINCREMENT,
            TenSach TEXT NOT NULL,
            TacGia TEXT,
            TheLoai TEXT,
            SoLuong INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS HocSinh (
            MaHS INTEGER PRIMARY KEY AUTOINCREMENT,
            TenHS TEXT NOT NULL,
            Lop TEXT,
            SoDienThoai TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MuonSach (
            MaMuon INTEGER PRIMARY KEY AUTOINCREMENT,
            MaHS INTEGER NOT NULL,
            MaSach INTEGER NOT NULL,
            NgayMuon TEXT DEFAULT CURRENT_TIMESTAMP,
            NgayTra TEXT,
            TrangThai TEXT DEFAULT 'Chưa trả',
            FOREIGN KEY(MaHS) REFERENCES HocSinh(MaHS),
            FOREIGN KEY(MaSach) REFERENCES Sach(MaSach)
        )
    ''')
    db.commit()

with app.app_context():
    init_db()

# ---------------------------
# API Endpoints
# ---------------------------

@app.route('/api/books', methods=['GET'])
def get_books():
    """Return list of available books (SoLuong > 0)"""
    db = get_db()
    cursor = db.execute('SELECT * FROM Sach WHERE SoLuong > 0')
    books = cursor.fetchall()
    result = []
    for book in books:
        result.append({
            'MaSach': book['MaSach'],
            'TenSach': book['TenSach'],
            'TacGia': book['TacGia'],
            'TheLoai': book['TheLoai'],
            'SoLuong': book['SoLuong']
        })
    return jsonify(result)

@app.route('/api/students', methods=['GET'])
def get_students():
    """Return list of students"""
    db = get_db()
    cursor = db.execute('SELECT * FROM HocSinh')
    students = cursor.fetchall()
    result = []
    for student in students:
        result.append({
            'MaHS': student['MaHS'],
            'TenHS': student['TenHS'],
            'Lop': student['Lop'],
            'SoDienThoai': student['SoDienThoai']
        })
    return jsonify(result)

@app.route('/api/overdue', methods=['GET'])
def get_overdue():
    """
    Return list of overdue loan records.
    Overdue is defined as NgayTra earlier than the current UTC time
    and TrangThai is 'Chưa trả'.
    """
    now = datetime.utcnow().isoformat()
    db = get_db()
    query = '''
        SELECT hs.TenHS, s.TenSach, ms.NgayTra
        FROM MuonSach ms
        JOIN HocSinh hs ON ms.MaHS = hs.MaHS
        JOIN Sach s ON ms.MaSach = s.MaSach
        WHERE ms.NgayTra < ? AND ms.TrangThai = 'Chưa trả'
    '''
    cursor = db.execute(query, (now,))
    records = cursor.fetchall()
    result = []
    for record in records:
        result.append({
            'TenHS': record['TenHS'],
            'TenSach': record['TenSach'],
            'NgayTra': record['NgayTra']
        })
    return jsonify(result)

@app.route('/api/most_borrowed', methods=['GET'])
def most_borrowed():
    """Return the most frequently borrowed book."""
    db = get_db()
    query = '''
        SELECT s.TenSach, COUNT(ms.MaMuon) AS SoLanMuon
        FROM MuonSach ms
        JOIN Sach s ON ms.MaSach = s.MaSach
        GROUP BY s.TenSach
        ORDER BY SoLanMuon DESC
        LIMIT 1
    '''
    cursor = db.execute(query)
    result = cursor.fetchone()
    if result:
        return jsonify({'TenSach': result['TenSach'], 'SoLanMuon': result['SoLanMuon']})
    else:
        return jsonify({}), 404

@app.route('/api/create_book', methods=['POST'])
def create_book():
    data = request.get_json()
    ten_sach = data.get('TenSach')
    tac_gia = data.get('TacGia')
    the_loai = data.get('TheLoai')
    so_luong = data.get('SoLuong', 0)  # Default to 0 if not provided

    if not ten_sach:
        return jsonify({'error': 'Book title (TenSach) is required'}), 400

    db = get_db()
    query = '''
        INSERT INTO Sach (TenSach, TacGia, TheLoai, SoLuong)
        VALUES (?, ?, ?, ?)
    '''
    cursor = db.execute(query, (ten_sach, tac_gia, the_loai, so_luong))
    db.commit()
    return jsonify({
        'message': 'Book created successfully',
        'MaSach': cursor.lastrowid
    }), 201

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    # Check for password in query parameter
    password_arg = request.args.get('password')
    if password_arg != 'adminpanel':
        return "Access Denied.", 403

    db = get_db()
    cursor = db.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    tables_list = [row['name'] for row in tables]

    result = None
    error = None

    if request.method == 'POST' and 'command' in request.form:
        command = request.form.get('command')
        if command:
            try:
                cursor = db.execute(command)
                db.commit()
                # If it's a SELECT command, fetch and show the results
                if command.strip().upper().startswith('SELECT'):
                    result = cursor.fetchall()
                else:
                    result = f"Command executed successfully. Rows affected: {cursor.rowcount}"
            except Exception as e:
                error = str(e)

    html = """
    <html>
      <head>
        <title>Admin Panel</title>
        <style>
          body { background: #111; color: #eee; font-family: sans-serif; padding: 20px; }
          h1, h2 { color: #d23669; }
          table { border-collapse: collapse; width: 100%; }
          th, td { border: 1px solid #555; padding: 5px; text-align: left; }
          textarea { width: 100%; }
          input[type="submit"] { background: #d23669; border: none; color: #fff; padding: 10px 20px; cursor: pointer; }
          input[type="submit"]:hover { background: #a12852; }
        </style>
      </head>
      <body>
        <h1>Admin Panel</h1>
        <h2>Current Tables</h2>
        <ul>
    """
    for table in tables_list:
        html += f"<li>{table}</li>"
    html += "</ul>"

    html += """
        <h2>Execute SQL Command</h2>
        <form method="post">
          <textarea name="command" rows="4" placeholder="Enter SQL command here"></textarea><br>
          <input type="submit" value="Execute">
        </form>
    """
    if error:
        html += f"<p style='color:red;'>Error: {error}</p>"
    if result:
        if isinstance(result, list):
            html += "<h3>Query Result:</h3><table><tr>"
            if result:
                keys = result[0].keys()
                for key in keys:
                    html += f"<th>{key}</th>"
                html += "</tr>"
                for row in result:
                    html += "<tr>"
                    for key in keys:
                        html += f"<td>{row[key]}</td>"
                    html += "</tr>"
            else:
                html += "<tr><td>No results</td></tr>"
            html += "</table>"
        else:
            html += f"<p>{result}</p>"
    html += "</body></html>"
    return html


@app.route('/api/borrow', methods=['POST'])
def borrow_book():
    data = request.get_json()
    ma_hs = data.get('MaHS')
    ma_sach = data.get('MaSach')
    if not ma_hs or not ma_sach:
        return jsonify({'error': 'Missing Student ID (MaHS) or Book ID (MaSach)'}), 400
    db = get_db()
    try:
        cursor = db.execute('SELECT SoLuong FROM Sach WHERE MaSach = ?', (ma_sach,))
        book = cursor.fetchone()
        if not book or book['SoLuong'] <= 0:
            return jsonify({'error': 'Book not available'}), 400
        new_quantity = book['SoLuong'] - 1
        db.execute('UPDATE Sach SET SoLuong = ? WHERE MaSach = ?', (new_quantity, ma_sach))
        borrow_cursor = db.execute(
            'INSERT INTO MuonSach (MaHS, MaSach, NgayMuon, TrangThai) VALUES (?, ?, datetime("now"), "Chưa trả")',
            (ma_hs, ma_sach)
        )
        db.commit()
        return jsonify({'message': 'Book borrowed successfully', 'MaMuon': borrow_cursor.lastrowid}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/return', methods=['POST'])
def return_book():
    data = request.get_json()
    ma_hs = data.get('MaHS')
    ma_sach = data.get('MaSach')
    if not ma_hs or not ma_sach:
        return jsonify({'error': 'Missing Student ID (MaHS) or Book ID (MaSach)'}), 400
    db = get_db()
    try:
        cursor = db.execute(
            'SELECT MaMuon FROM MuonSach WHERE MaHS = ? AND MaSach = ? AND TrangThai = "Chưa trả"',
            (ma_hs, ma_sach)
        )
        record = cursor.fetchone()
        if not record:
            return jsonify({'error': 'No outstanding borrow record found'}), 400
        db.execute(
            'UPDATE MuonSach SET TrangThai = "Đã trả", NgayTra = datetime("now") WHERE MaMuon = ?',
            (record['MaMuon'],)
        )
        cursor = db.execute('SELECT SoLuong FROM Sach WHERE MaSach = ?', (ma_sach,))
        book = cursor.fetchone()
        new_quantity = book['SoLuong'] + 1 if book else 0
        db.execute('UPDATE Sach SET SoLuong = ? WHERE MaSach = ?', (new_quantity, ma_sach))
        db.commit()
        return jsonify({'message': 'Book returned successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---------------------------
# Visitor Logging Endpoint
# ---------------------------
@app.route('/log_visit', methods=['POST'])
def log_visit():
    ip = request.remote_addr
    timestamp = datetime.utcnow().isoformat()
    app.logger.info("Visitor logged: IP: %s at %s", ip, timestamp)
    return jsonify({"message": "Visit logged"}), 200


if __name__ == '__main__':
    app.run(debug=True)
