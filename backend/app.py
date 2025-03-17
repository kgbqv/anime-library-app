# app.py
import sqlite3
from flask import Flask, jsonify, g, request
import flask
from datetime import datetime
import os

#check if flask is installed
print("Flask version is {}".format(flask.__version__))
app = Flask(__name__)

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

# ---------------------------
# Run the App
# ---------------------------

if __name__ == '__main__':
    app.run(debug=True)
