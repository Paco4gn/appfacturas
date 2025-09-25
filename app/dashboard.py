from flask import Blueprint, render_template
from flask_login import login_required, current_user

from .models import Client, Invoice


dashboard_bp = Blueprint("dashboard", __name__, template_folder="templates")


def _calculate_totals(invoices):
    total_pending = sum(inv.total for inv in invoices if inv.status == "pendiente")
    total_paid = sum(inv.total for inv in invoices if inv.status == "pagada")
    return total_pending, total_paid


@dashboard_bp.route("/")
@login_required
def index():
    clients_count = Client.query.count()
    invoices = Invoice.query.order_by(Invoice.issue_date.desc()).limit(5).all()
    total_pending, total_paid = _calculate_totals(Invoice.query.all())

    return render_template(
        "dashboard.html",
        clients_count=clients_count,
        invoices=invoices,
        total_pending=total_pending,
        total_paid=total_paid,
        user=current_user,
    )
