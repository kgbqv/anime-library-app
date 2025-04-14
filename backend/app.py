import pandas as pd
from flask import Flask, jsonify, request, g, current_app
import sqlite3
import os
from datetime import datetime
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail,Message
from email_helper import registration_email, borrow_email, return_email
import backup_helper
import time

app = Flask(__name__)
CORS(app)


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'voainlp@gmail.com'
app.config['MAIL_PASSWORD'] = 'xkxp qdmq oixy cklw'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)



def send_email(to, subject, body, html):
    msg = Message(
        subject=subject,
        sender='voainlp@gmail.com',  # Ensure this matches MAIL_USERNAME
        recipients=[to]
    )
    msg.body = body
    msg.html = html
    mail.send(msg)

def load_quotes():
    df = pd.read_csv('mysite/quotes.csv')
    df['category'] = df['tags'].apply(lambda x: str(x).split(';'))
    df = df.drop('tags', axis=1)
    return df

df_quotes = load_quotes()

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Welcome to the Quote API. Use the /random-quote endpoint to get a random quote.'
    })

@app.route('/random-quote', methods=['GET'])
def random_quote():
    random_row = df_quotes.sample(n=1).iloc[0]
    return jsonify({
        'id': str(random_row['index']),
        'quote': random_row['quote'],
        'author': random_row['author'],
        'category': random_row['category']
    })

@app.route('/search', methods=['POST'])
def search_quote():
    query = request.get_json().get('query', '')

    filtered_df = df_quotes[
        df_quotes['quote'].str.contains(query, case=False, na=False) |
        df_quotes['category'].apply(lambda categories: any(query in category.lower() for category in categories))
    ]

    if not filtered_df.empty:
        filtered_df.sort_values('likes', inplace=True,ascending=False)
        random_row = filtered_df.sample(n=1).iloc[0]
        return jsonify({
            'id': str(random_row['index']),
            'quote': random_row['quote'],
            'author': random_row['author'],
            'category': random_row['category']
        })
    else:
        return jsonify({"error": "No matching quotes found."})

@app.route('/fetch-quote', methods=['POST'])
def fetch_quote():
    quote_id = request.get_json().get('id', '')

    filtered_df = df_quotes[
        df_quotes['index'] == int(quote_id)
    ]

    if not filtered_df.empty:
        random_row = filtered_df.iloc[0]
        return jsonify({
            'id': str(random_row['index']),
            'quote': random_row['quote'],
            'author': random_row['author'],
            'category': random_row['category']
        })
    else:
        return jsonify({"error": "Quote not found."})

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
            MaHS INTEGER PRIMARY KEY,
            TenHS TEXT NOT NULL,
            Lop TEXT,
            SoDienThoai TEXT,
            Email TEXT,
            password TEXT NOT NULL
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

def get_email_by_mahs(mahs):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT Email FROM HocSinh WHERE MaHS = ?', (mahs,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_ten_by_mahs(mahs):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT TenHS FROM HocSinh WHERE MaHS = ?', (mahs,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_tensach_by_masach(masach):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT TenSach FROM Sach WHERE MaSach = ?', (masach,))
    result = cursor.fetchone()
    return result[0] if result else None



@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    mahs = data.get('MaHS')
    tenhs = data.get('TenHS')
    lop = data.get('Lop')
    sodienthoai = data.get('SoDienThoai')
    email = data.get('Email')
    password = data.get('password')
    if not mahs or not password:
        return jsonify({"error": "MaHS and password are required"}), 400

    hashed_pw = generate_password_hash(password, method='sha256')
    db = get_db()
    try:
        db.execute(
            "INSERT INTO HocSinh (MaHS, TenHS, Lop, SoDienThoai, Email, password) VALUES (?, ?, ?, ?, ?, ?)",
            (mahs, tenhs, lop, sodienthoai, email, hashed_pw)
        )
        db.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    email_content = registration_email(tenhs)
    response = send_email(email, email_content["subject"], email_content["body"], email_content["html"])
    return jsonify({"message": "Registration successful"}), 201

# ---------------------------
# Login Endpoint
# ---------------------------
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    mahs = data.get('MaHS')
    password = data.get('password')
    if not mahs or not password:
        return jsonify({"error": "MaHS and password are required"}), 400

    db = get_db()
    cursor = db.execute("SELECT * FROM HocSinh WHERE MaHS = ?", (mahs,))
    user = cursor.fetchone()
    if not user:
        return jsonify({"error": "User not found"}), 404

    if check_password_hash(user['password'], password):
        # In a real app, you would create a session or token here.
        return jsonify({"message": "Login successful", "MaHS": user["MaHS"], "TenHS": user["TenHS"]}), 200
    else:
        return jsonify({"error": "Incorrect password"}), 401

# ---------------------------
# Edit Info Endpoint
# ---------------------------
@app.route('/edit_info', methods=['POST'])
def edit_info():
    data = request.get_json()
    mahs = data.get('MaHS')
    if not mahs:
        return jsonify({"error": "MaHS is required"}), 400

    # Only update fields that are provided
    fields = []
    params = []
    if data.get('TenHS'):
        fields.append("TenHS = ?")
        params.append(data.get('TenHS'))
    if data.get('Lop'):
        fields.append("Lop = ?")
        params.append(data.get('Lop'))
    if data.get('SoDienThoai'):
        fields.append("SoDienThoai = ?")
        params.append(data.get('SoDienThoai'))
    if data.get('Email'):
        fields.append("Email = ?")
        params.append(data.get('Email'))
    if data.get('password'):
        hashed_pw = generate_password_hash(data.get('password'), method='sha256')
        fields.append("password = ?")
        params.append(hashed_pw)
    if not fields:
        return jsonify({"error": "No fields to update"}), 400
    params.append(mahs)

    db = get_db()
    try:
        query = "UPDATE HocSinh SET " + ", ".join(fields) + " WHERE MaHS = ?"
        db.execute(query, tuple(params))
        db.commit()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "User info updated successfully"}), 200


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

@app.route('/api/metadata', methods=['GET'])
def get_metadata():
    db = get_db()
    cursor = db.execute('SELECT DISTINCT TheLoai FROM Sach')
    genres = [row['TheLoai'] for row in cursor.fetchall()]
    cursor = db.execute('SELECT DISTINCT TacGia FROM Sach')
    authors = [row['TacGia'] for row in cursor.fetchall()]
    print(f"Fetched genres: {genres}")
    print(f"Fetched authors: {authors}")
    return jsonify({'genres': genres, 'authors': authors})

@app.route('/api/filter_books', methods=['POST'])
def filter_books():
    data = request.get_json() or {}
    genres_list = data.get('genres', [])
    authors_list = data.get('authors', [])
    titles_list = data.get('titles', [])

    db = get_db()
    query = "SELECT * FROM Sach WHERE 1=1"
    params = []

    # Filter by genre
    if genres_list:
        placeholders = ','.join('?' for _ in genres_list)
        query += f" AND TheLoai IN ({placeholders})"
        params.extend(genres_list)

    # Filter by author
    if authors_list:
        placeholders = ','.join('?' for _ in authors_list)
        query += f" AND TacGia IN ({placeholders})"
        params.extend(authors_list)

    # Filter by title substring
    if titles_list:
        # build: AND (TenSach LIKE ? OR TenSach LIKE ? OR ...)
        like_clauses = []
        for _ in titles_list:
            like_clauses.append("TenSach LIKE ?")
        query += " AND (" + " AND ".join(like_clauses) + ")"
        # for each title, wrap with wildcards
        params.extend([f"%{t}%" for t in titles_list])

    cursor = db.execute(query, tuple(params))
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
    if password_arg != 'adminpanel123':
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
        tenhs = get_ten_by_mahs(ma_hs)
        email = get_email_by_mahs(ma_hs)
        tensach = get_tensach_by_masach(ma_sach)
        email_content = borrow_email(tenhs, tensach, "whenever you finish it.")
        response = send_email(email, email_content["subject"], email_content["body"], email_content["html"])
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
        tenhs = get_ten_by_mahs(ma_hs)
        email = get_email_by_mahs(ma_hs)
        tensach = get_tensach_by_masach(ma_sach)
        email_content = return_email(tenhs, tensach)
        response = send_email(email, email_content["subject"], email_content["body"], email_content["html"])
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

from langchain_google_genai import ChatGoogleGenerativeAI

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = 'AIzaSyCpFPHPTkec6_umV-NT3zfc5_wPTH1ld2Q'

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-001",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2
)

@app.route('/api/gemini', methods=['POST'])
def gemini_response():
    """
    Receives a prompt in JSON, uses the Gemini LLM to generate a response,
    and returns the response as JSON.
    """
    data = request.get_json()
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({"error": "A prompt is required."}), 400

    try:
        # Generate response from the language model.
        response_text = llm(prompt)
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": f"LLM error: {str(e)}"}), 500

# ---------------------------
# Translation Endpoint using Gemini LLM
# ---------------------------
# ---------------------------
# Book Query Endpoint using Gemini LLM
# ---------------------------
@app.route('/api/book_query', methods=['POST'])
def book_query():
    """
    Receives a book description in the JSON payload,
    queries the available books from the database,
    and uses the Gemini LLM to suggest which book best fits the description.
    Responds with the book's ID and a short explanation.
    """
    data = request.get_json()
    description = data.get('description', '')
    if not description:
        return jsonify({"error": "No description provided."}), 400

    # Query the database for available books (for example, books that are in stock).
    db = get_db()
    cursor = db.execute('SELECT MaSach, TenSach, TacGia, TheLoai, SoLuong FROM Sach WHERE SoLuong > 0')
    books = cursor.fetchall()

    if not books:
        return jsonify({"error": "No available books in the database."}), 404

    # Build a text summary of the available books.
    # This summary will be passed to the LLM so it can match the description with the book details.
    book_list_str = "\n".join([
        f"ID: {book['MaSach']}, Title: {book['TenSach']}, Author: {book['TacGia']}, Genre: {book['TheLoai']}"
        for book in books
    ])

    # Create a system message that includes the available book list and instruction.
    system_message = (
        "You are a helpful assistant that selects the best matching book from the available list given a description. "
        "Below is the list of available books:\n"
        f"{book_list_str}\n\n"
        "Based on the user description, please respond with the book's ID and a short explanation about why it matches."
    )

    # The human message carries the user-provided description.
    messages = [
    {"role": "system",  "content": system_message},
    {"role": "user",    "content": description}
    ]


    try:
        # Invoke the Gemini LLM with the prompt messages.
        response_text = llm.invoke(messages)
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": f"LLM error: {str(e)}"}), 500

if __name__ == '__main__':
    app.run()