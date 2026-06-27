"""
app.py
------
Main Flask application. Run with:
    python app.py

Then open http://127.0.0.1:5000 in your browser.
"""

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from database import get_connection
from chatbot import get_chatbot_response

app = Flask(__name__)
app.secret_key = "change-this-secret-key"   # used to keep login sessions secure


# ------------------------------------------------------------------
# Helper decorators (simple, no extra library needed)
# ------------------------------------------------------------------
def login_required(f):
    from functools import wraps

    @wraps(f)
    def wrapper(*args, **kwargs):
        if "roll_no" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return wrapper


def admin_required(f):
    from functools import wraps

    @wraps(f)
    def wrapper(*args, **kwargs):
        if "admin" not in session:
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return wrapper


# ------------------------------------------------------------------
# Public / Student routes
# ------------------------------------------------------------------
@app.route("/")
def home():
    if "roll_no" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        roll_no = request.form["roll_no"].strip()
        password = request.form["password"].strip()

        conn = get_connection()
        student = conn.execute(
            "SELECT * FROM students WHERE roll_no = ? AND password = ?",
            (roll_no, password)
        ).fetchone()
        conn.close()

        if student:
            session["roll_no"] = student["roll_no"]
            session["name"] = student["name"]
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid roll number or password."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html", name=session.get("name"))


@app.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"reply": "Please type a question."})

    reply = get_chatbot_response(user_message)
    return jsonify({"reply": reply})


@app.route("/timetable")
@login_required
def timetable():
    conn = get_connection()
    student = conn.execute(
        "SELECT * FROM students WHERE roll_no = ?", (session["roll_no"],)
    ).fetchone()

    rows = conn.execute(
        "SELECT * FROM timetable WHERE department = ? AND year = ? "
        "ORDER BY day, period",
        (student["department"], student["year"])
    ).fetchall()
    conn.close()

    return render_template("timetable.html", rows=rows)


@app.route("/faculty")
@login_required
def faculty():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM faculty").fetchall()
    conn.close()
    return render_template("faculty.html", rows=rows)


@app.route("/attendance")
@login_required
def attendance():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM attendance WHERE roll_no = ?", (session["roll_no"],)
    ).fetchall()
    conn.close()

    # Calculate percentage for each subject in Python (basic, beginner friendly)
    attendance_data = []
    for r in rows:
        pct = round((r["attended_classes"] / r["total_classes"]) * 100, 1) if r["total_classes"] else 0
        attendance_data.append({
            "subject": r["subject"],
            "total": r["total_classes"],
            "attended": r["attended_classes"],
            "percentage": pct,
        })

    return render_template("attendance.html", data=attendance_data)


@app.route("/faqs")
@login_required
def faqs():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM knowledge_base WHERE category = 'faq'"
    ).fetchall()
    conn.close()
    return render_template("faqs.html", rows=rows)


# ------------------------------------------------------------------
# Admin routes
# ------------------------------------------------------------------
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        conn = get_connection()
        admin = conn.execute(
            "SELECT * FROM admins WHERE username = ? AND password = ?",
            (username, password)
        ).fetchone()
        conn.close()

        if admin:
            session["admin"] = username
            return redirect(url_for("admin_dashboard"))
        else:
            error = "Invalid admin credentials."

    return render_template("admin_login.html", error=error)


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    return redirect(url_for("admin_login"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM knowledge_base ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("admin_dashboard.html", rows=rows)


@app.route("/admin/add", methods=["POST"])
@admin_required
def admin_add():
    category = request.form["category"].strip()
    question = request.form["question"].strip()
    answer = request.form["answer"].strip()

    conn = get_connection()
    conn.execute(
        "INSERT INTO knowledge_base (category, question, answer) VALUES (?,?,?)",
        (category, question, answer)
    )
    conn.commit()
    conn.close()
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/delete/<int:item_id>")
@admin_required
def admin_delete(item_id):
    conn = get_connection()
    conn.execute("DELETE FROM knowledge_base WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for("admin_dashboard"))


if __name__ == "__main__":
    app.run(debug=True)
