# Every page of the website. app.py registers this blueprint.
from flask import Blueprint, redirect, render_template, request, session, url_for

from extension import db
from model.model import Submission
from service.analyzer import analyse, dashboard_numbers, read_resume_file, save_submission
from service.login import admin_only, check_login, is_logged_in, log_in, log_out

main = Blueprint("main", __name__)


# ---------- Public pages ----------

@main.route("/")
def index():
    return render_template("index.html")


@main.route("/analyze", methods=["POST"])
def analyze():
    file = request.files.get("resume")
    job_description = request.form.get("job_description", "")

    if not file or file.filename == "":
        return render_template("index.html", error="Please choose a resume file to upload."), 400

    try:
        text, page_count = read_resume_file(file)
    except ValueError as problem:
        return render_template("index.html", error=str(problem)), 400

    result = analyse(text, job_description, page_count)
    session["last_submission_id"] = save_submission(result)
    return redirect(url_for("main.results"))


@main.route("/results")
def results():
    submission_id = session.get("last_submission_id")
    submission = db.session.get(Submission, submission_id) if submission_id else None

    if submission is None:
        return redirect(url_for("main.index"))
    return render_template("results.html", r=submission.result())


# ---------- Admin pages ----------

@main.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if is_logged_in():
        return redirect(url_for("main.admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        if not username or not password:
            return render_template("login.html", error="Please enter your username and password."), 400
        if not check_login(username, password):
            return render_template("login.html", error="Incorrect username or password."), 401

        log_in()
        return redirect(url_for("main.admin_dashboard"))

    return render_template("login.html")


@main.route("/admin")
@admin_only
def admin_dashboard():
    rows, count, average, top_field = dashboard_numbers()
    return render_template("dashboard.html", rows=rows, count=count, average=average, top_field=top_field)


@main.route("/admin/logout", methods=["POST"])
@admin_only
def admin_logout():
    log_out()
    return redirect(url_for("main.admin_login"))


# ---------- Errors ----------

@main.app_errorhandler(413)
def file_too_big(error):
    return render_template("index.html", error="That file is too big. Please upload a file under 5 MB."), 413
