from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from . import db
from .models import User


auth_bp = Blueprint("auth", __name__, template_folder="templates")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username or not email or not password:
            flash("Todos los campos son obligatorios", "danger")
        elif password != confirm_password:
            flash("Las contraseñas no coinciden", "danger")
        elif User.query.filter((User.username == username) | (User.email == email)).first():
            flash("El usuario o correo ya existe", "danger")
        else:
            user = User(username=username, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Cuenta creada correctamente. Inicia sesión.", "success")
            return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Bienvenido de nuevo", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.index"))
        flash("Credenciales inválidas", "danger")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("auth.login"))
