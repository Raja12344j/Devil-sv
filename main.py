from flask import Flask, render_template, request, redirect, session
import json
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

PENDING_FILE = "pending.json"
APPROVED_FILE = "approved.json"

ADMIN_USERNAME = "USERNAME"
ADMIN_PASSWORD = "PASSWORD"


def load_pending():
    if not os.path.exists(PENDING_FILE):
        return {}
    with open(PENDING_FILE, "r") as f:
        return json.load(f)


def save_pending(data):
    with open(PENDING_FILE, "w") as f:
        json.dump(data, f, indent=4)


def load_approved():
    if not os.path.exists(APPROVED_FILE):
        return {}
    with open(APPROVED_FILE, "r") as f:
        return json.load(f)


def save_approved(data):
    with open(APPROVED_FILE, "w") as f:
        json.dump(data, f, indent=4)


@app.route("/")
def home():
    return redirect("/approval_request")


@app.route("/approval_request", methods=["GET", "POST"])
def approval_request():
    if request.method == "POST":
        username = request.form.get("name")
        pending = load_pending()
        uid = str(len(pending) + 1)
        pending[uid] = {"name": username}
        save_pending(pending)
        return "Approval request sent!"
    return render_template("approval_request.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        user = request.form.get("username")
        pw = request.form.get("password")
        if user == ADMIN_USERNAME and pw == ADMIN_PASSWORD:
            session["admin_logged_in"] = True
            return redirect("/admin/panel")
        else:
            return "Wrong admin username or password!"
    return render_template("admin_login.html")


@app.route("/admin/panel")
def admin_panel():
    if "admin_logged_in" not in session:
        return redirect("/admin/login")

    pending = load_pending()
    approved = load_approved()

    return render_template("admin_panel.html",
                           pending=pending,
                           approved=approved)


@app.route("/admin/approve/<uid>")
def approve(uid):
    if "admin_logged_in" not in session:
        return redirect("/admin/login")

    pending = load_pending()
    approved = load_approved()

    if uid in pending:
        approved[uid] = pending[uid]
        del pending[uid]

    save_approved(approved)
    save_pending(pending)

    return redirect("/admin/panel")


@app.route("/admin/reject/<uid>")
def reject(uid):
    if "admin_logged_in" not in session:
        return redirect("/admin/login")

    pending = load_pending()
    if uid in pending:
        del pending[uid]
    save_pending(pending)

    return redirect("/admin/panel")


@app.route("/admin/remove/<uid>")
def remove(uid):
    if "admin_logged_in" not in session:
        return redirect("/admin/login")

    approved = load_approved()
    if uid in approved:
        del approved[uid]
    save_approved(approved)

    return redirect("/admin/panel")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
