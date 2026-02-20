from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = "secret_key_yahan_kuch_bhi_likho" # Session ke liye zaruri hai
app.config['EXTENSIONS'] = []
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
db = SQLAlchemy(app)

# Book Model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)

# Login Page Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Yahan humne simple check rakha hai
        if username == 'admin' and password == 'password123':
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return "Galat Password! Dubara try karein."
    return '''
        <form method="post">
            Username: <input type="text" name="username"><br>
            Password: <input type="password" name="password"><br>
            <input type="submit" value="Login">
        </form>
    '''

# Protected Index Route
@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    all_books = Book.query.all()
    # Note: Aapko 'index.html' file templates folder mein chahiye hogi
    return f"Logged In! Total Books: {len(all_books)}" 

if __name__ == "__main__":
    with app.app_context():
        db.create_all() # Database file banane ke liye
    app.run(host='0.0.0.0', port=5000, debug=True)
