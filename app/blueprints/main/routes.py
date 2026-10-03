from flask import render_template, redirect, url_for
from flask_login import current_user

from app.blueprints.main import main_bp


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        if current_user.is_teacher:
            return redirect(url_for("teacher.dashboard"))
        return redirect(url_for("student.dashboard"))
    return render_template("main/index.html")
