from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from clinic_connect.database import db
from clinic_connect.routes.auth import login_required
from clinic_connect.models import Inventory, AuditLog

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory_bp.route('/')
@login_required
def index():
    clinic_id = session['clinic_id']
    items = Inventory.query.filter_by(clinic_id=clinic_id).all()
    
    # Calculate simple alert statistics
    alert_count = sum(1 for item in items if item.stock_quantity <= item.min_threshold)
    total_distinct_items = len(items)
    
    return render_template('inventory/list.html', 
                           items=items, 
                           alert_count=alert_count, 
                           total_distinct_items=total_distinct_items)

@inventory_bp.route('/add', methods=['POST'])
@login_required
def add_item():
    clinic_id = session['clinic_id']
    name = request.form.get('name', '').strip()
    qty = request.form.get('stock_quantity', type=int, default=0)
    price = request.form.get('unit_price', type=float, default=0.0)
    threshold = request.form.get('min_threshold', type=int, default=10)
    
    if not name:
        flash('Medicine name is required! / दवा का नाम आवश्यक है।', 'error')
        return redirect(url_for('inventory.index'))
        
    try:
        item = Inventory(
            clinic_id=clinic_id,
            name=name,
            stock_quantity=qty,
            unit_price=price,
            min_threshold=threshold
        )
        db.session.add(item)
        
        # Audit Log
        log = AuditLog(
            clinic_id=clinic_id,
            action='Add Inventory Item',
            details=f'Added new medicine {name} with quantity {qty} (threshold: {threshold}) to stock.'
        )
        db.session.add(log)
        db.session.commit()
        
        flash(f'Medicine {name} registered in stock! / दवा स्टॉक में दर्ज की गई!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Failed to add item: {str(e)}', 'error')
        
    return redirect(url_for('inventory.index'))

@inventory_bp.route('/update-stock/<int:item_id>', methods=['POST'])
@login_required
def update_stock(item_id):
    clinic_id = session['clinic_id']
    item = Inventory.query.filter_by(item_id=item_id, clinic_id=clinic_id).first_or_404()
    
    qty = request.form.get('stock_quantity', type=int)
    price = request.form.get('unit_price', type=float)
    
    if qty is None or price is None:
        flash('All values must be filled. / सभी मूल्य भरें।', 'error')
        return redirect(url_for('inventory.index'))
        
    try:
        old_qty = item.stock_quantity
        item.stock_quantity = qty
        item.unit_price = price
        
        # Audit Log
        log = AuditLog(
            clinic_id=clinic_id,
            action='Update Inventory Stock',
            details=f'Updated stock levels for {item.name}. Quantity: {old_qty} -> {qty}. Price: ₹{price}.'
        )
        db.session.add(log)
        db.session.commit()
        
        flash(f'Stock for {item.name} updated successfully! / स्टॉक अपडेट सफल!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Update failed: {str(e)}', 'error')
        
    return redirect(url_for('inventory.index'))
