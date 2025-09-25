import io
import json
from datetime import datetime

from flask import Blueprint, send_file, request, redirect, url_for, flash, render_template
from flask_login import login_required

from . import db
from .models import User, Client, Invoice, InvoiceItem


backup_bp = Blueprint("backup", __name__, url_prefix="/backup", template_folder="templates")


@backup_bp.route("/exportar")
@login_required
def export_backup():
    data = {
        "users": [
            {"id": user.id, "username": user.username, "email": user.email, "password_hash": user.password_hash}
            for user in User.query.all()
        ],
        "clients": [
            {
                "id": client.id,
                "name": client.name,
                "tax_id": client.tax_id,
                "email": client.email,
                "phone": client.phone,
                "address": client.address,
            }
            for client in Client.query.all()
        ],
        "invoices": [
            {
                "id": invoice.id,
                "invoice_number": invoice.invoice_number,
                "issue_date": invoice.issue_date.isoformat(),
                "due_date": invoice.due_date.isoformat(),
                "status": invoice.status,
                "notes": invoice.notes,
                "client_id": invoice.client_id,
                "user_id": invoice.user_id,
                "subtotal": invoice.subtotal,
                "tax_rate": invoice.tax_rate,
                "total": invoice.total,
            }
            for invoice in Invoice.query.all()
        ],
        "items": [
            {
                "id": item.id,
                "description": item.description,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "line_total": item.line_total,
                "invoice_id": item.invoice_id,
            }
            for item in InvoiceItem.query.all()
        ],
    }

    buffer = io.BytesIO()
    buffer.write(json.dumps(data, indent=2).encode("utf-8"))
    buffer.seek(0)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"backup_appfacturas_{timestamp}.json"

    return send_file(
        buffer,
        mimetype="application/json",
        as_attachment=True,
        download_name=filename,
    )


@backup_bp.route("/importar", methods=["GET", "POST"])
@login_required
def import_backup():
    if request.method == "POST":
        file = request.files.get("backup_file")
        if not file:
            flash("Debes seleccionar un archivo JSON", "danger")
            return redirect(url_for("backup.import_backup"))

        try:
            data = json.load(file)
        except json.JSONDecodeError:
            flash("El archivo no tiene un formato JSON válido", "danger")
            return redirect(url_for("backup.import_backup"))

        InvoiceItem.query.delete()
        Invoice.query.delete()
        Client.query.delete()
        User.query.delete()
        db.session.commit()

        users_map = {}
        for user_data in data.get("users", []):
            user = User(
                id=user_data.get("id"),
                username=user_data.get("username"),
                email=user_data.get("email"),
                password_hash=user_data.get("password_hash"),
            )
            db.session.add(user)
            users_map[user.id] = user

        clients_map = {}
        for client_data in data.get("clients", []):
            client = Client(
                id=client_data.get("id"),
                name=client_data.get("name"),
                tax_id=client_data.get("tax_id"),
                email=client_data.get("email"),
                phone=client_data.get("phone"),
                address=client_data.get("address"),
            )
            db.session.add(client)
            clients_map[client.id] = client

        db.session.flush()

        invoices_map = {}
        for invoice_data in data.get("invoices", []):
            invoice = Invoice(
                id=invoice_data.get("id"),
                invoice_number=invoice_data.get("invoice_number"),
                issue_date=datetime.fromisoformat(invoice_data.get("issue_date")),
                due_date=datetime.fromisoformat(invoice_data.get("due_date")),
                status=invoice_data.get("status"),
                notes=invoice_data.get("notes"),
                client_id=invoice_data.get("client_id"),
                user_id=invoice_data.get("user_id"),
                subtotal=invoice_data.get("subtotal"),
                tax_rate=invoice_data.get("tax_rate"),
                total=invoice_data.get("total"),
            )
            db.session.add(invoice)
            invoices_map[invoice.id] = invoice

        db.session.flush()

        for item_data in data.get("items", []):
            item = InvoiceItem(
                id=item_data.get("id"),
                description=item_data.get("description"),
                quantity=item_data.get("quantity"),
                unit_price=item_data.get("unit_price"),
                line_total=item_data.get("line_total"),
                invoice_id=item_data.get("invoice_id"),
            )
            db.session.add(item)

        db.session.commit()
        flash("Datos restaurados correctamente", "success")
        return redirect(url_for("dashboard.index"))

    return render_template("backup/import.html")
