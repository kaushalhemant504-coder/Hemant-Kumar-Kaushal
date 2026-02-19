from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "library_admin_key"

def get_db():
    conn = sqlite3.connect("library.db")
    conn.row_factory = sqlite3.Row # Taaki columns ko naam se access kar sakein
    return conn

@app.route('/')
def index():
    if 'user' in session: return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if request.form['username'] == 'admin' and request.form['password'] == '1234':
        session['user'] = 'admin'
        return redirect(url_for('dashboard'))
    flash("Invalid Credentials!")
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user' not in session: return redirect(url_for('index'))
    search_query = request.args.get('search', '')
    conn = get_db()
    
    if search_query:
        # Search query check kar rahe hain Title ya ID mein
        books = conn.execute("SELECT * FROM books WHERE title LIKE ? OR book_id LIKE ?", 
                             ('%'+search_query+'%', '%'+search_query+'%')).fetchall()
    else:
        books = conn.execute("SELECT * FROM books").fetchall()
    
    conn.close()
    return render_template('dashboard.html', books=books, search_query=search_query)

@app.route('/add', methods=['POST'])
def add_book():
    data = (request.form['b_id'], request.form['title'], request.form['author'], "Available", "")
    conn = get_db()
    try:
        conn.execute("INSERT INTO books VALUES (?,?,?,?,?)", data)
        conn.commit()
    except: flash("Book ID already exists!")
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/delete/<id>')
def delete_book(id):
    conn = get_db()
    conn.execute("DELETE FROM books WHERE book_id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/issue', methods=['POST'])
def issue_book():
    conn = get_db()
    conn.execute("UPDATE books SET status='Issued', issued_to=? WHERE book_id=?", 
                 (request.form['student'], request.form['b_id']))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/return/<id>')
def return_book(id):
    conn = get_db()
    conn.execute("UPDATE books SET status='Available', issued_to='' WHERE book_id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
