from flask import Flask, request, jsonify, render_template, redirect, make_response
import sqlite3
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

SECRET_KEY = "secret123"

DATABASE = "database.db"


# ==============================
# DATABASE INIT
# ==============================

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
    CREATE TABLE IF NOT EXISTS invoices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount INTEGER
    )
    """)

    # Default users
    c.execute("INSERT OR IGNORE INTO users (id, username, password, role) VALUES (1, 'admin', 'admin123', 'admin')")
    c.execute("INSERT OR IGNORE INTO users (id, username, password, role) VALUES (2, 'user1', 'password', 'user')")

    # Default invoices
    c.execute("INSERT OR IGNORE INTO invoices (id, user_id, amount) VALUES (1, 2, 500)")
    c.execute("INSERT OR IGNORE INTO invoices (id, user_id, amount) VALUES (2, 1, 1000)")

    conn.commit()
    conn.close()


# ==============================
# AUTH DECORATOR (BROKEN)
# ==============================

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.cookies.get("token")

        if not token:
            return redirect("/")

        try:
            # 🚨 Accepts any algorithm
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.user = data
        except:
            return redirect("/")

        return f(*args, **kwargs)
    return decorated


# ==============================
# ROUTES
# ==============================

@app.route("/")
def home():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()

    if not user:
        return "Invalid credentials"

    token = jwt.encode({
        "user_id": user[0],
        "username": user[1],
        "role": user[3],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1)
    }, SECRET_KEY, algorithm="HS256")

    resp = make_response(redirect("/dashboard"))
    resp.set_cookie("token", token)

    return resp


# ==============================
# DASHBOARD
# ==============================

@app.route("/dashboard")
@token_required
def dashboard():
    return render_template("dashboard.html", user=request.user)


# ==============================
# 🚨 IDOR VULNERABILITY
# ==============================

@app.route("/api/invoice")
@token_required
def get_invoice():
    invoice_id = request.args.get("id")

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM invoices WHERE id=?", (invoice_id,))
    invoice = c.fetchone()
    conn.close()

    if not invoice:
        return jsonify({"error": "Invoice not found"})

    # 🚨 NO ownership check
    if invoice[2] == 1000:
        return jsonify({
            "invoice_id": invoice[0],
            "amount": invoice[2],
            "flag": "ESECxGCD{IDOR_ACCESS_GRANTED}"
        })

    return jsonify({
        "invoice_id": invoice[0],
        "amount": invoice[2]
    })


# ==============================
# 🚨 ADMIN PANEL (NO ROLE CHECK)
# ==============================

@app.route("/admin")
@token_required
def admin():
    if request.user["role"] == "admin":
        flag = "ESECxGCD{ADMIN_PANEL_PWNED}"
    else:
        flag = "ESECxGCD{PRIV_ESCALATION_REQUIRED}"

    return render_template("admin.html", flag=flag)


# ==============================
# 🚨 Missing Method-Level Authorization
# ==============================

@app.route("/api/users", methods=["GET", "DELETE"])
@token_required
def manage_users():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    if request.method == "GET":
        c.execute("SELECT id, username, role FROM users")
        users = c.fetchall()
        conn.close()
        return jsonify(users)

    if request.method == "DELETE":
        user_id = request.args.get("id")
        c.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": "User deleted", "flag": "ESECxGCD{METHOD_LEVEL_BROKEN}"})


# ==============================
# 🚨 CSRF VULNERABILITY
# ==============================

@app.route("/api/change-email", methods=["POST"])
@token_required
def change_email():
    new_email = request.form.get("email")

    return jsonify({
        "message": f"Email changed to {new_email}",
        "flag": "ESECxGCD{CSRF_SUCCESS}"
    })


# ==============================
# 🚨 BUSINESS LOGIC FLAW
# ==============================

@app.route("/api/upgrade-plan", methods=["POST"])
@token_required
def upgrade_plan():
    plan = request.json.get("plan")

    if plan == "premium":
        return jsonify({
            "message": "Upgraded to premium",
            "flag": "ESECxGCD{FREE_PREMIUM_ACCESS}"
        })

    return jsonify({"message": "Invalid plan"})


# ==============================
# RUN
# ==============================

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
