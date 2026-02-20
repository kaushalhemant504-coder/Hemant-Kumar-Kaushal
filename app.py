from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "secret_key_123" # Session security ke liye

def get_db():
    conn = sqlite3.connect("library.db")
    conn.row_factory = sqlite3.Row # Taaki hum data ko column name se access kar sakein
    return conn

# Database Setup
def init_db():
    with get_db() as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS books(
            book_id TEXT PRIMARY KEY, title TEXT, author TEXT, 
            edition TEXT, price TEXT, status TEXT, issued_to TEXT)""")
        conn.execute("CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)")
        
        # Default Admin
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username='admin'")
        if not cur.fetchone():
            conn.execute("INSERT INTO users VALUES (?, ?)", ("admin", "1234"))
        conn.commit()

init_db()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        if user:
            session['user'] = username
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid Credentials!")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    conn = get_db()
    books = conn.execute("SELECT * FROM books").fetchall()
    return render_template('dashboard.html', books=books)

@app.route('/add_book', methods=['POST'])
def add_book():
    data = request.form
    conn = get_db()
    try:
        conn.execute("INSERT INTO books VALUES (?,?,?,?,?,?,?)",
                    (data['b_id'], data['title'], data['author'], data['edition'], data['price'], "Available", ""))
        conn.commit()
        flash("Book Added Successfully!")
    except:
        flash("Error: Book ID already exists!")
    return redirect(url_for('dashboard'))

@app.route('/issue/<id>', methods=['POST'])
def issue_book(id):
    student = request.form['student_id']
    conn = get_db()
    conn.execute("UPDATE books SET status='Issued', issued_to=? WHERE book_id=?", (student, id))
    conn.commit()
    return redirect(url_for('dashboard'))

@app.route('/return/<id>')
def return_book(id):
    conn = get_db()
    conn.execute("UPDATE books SET status='Available', issued_to='' WHERE book_id=?", (id,))
    conn.commit()
    return redirect(url_for('dashboard'))

@app.route('/delete/<id>')
def delete_book(id):
    conn = get_db()
    conn.execute("DELETE FROM books WHERE book_id=?", (id,))
    conn.commit()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    # Isse Render par koi dikkat nahi aayegi
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))

