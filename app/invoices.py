from datetime import datetime

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from . import db
from .models import Client, Invoice, InvoiceItem


invoices_bp = Blueprint("invoices", __name__, url_prefix="/facturas", template_folder="templates")


def _parse_items_from_request(form):
    descriptions = form.getlist("item_description")
    quantities = form.getlist("item_quantity")
    unit_prices = form.getlist("item_unit_price")
    items = []
    for description, quantity, unit_price in zip(descriptions, quantities, unit_prices):
        if not description:
            continue
        qty = int(quantity or 1)
        price = float(unit_price or 0)
        items.append({
            "description": description,
            "quantity": qty,
            "unit_price": price,
            "line_total": qty * price,
        })
    return items


def _recalculate_totals(invoice, items_data, tax_rate):
    subtotal = sum(item["line_total"] for item in items_data)
    total = subtotal + (subtotal * tax_rate / 100)
    invoice.subtotal = subtotal
    invoice.tax_rate = tax_rate
    invoice.total = total


@invoices_bp.route("/")
@login_required
def list_invoices():
    status = request.args.get("estado")
    query = Invoice.query.order_by(Invoice.issue_date.desc())
    if status:
        query = query.filter_by(status=status)
    invoices = query.all()
    return render_template("invoices/list.html", invoices=invoices, status=status)


@invoices_bp.route("/nueva", methods=["GET", "POST"])
@login_required
def create_invoice():
    clients = Client.query.order_by(Client.name.asc()).all()
    if not clients:
        flash("Debes registrar un cliente antes de crear facturas", "warning")
        return redirect(url_for("clients.create_client"))

    if request.method == "POST":
        invoice_number = request.form.get("invoice_number")
        client_id = request.form.get("client_id")
        issue_date = request.form.get("issue_date")
        due_date = request.form.get("due_date")
        status = request.form.get("status") or "pendiente"
        notes = request.form.get("notes")
        tax_rate = float(request.form.get("tax_rate") or 0)

        if not all([invoice_number, client_id, issue_date, due_date]):
            flash("Número de factura, cliente y fechas son obligatorios", "danger")
        else:
            invoice = Invoice(
                invoice_number=invoice_number,
                client_id=int(client_id),
                issue_date=datetime.strptime(issue_date, "%Y-%m-%d"),
                due_date=datetime.strptime(due_date, "%Y-%m-%d"),
                status=status,
                notes=notes,
                user_id=current_user.id,
            )
            items_data = _parse_items_from_request(request.form)
            _recalculate_totals(invoice, items_data, tax_rate)

            try:
                db.session.add(invoice)
                db.session.flush()
                for item in items_data:
                    invoice_item = InvoiceItem(
                        description=item["description"],
                        quantity=item["quantity"],
                        unit_price=item["unit_price"],
                        line_total=item["line_total"],
                        invoice_id=invoice.id,
                    )
                    db.session.add(invoice_item)
                db.session.commit()
                flash("Factura creada correctamente", "success")
                return redirect(url_for("invoices.list_invoices"))
            except IntegrityError:
                db.session.rollback()
                flash("El número de factura ya existe", "danger")

    return render_template("invoices/form.html", clients=clients, invoice=None)


@invoices_bp.route("/<int:invoice_id>")
@login_required
def view_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    return render_template("invoices/detail.html", invoice=invoice)


@invoices_bp.route("/<int:invoice_id>/editar", methods=["GET", "POST"])
@login_required
def edit_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    clients = Client.query.order_by(Client.name.asc()).all()

    if request.method == "POST":
        invoice.invoice_number = request.form.get("invoice_number")
        invoice.client_id = int(request.form.get("client_id"))
        invoice.issue_date = datetime.strptime(request.form.get("issue_date"), "%Y-%m-%d")
        invoice.due_date = datetime.strptime(request.form.get("due_date"), "%Y-%m-%d")
        invoice.status = request.form.get("status")
        invoice.notes = request.form.get("notes")
        tax_rate = float(request.form.get("tax_rate") or 0)

        items_data = _parse_items_from_request(request.form)
        invoice.items.clear()
        db.session.flush()
        for item in items_data:
            invoice.items.append(
                InvoiceItem(
                    description=item["description"],
                    quantity=item["quantity"],
                    unit_price=item["unit_price"],
                    line_total=item["line_total"],
                )
            )

        _recalculate_totals(invoice, items_data, tax_rate)
        db.session.commit()
        flash("Factura actualizada", "success")
        return redirect(url_for("invoices.view_invoice", invoice_id=invoice.id))

    return render_template("invoices/form.html", clients=clients, invoice=invoice)


@invoices_bp.route("/<int:invoice_id>/eliminar", methods=["POST"])
@login_required
def delete_invoice(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    db.session.delete(invoice)
    db.session.commit()
    flash("Factura eliminada", "info")
    return redirect(url_for("invoices.list_invoices"))
