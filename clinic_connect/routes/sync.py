from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from datetime import datetime
from clinic_connect.database import db
from clinic_connect.routes.auth import login_required, receptionist_required
from clinic_connect.models import SyncLog, AuditLog

sync_bp = Blueprint('sync', __name__, url_prefix='/sync')

@sync_bp.route('/')
@login_required
@receptionist_required
def index():
    clinic_id = session['clinic_id']
    logs = SyncLog.query.filter_by(clinic_id=clinic_id).order_by(SyncLog.created_at.desc()).all()
    
    # Summary stats
    pending_count = sum(1 for log in logs if log.status == 'Pending')
    sent_count = sum(1 for log in logs if log.status == 'Sent')
    
    return render_template('sync/list.html', logs=logs, pending_count=pending_count, sent_count=sent_count)

@sync_bp.route('/execute', methods=['POST'])
@login_required
@receptionist_required
def execute_sync():
    clinic_id = session['clinic_id']
    
    # Verify network connectivity status
    if session.get('network_status') == 'offline':
        return jsonify({
            'success': False, 
            'message': 'Cannot synchronize: Connection is offline. Toggle status to Online first. / नेटवर्क ऑफ़लाइन है।'
        }), 400
        
    try:
        # Load pending logs
        pending = SyncLog.query.filter_by(clinic_id=clinic_id, status='Pending').all()
        synced_count = len(pending)
        
        for log in pending:
            # Simulate Twilio SMS gateway delay/execution
            # (In production, this would call twilio_client.messages.create)
            log.status = 'Sent'
            log.synced_at = datetime.utcnow()
            
        if synced_count > 0:
            # Audit Log entry
            audit = AuditLog(
                clinic_id=clinic_id,
                action='Sync Notifications',
                details=f'Successfully synchronized {synced_count} pending SMS notifications to gateway.'
            )
            db.session.add(audit)
            db.session.commit()
            
            # Recalculate global pending badges in session
            session['pending_sync_count'] = 0
            
        return jsonify({
            'success': True,
            'synced_count': synced_count,
            'message': f'Successfully synchronized {synced_count} message(s)! / सिंक सफल!'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Synchronization failed: {str(e)}'
        }), 500
