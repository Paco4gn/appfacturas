from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from . import db
from .models import Client


clients_bp = Blueprint("clients", __name__, url_prefix="/clientes", template_folder="templates")


@clients_bp.route("/")
@login_required
def list_clients():
    query = Client.query.order_by(Client.name.asc())
    search = request.args.get("q")
    if search:
        like_term = f"%{search.lower()}%"
        query = query.filter(db.func.lower(Client.name).like(like_term))
    clients = query.all()
    return render_template("clients/list.html", clients=clients, search=search)


@clients_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def create_client():
    if request.method == "POST":
        name = request.form.get("name")
        tax_id = request.form.get("tax_id")
        email = request.form.get("email")
        phone = request.form.get("phone")
        address = request.form.get("address")

        if not name or not tax_id or not email:
            flash("Nombre, identificación fiscal y correo son obligatorios", "danger")
        else:
            client = Client(name=name, tax_id=tax_id, email=email, phone=phone, address=address)
            db.session.add(client)
            db.session.commit()
            flash("Cliente creado correctamente", "success")
            return redirect(url_for("clients.list_clients"))

    return render_template("clients/form.html", client=None)


@clients_bp.route("/<int:client_id>/editar", methods=["GET", "POST"])
@login_required
def edit_client(client_id):
    client = Client.query.get_or_404(client_id)
    if request.method == "POST":
        client.name = request.form.get("name")
        client.tax_id = request.form.get("tax_id")
        client.email = request.form.get("email")
        client.phone = request.form.get("phone")
        client.address = request.form.get("address")

        if not client.name or not client.tax_id or not client.email:
            flash("Nombre, identificación fiscal y correo son obligatorios", "danger")
        else:
            db.session.commit()
            flash("Cliente actualizado", "success")
            return redirect(url_for("clients.list_clients"))

    return render_template("clients/form.html", client=client)


@clients_bp.route("/<int:client_id>/eliminar", methods=["POST"])
@login_required
def delete_client(client_id):
    client = Client.query.get_or_404(client_id)
    db.session.delete(client)
    db.session.commit()
    flash("Cliente eliminado", "info")
    return redirect(url_for("clients.list_clients"))
