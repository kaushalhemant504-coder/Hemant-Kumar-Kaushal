import tkinter as tk
from tkinter import messagebox
import sqlite3

# ---------------- DATABASE SETUP ----------------
conn = sqlite3.connect("library.db")
cur = conn.cursor()

# Books table
cur.execute("""
CREATE TABLE IF NOT EXISTS books(
    book_id TEXT PRIMARY KEY, title TEXT, author TEXT, 
    edition TEXT, price TEXT, status TEXT, issued_to TEXT)
""")

# Users table (Login ke liye)
cur.execute("CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)")

# Ek default admin account add karein (Sirf pehli baar ke liye)
cur.execute("SELECT * FROM users WHERE username='admin'")
if not cur.fetchone():
    cur.execute("INSERT INTO users VALUES (?, ?)", ("admin", "1234"))
    conn.commit()

# ---------------- APP LOGIC ----------------
def login():
    uname = user_entry.get()
    pwd = pass_entry.get()
    
    cur.execute("SELECT * FROM users WHERE username=? AND password=?", (uname, pwd))
    if cur.fetchone():
        login_window.destroy() # Login window band karein
        main_app()             # Main Library System kholein
    else:
        messagebox.showerror("Error", "Invalid Username or Password")

def main_app():
    global root, b_id, title, author, edition, price, student
    root = tk.Tk()
    root.title("Library Management System")
    root.geometry("450x600")

    # --- UI Elements (Aapka existing GUI) ---
    tk.Label(root, text="--- Library Dashboard ---", font=("Arial", 14, "bold")).pack(pady=10)
    
    fields = [("Book ID", "b_id"), ("Title", "title"), ("Author", "author"), 
              ("Edition", "edition"), ("Price", "price"), ("Student ERP ID", "student")]
    
    # Entries dictionary to store objects
    entries = {}
    for text, var_name in fields:
        tk.Label(root, text=text).pack()
        e = tk.Entry(root)
        e.pack()
        entries[var_name] = e

    # Global variables set karna taaki purane functions kaam karein
    b_id, title, author = entries['b_id'], entries['title'], entries['author']
    edition, price, student = entries['edition'], entries['price'], entries['student']

    # Buttons
    tk.Button(root, text="Add Book", width=25, bg="lightblue", command=add_book).pack(pady=3)
    tk.Button(root, text="Search Book", width=25, command=search_book).pack(pady=3)
    tk.Button(root, text="Issue Book", width=25, command=issue_book).pack(pady=3)
    tk.Button(root, text="Return Book", width=25, command=return_book).pack(pady=3)
    tk.Button(root, text="Delete Book", width=25, fg="white", bg="red", command=delete_book).pack(pady=3)
    tk.Button(root, text="Show All Books", width=25, command=show_books).pack(pady=3)
    tk.Button(root, text="Clear", width=25, command=clear).pack(pady=3)

    root.mainloop()

# ---------------- DATABASE FUNCTIONS ----------------
# (Aapke purane functions yaha add honge: add_book, show_books, etc.)
def add_book():
    if b_id.get()=="":
        messagebox.showerror("Error","Book ID Required")
        return
    cur.execute("INSERT INTO books VALUES (?,?,?,?,?,?,?)",
                (b_id.get(), title.get(), author.get(),
                 edition.get(), price.get(), "Available", ""))
    conn.commit()
    messagebox.showinfo("Success","Book Added")
    clear()

def show_books():
    top = tk.Toplevel(root)
    top.title("All Books")
    cur.execute("SELECT * FROM books")
    for i,row in enumerate(cur.fetchall()):
        tk.Label(top,text=row,font=("Arial",9)).grid(row=i,column=0)

def search_book():
    cur.execute("SELECT * FROM books WHERE book_id=?", (b_id.get(),))
    data = cur.fetchone()
    if data:
        clear() # Pehle purana data clear karein
        b_id.insert(0, data[0])
        title.insert(0,data[1])
        author.insert(0,data[2])
        edition.insert(0,data[3])
        price.insert(0,data[4])
    else:
        messagebox.showerror("Error","Book Not Found")

def issue_book():
    cur.execute("UPDATE books SET status='Issued', issued_to=? WHERE book_id=?",
                (student.get(), b_id.get()))
    conn.commit()
    messagebox.showinfo("Issued","Book Issued")

def return_book():
    cur.execute("UPDATE books SET status='Available', issued_to='' WHERE book_id=?",
                (b_id.get(),))
    conn.commit()
    messagebox.showinfo("Returned","Book Returned")

def delete_book():
    cur.execute("DELETE FROM books WHERE book_id=?", (b_id.get(),))
    conn.commit()
    messagebox.showinfo("Deleted","Book Deleted")
    clear()

def clear():
    for e in [b_id, title, author, edition, price, student]:
        e.delete(0, tk.END)

# ---------------- LOGIN WINDOW ----------------
login_window = tk.Tk()
login_window.title("Login")
login_window.geometry("300x250")

tk.Label(login_window, text="Admin Login", font=("Arial", 12, "bold")).pack(pady=10)

tk.Label(login_window, text="Username").pack()
user_entry = tk.Entry(login_window)
user_entry.pack()

tk.Label(login_window, text="Password").pack()
pass_entry = tk.Entry(login_window, show="*") # Password hide karne ke liye
pass_entry.pack()

tk.Button(login_window, text="Login", width=15, command=login).pack(pady=20)

login_window.mainloop()
