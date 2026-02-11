from flask import Flask, request, render_template, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "supersecret"

DATABASE = "database.db"


# ============================
# INIT DATABASE
# ============================

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT
    )
    """)

    c.execute("INSERT OR IGNORE INTO users (id, username, password, role) VALUES (1,'admin','admin123','admin')")
    c.execute("INSERT OR IGNORE INTO users (id, username, password, role) VALUES (2,'user','password','user')")

    conn.commit()
    conn.close()


# ============================
# HOME
# ============================

@app.route("/")
def home():
    return render_template("index.html")


# ============================
# SQL INJECTION (LOGIN)
# ============================

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    user = c.execute(query).fetchone()

    conn.close()

    if user:
        session["user"] = user[1]
        session["role"] = user[3]
        return redirect("/dashboard")

    return "Invalid credentials"


# ============================
# DASHBOARD
# ============================

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    return render_template("dashboard.html", user=session["user"], role=session["role"])


# ============================
# SQL INJECTION (SEARCH)
# ============================

@app.route("/search")
def search():
    term = request.args.get("q", "")

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    query = f"SELECT username FROM users WHERE username LIKE '%{term}%'"
    results = c.execute(query).fetchall()

    conn.close()

    return render_template("search.html", results=results)


# ============================
# STORED XSS
# ============================

@app.route("/comments", methods=["GET", "POST"])
def comments():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    if request.method == "POST":
        content = request.form["content"]

        c.execute(f"INSERT INTO comments (content) VALUES ('{content}')")
        conn.commit()

    c.execute("SELECT content FROM comments")
    all_comments = c.fetchall()
    conn.close()

    return render_template("comments.html", comments=all_comments)


# ============================
# REFLECTED XSS
# ============================

@app.route("/greet")
def greet():
    name = request.args.get("name", "Guest")

    return f"<h1>Hello {name}</h1>"


# ============================
# OS COMMAND INJECTION
# ============================

@app.route("/ping")
def ping():
    host = request.args.get("host")

    if not host:
        return "Provide host parameter"

    result = os.popen(f"ping -c 1 {host}").read()

    if "root" in result:
        flag = "ESECxGCD{COMMAND_INJECTION_SUCCESS}"
    else:
        flag = "No flag yet"

    return f"<pre>{result}</pre><br>{flag}"


# ============================
# ORM-LIKE FILTER INJECTION
# ============================

@app.route("/filter")
def filter_users():
    role = request.args.get("role", "user")

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    query = f"SELECT username FROM users WHERE role = '{role}'"
    results = c.execute(query).fetchall()

    conn.close()

    return {"results": results}


# ============================
# FLAGS ROUTE
# ============================

@app.route("/admin/secret")
def secret():
    if session.get("role") == "admin":
        return "ESECxGCD{SQLI_ADMIN_ACCESS}"
    return "Access denied"


# ============================

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
