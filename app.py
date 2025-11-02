from flask import Flask, render_template, request, redirect, url_for, session, g, flash
import sqlite3
import os
import urllib.parse

app = Flask(__name__)
app.secret_key = "dev-secret-key-please-change"  # untuk lab saja

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(BASE_DIR, "app.db")

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exc):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

# -----------------------
# PUBLIC PAGES 
# -----------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/public")
def public():
    return render_template("public.html")

# -----------------------
# AUTH 
# -----------------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        db = get_db()
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        cur = db.execute(query)
        user = cur.fetchone()

        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            flash("Login sukses", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Login gagal", "danger")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

# -----------------------
# USER DASHBOARD (private)
# -----------------------
def login_required(fn):
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return fn(*args, **kwargs)
    return wrapper

@app.route("/dashboard")
@login_required
def dashboard():
    db = get_db()
    user_id = session["user_id"]
    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    account = db.execute("SELECT * FROM accounts WHERE user_id = ?", (user_id,)).fetchone()
    comments = db.execute("SELECT c.*, u.username FROM comments c JOIN users u ON c.user_id = u.id ORDER BY c.id DESC").fetchall()
    return render_template("dashboard.html", user=user, account=account, comments=comments)

# -----------------------
# PROFILE
# -----------------------
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    db = get_db()
    user_id = session["user_id"]
    if request.method == "POST":
        # allow user to post a comment (stored, no sanitization -> XSS)
        comment = request.form.get("comment", "")
        db.execute("INSERT INTO comments (user_id, comment) VALUES (?, ?)", (user_id, comment))
        db.commit()
        flash("Komentar ditambahkan", "success")
        return redirect(url_for("profile"))

    user = db.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    comments = db.execute("SELECT c.*, u.username FROM comments c JOIN users u ON c.user_id = u.id ORDER BY c.id DESC").fetchall()
    return render_template("profile.html", user=user, comments=comments)

# -----------------------
# TRANSFER 
# -----------------------
@app.route("/transfer", methods=["GET", "POST"])
@login_required
def transfer():
    db = get_db()
    user_id = session["user_id"]
    account = db.execute("SELECT * FROM accounts WHERE user_id = ?", (user_id,)).fetchone()

    if request.method == "POST":
        to_user = request.form.get("to_user")
        amount = int(request.form.get("amount", "0"))
        # simple transfer logic (no transaction safety for simplicity)
        if amount <= 0:
            flash("Jumlah tidak valid", "danger")
            return redirect(url_for("transfer"))

        to = db.execute("SELECT * FROM users WHERE username = ?", (to_user,)).fetchone()
        if not to:
            flash("Penerima tidak ditemukan", "danger")
            return redirect(url_for("transfer"))

        # debit sender
        sender_acc = db.execute("SELECT * FROM accounts WHERE user_id = ?", (user_id,)).fetchone()
        if sender_acc["balance"] < amount:
            flash("Saldo tidak cukup", "danger")
            return redirect(url_for("transfer"))

        db.execute("UPDATE accounts SET balance = balance - ? WHERE user_id = ?", (amount, user_id))
        db.execute("UPDATE accounts SET balance = balance + ? WHERE user_id = ?", (amount, to["id"]))
        db.commit()
        flash(f"Transfer {amount} ke {to_user} berhasil", "success")
        return redirect(url_for("dashboard"))

    return render_template("transfer.html", account=account)

# -----------------------
# ADMIN (demonstrate route protected)
# -----------------------
@app.route("/admin")
@login_required
def admin():
    if session.get("role") != "admin":
        flash("Akses ditolak: bukan admin", "danger")
        return redirect(url_for("dashboard"))
    db = get_db()
    users = db.execute("SELECT u.id, u.username, u.fullname, a.balance FROM users u LEFT JOIN accounts a ON u.id = a.user_id").fetchall()
    return render_template("admin.html", users=users)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
