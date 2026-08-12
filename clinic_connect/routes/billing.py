from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from clinic_connect.database import db
from clinic_connect.routes.auth import login_required, receptionist_required
from clinic_connect.models import Invoice, AuditLog

billing_bp = Blueprint('billing', __name__, url_prefix='/billing')

@billing_bp.route('/')
@login_required
@receptionist_required
def index():
    clinic_id = session['clinic_id']
    invoices = Invoice.query.filter_by(clinic_id=clinic_id).order_by(Invoice.created_at.desc()).all()
    
    # Calculate simple financial stats for billing bento cards
    total_revenue = sum(inv.total_amount for inv in invoices if inv.status == 'Paid')
    pending_revenue = sum(inv.total_amount for inv in invoices if inv.status == 'Pending')
    paid_count = sum(1 for inv in invoices if inv.status == 'Paid')
    pending_count = sum(1 for inv in invoices if inv.status == 'Pending')
    
    return render_template('billing/list.html', 
                           invoices=invoices, 
                           total_revenue=total_revenue,
                           pending_revenue=pending_revenue,
                           paid_count=paid_count,
                           pending_count=pending_count)

@billing_bp.route('/pay/<int:invoice_id>', methods=['POST'])
@login_required
@receptionist_required
def record_payment(invoice_id):
    clinic_id = session['clinic_id']
    invoice = Invoice.query.filter_by(invoice_id=invoice_id, clinic_id=clinic_id).first_or_404()
    
    if invoice.status == 'Paid':
        flash('Invoice is already paid! / इनवॉइस का भुगतान पहले ही हो चुका है।', 'warning')
        return redirect(url_for('billing.index'))
        
    try:
        invoice.status = 'Paid'
        
        # Audit Log
        log = AuditLog(
            clinic_id=clinic_id,
            action='Record Payment',
            details=f'Recorded payment of ₹{invoice.total_amount} for Invoice #{invoice.invoice_id} (Patient: {invoice.patient.name}).'
        )
        db.session.add(log)
        db.session.commit()
        
        flash(f'Payment of ₹{invoice.total_amount} recorded successfully! / भुगतान सफलतापूर्वक दर्ज हुआ!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Payment record failed: {str(e)}', 'error')
        
    return redirect(url_for('billing.index'))

@billing_bp.route('/print/<int:invoice_id>')
@login_required
def print_invoice(invoice_id):
    clinic_id = session['clinic_id']
    # Security check
    invoice = Invoice.query.filter_by(invoice_id=invoice_id, clinic_id=clinic_id).first_or_404()
    return render_template('billing/print.html', invoice=invoice)
