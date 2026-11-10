
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from database import get_db_connection, create_table
from functools import wraps
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__, static_folder="public/static", static_url_path="/static")

app.secret_key = os.environ.get("SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("SECRET_KEY is missing. Check your .env file.")

if os.environ.get("VERCEL"):
    app.config["SESSION_COOKIE_SECURE"] = True

app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

create_table()


def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return function(*args, **kwargs)
    return wrapper


def api_login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"error": "Please login first"}), 401
        return function(*args, **kwargs)
    return wrapper


@app.route("/")
@login_required
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please enter both username and password.")
            return redirect(url_for("register"))

        if len(password) < 6:
            flash("Password must contain at least 6 characters.")
            return redirect(url_for("register"))

        connection = get_db_connection()

        try:
            existing_user = connection.execute(
                "SELECT id FROM users WHERE username = %s",
                (username,)
            ).fetchone()

            if existing_user:
                flash("Username already exists. Please choose another.")
                return redirect(url_for("register"))

            user_count = connection.execute(
                "SELECT COUNT(*) AS count FROM users"
            ).fetchone()["count"]

            password_hash = generate_password_hash(password)

            cursor = connection.execute(
                """
                INSERT INTO users (username, password_hash)
                VALUES (%s, %s)
                RETURNING id
                """,
                (username, password_hash)
            )

            new_user_id = cursor.fetchone()["id"]

            if user_count == 0:
                connection.execute(
                    "UPDATE tasks SET user_id = %s WHERE user_id IS NULL",
                    (new_user_id,)
                )

            connection.commit()

            session["user_id"] = new_user_id
            session["username"] = username

            return redirect(url_for("home"))

        finally:
            connection.close()

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        connection = get_db_connection()

        try:
            user = connection.execute(
                "SELECT * FROM users WHERE username = %s",
                (username,)
            ).fetchone()

            if user and check_password_hash(user["password_hash"], password):
                session.clear()
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                return redirect(url_for("home"))

            flash("Invalid username or password.")
            return redirect(url_for("login"))

        finally:
            connection.close()

    return render_template("login.html")


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/api/tasks", methods=["GET"])
@api_login_required
def get_tasks():
    connection = get_db_connection()

    try:
        tasks = connection.execute(
            """
            SELECT * FROM tasks
            WHERE user_id = %s
            ORDER BY id DESC
            """,
            (session["user_id"],)
        ).fetchall()

        return jsonify(tasks)

    finally:
        connection.close()


@app.route("/api/tasks", methods=["POST"])
@api_login_required
def add_task():
    data = request.get_json(silent=True) or {}

    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    priority = data.get("priority", "Medium")

    if not title:
        return jsonify({"error": "Task title is required"}), 400

    if priority not in ["High", "Medium", "Low"]:
        return jsonify({"error": "Invalid priority"}), 400

    connection = get_db_connection()

    try:
        connection.execute(
            """
            INSERT INTO tasks (title, description, priority, user_id)
            VALUES (%s, %s, %s, %s)
            """,
            (title, description, priority, session["user_id"])
        )

        connection.commit()

        return jsonify({"message": "Task added successfully"}), 201

    finally:
        connection.close()


@app.route("/api/tasks/<int:task_id>/edit", methods=["PUT"])
@api_login_required
def edit_task(task_id):
    data = request.get_json(silent=True) or {}

    title = data.get("title", "").strip()
    description = data.get("description", "").strip()
    priority = data.get("priority", "Medium")

    if not title:
        return jsonify({"error": "Task title is required"}), 400

    if priority not in ["High", "Medium", "Low"]:
        return jsonify({"error": "Invalid priority"}), 400

    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE tasks
            SET title = %s, description = %s, priority = %s
            WHERE id = %s AND user_id = %s
            """,
            (title, description, priority, task_id, session["user_id"])
        )

        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({"message": "Task edited successfully"})

    finally:
        connection.close()


@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
@api_login_required
def update_task(task_id):
    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            UPDATE tasks
            SET completed = CASE
                WHEN completed = 0 THEN 1
                ELSE 0
            END
            WHERE id = %s AND user_id = %s
            """,
            (task_id, session["user_id"])
        )

        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({"message": "Task status updated successfully"})

    finally:
        connection.close()


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@api_login_required
def delete_task(task_id):
    connection = get_db_connection()

    try:
        cursor = connection.execute(
            """
            DELETE FROM tasks
            WHERE id = %s AND user_id = %s
            """,
            (task_id, session["user_id"])
        )

        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({"message": "Task deleted successfully"})

    finally:
        connection.close()


if __name__ == "__main__":
    app.run(debug=True)
