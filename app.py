from flask import Flask, render_template, request, jsonify
from database import get_db_connection, create_table

app = Flask(__name__)


# Display home page
@app.route("/")
def home():
    return render_template("index.html")


# Get all tasks
@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    connection = get_db_connection()

    try:
        tasks = connection.execute(
            "SELECT * FROM tasks ORDER BY id DESC"
        ).fetchall()

        return jsonify([dict(task) for task in tasks])

    finally:
        connection.close()


# Add a new task
@app.route("/api/tasks", methods=["POST"])
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
            INSERT INTO tasks (title, description, priority)
            VALUES (?, ?, ?)
            """,
            (title, description, priority)
        )

        connection.commit()

        return jsonify({
            "message": "Task added successfully"
        }), 201

    finally:
        connection.close()


# Edit task details
@app.route("/api/tasks/<int:task_id>/edit", methods=["PUT"])
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
            SET title = ?, description = ?, priority = ?
            WHERE id = ?
            """,
            (title, description, priority, task_id)
        )

        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({
            "message": "Task edited successfully"
        })

    finally:
        connection.close()


# Mark task as completed or pending
@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
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
            WHERE id = ?
            """,
            (task_id,)
        )

        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({
            "message": "Task status updated successfully"
        })

    finally:
        connection.close()


# Delete a task
@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    connection = get_db_connection()

    try:
        cursor = connection.execute(
            "DELETE FROM tasks WHERE id = ?",
            (task_id,)
        )

        connection.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({
            "message": "Task deleted successfully"
        })

    finally:
        connection.close()


# Run Flask application
if __name__ == "__main__":
    create_table()
    app.run(debug=True)
