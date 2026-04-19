from flask import Flask, request, render_template, redirect, make_response
import sqlite3
import os

app = Flask(__name__)

# Hardcoded credentials (BAD PRACTICE)
USERNAME = "admin"
PASSWORD = "password123"

# Используем переменную окружения для пути к БД
DB_PATH = os.environ.get('DB_PATH', '/app/data/test.db')

# Insecure database setup
def init_db():
    # Создаем директорию для БД если её нет
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)")
    c.execute("INSERT INTO users (username, password) VALUES ('user1', 'password1')")
    conn.commit()
    conn.close()

# Вызываем при старте
init_db()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")

    # SQL Injection Vulnerability
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    result = c.execute(query).fetchone()

    if result:
        response = make_response(redirect("/dashboard"))
        response.set_cookie("session", username)  # Insecure session management
        return response
    else:
        return "Invalid credentials. <a href='/'>Try again</a>"

@app.route("/dashboard")
def dashboard():
    # No authentication check
    user = request.cookies.get("session", "guest")
    return f"<h1>Welcome, {user}!</h1> <script>alert('XSS Vulnerability!')</script>"

@app.route("/search", methods=["GET"])
def search():
    # Reflective XSS vulnerability
    query = request.args.get("q", "")
    return f"<h1>Search Results for {query}</h1>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)