# app.py - Main Flask Application
# Student Task Management System
# This file contains all the routes (pages) of our web application

from flask import Flask, render_template, request, redirect, url_for, session
from database import init_db, get_db_connection

# Create the Flask app
app = Flask(__name__)

# Secret key is needed for session (to remember who is logged in)
app.secret_key = "student_task_manager_secret_key"

# Initialize the database when the app starts
init_db()


# ─────────────────────────────────────────
# HOME PAGE - redirect to login
# ─────────────────────────────────────────
@app.route("/")
def home():
    return redirect(url_for("login"))


# ─────────────────────────────────────────
# REGISTER PAGE - Create a new account
# ─────────────────────────────────────────
@app.route("/register", methods=["GET", "POST"])
def register():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Connect to database
        conn = get_db_connection()

        # Check if username already exists
        existing_user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()

        if existing_user:
            error = "Username already exists. Please choose a different one."
        else:
            # Save new user to database
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password),
            )
            conn.commit()
            conn.close()
            return redirect(url_for("login"))

        conn.close()

    return render_template("register.html", error=error)


# ─────────────────────────────────────────
# LOGIN PAGE - Log in to your account
# ─────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Connect to database and check if user exists
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?",
            (username, password),
        ).fetchone()
        conn.close()

        if user:
            # Save user info in session (so we know who is logged in)
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid username or password. Please try again."

    return render_template("login.html", error=error)


# ─────────────────────────────────────────
# LOGOUT - Clear session and go to login
# ─────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ─────────────────────────────────────────
# DASHBOARD - View all tasks
# ─────────────────────────────────────────
@app.route("/dashboard")
def dashboard():
    # If user is not logged in, send them to login page
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Get all tasks for the logged-in user
    conn = get_db_connection()
    tasks = conn.execute(
        "SELECT * FROM tasks WHERE user_id = ? ORDER BY due_date ASC",
        (session["user_id"],),
    ).fetchall()
    conn.close()

    return render_template("dashboard.html", tasks=tasks, username=session["username"])


# ─────────────────────────────────────────
# ADD TASK - Add a new task
# ─────────────────────────────────────────
@app.route("/add_task", methods=["GET", "POST"])
def add_task():
    # If user is not logged in, send them to login page
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        due_date = request.form["due_date"]

        # Save the new task to database
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO tasks (user_id, title, description, due_date, status) VALUES (?, ?, ?, ?, ?)",
            (session["user_id"], title, description, due_date, "Pending"),
        )
        conn.commit()
        conn.close()

        return redirect(url_for("dashboard"))

    return render_template("add_task.html")


# ─────────────────────────────────────────
# EDIT TASK - Edit an existing task
# ─────────────────────────────────────────
@app.route("/edit_task/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]
        due_date = request.form["due_date"]
        status = request.form["status"]

        # Update the task in database
        conn.execute(
            "UPDATE tasks SET title = ?, description = ?, due_date = ?, status = ? WHERE id = ? AND user_id = ?",
            (title, description, due_date, status, task_id, session["user_id"]),
        )
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))

    # Get the task details to show in the form
    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, session["user_id"]),
    ).fetchone()
    conn.close()

    return render_template("edit_task.html", task=task)


# ─────────────────────────────────────────
# DELETE TASK - Delete a task
# ─────────────────────────────────────────
@app.route("/delete_task/<int:task_id>")
def delete_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    conn.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, session["user_id"]),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


# ─────────────────────────────────────────
# MARK AS COMPLETE - Toggle task status
# ─────────────────────────────────────────
@app.route("/complete_task/<int:task_id>")
def complete_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    conn.execute(
        "UPDATE tasks SET status = 'Completed' WHERE id = ? AND user_id = ?",
        (task_id, session["user_id"]),
    )
    conn.commit()
    conn.close()

    return redirect(url_for("dashboard"))


# Run the app
if __name__ == "__main__":
    app.run(debug=True)
