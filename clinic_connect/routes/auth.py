import time
from collections import defaultdict
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from clinic_connect.database import db
from clinic_connect.models import Clinic, AuditLog, SyncLog
from clinic_connect.seeder import seed_demo_clinic

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# ==================== RATE LIMITER (BRUTE FORCE PROTECTION) ====================
# Track failed login attempts: { ip_address: [timestamp1, timestamp2, ...] }
FAILED_LOGIN_ATTEMPTS = defaultdict(list)
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION = 300  # 5 minutes in seconds

def is_rate_limited(ip_address):
    """Check if the requesting IP has exceeded maximum failed login attempts within the window"""
    now = time.time()
    # Prune attempts older than lockout duration
    FAILED_LOGIN_ATTEMPTS[ip_address] = [
        ts for ts in FAILED_LOGIN_ATTEMPTS[ip_address] if now - ts < LOCKOUT_DURATION
    ]
    return len(FAILED_LOGIN_ATTEMPTS[ip_address]) >= MAX_FAILED_ATTEMPTS

def record_failed_attempt(ip_address):
    """Record a failed login attempt timestamp for the given IP"""
    FAILED_LOGIN_ATTEMPTS[ip_address].append(time.time())

def clear_failed_attempts(ip_address):
    """Reset failed attempts upon successful login"""
    if ip_address in FAILED_LOGIN_ATTEMPTS:
        del FAILED_LOGIN_ATTEMPTS[ip_address]

# ==================== LOGIN DECORATORS ====================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'clinic_id' not in session:
            flash('Session expired. Please log in. / कृपया लॉग इन करें।', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def doctor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'clinic_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('active_role') != 'doctor':
            flash('Access Restricted: Doctor mode required. / केवल डॉक्टर एक्सेस कर सकते हैं।', 'error')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

def receptionist_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'clinic_id' not in session:
            return redirect(url_for('auth.login'))
        if session.get('active_role') != 'receptionist':
            flash('Access Restricted: Receptionist mode required. / केवल रिसेप्शनिस्ट एक्सेस कर सकते हैं।', 'error')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== MIDDLEWARE FOR SYNC COUNTS ====================

@auth_bp.app_context_processor
def inject_pending_sync_count():
    if 'clinic_id' in session:
        count = SyncLog.query.filter_by(clinic_id=session['clinic_id'], status='Pending').count()
        session['pending_sync_count'] = count
        return dict(pending_sync_count=count)
    return dict(pending_sync_count=0)

# ==================== ROUTES ====================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'clinic_id' in session:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        client_ip = request.remote_addr or '127.0.0.1'
        
        # 1. Check Rate Limiting
        if is_rate_limited(client_ip):
            flash('Too many failed login attempts! Account access temporarily locked for 5 minutes. / कई असफल प्रयास। कृपया 5 मिनट प्रतीक्षा करें।', 'error')
            return redirect(url_for('auth.login'))
            
        license_code = request.form.get('license_code', '').strip()
        password = request.form.get('password')
        
        # Input length sanitization
        if not license_code or not password or len(license_code) > 100 or len(password) > 200:
            flash('Credentials invalid or empty. / सभी विवरण सही भरें।', 'error')
            return redirect(url_for('auth.login'))
            
        clinic = Clinic.query.filter_by(license_code=license_code).first()
        if clinic and clinic.check_password(password):
            # Clear rate limit history on success
            clear_failed_attempts(client_ip)
            
            # Session Fixation Defense: Reset and reinitialize session
            saved_csrf = session.get('csrf_token')
            session.clear()
            session.permanent = True
            session['csrf_token'] = saved_csrf
            session['clinic_id'] = clinic.clinic_id
            session['clinic_name'] = clinic.name
            session['active_role'] = 'receptionist'
            session['network_status'] = 'online'
            
            # Log action
            log = AuditLog(clinic_id=clinic.clinic_id, action='Login', details='Successful login.')
            db.session.add(log)
            db.session.commit()
            
            return redirect(url_for('dashboard.index'))
        else:
            record_failed_attempt(client_ip)
            attempts_left = MAX_FAILED_ATTEMPTS - len(FAILED_LOGIN_ATTEMPTS[client_ip])
            if attempts_left > 0:
                flash(f'Invalid License Code or Password. {attempts_left} attempt(s) remaining. / अमान्य विवरण।', 'error')
            else:
                flash('Too many failed attempts. Locked out for 5 minutes. / खाता 5 मिनट के लिए लॉक है।', 'error')
            
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'clinic_id' in session:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        license_code = request.form.get('license_code', '').strip()
        password = request.form.get('password')
        address = request.form.get('address', '').strip()
        contact = request.form.get('contact', '').strip()
        email = request.form.get('email', '').strip()
        
        # Validation & Length Limits
        if not name or not license_code or not password:
            flash('Name, License Code, and Password are required! / नाम, लाइसेंस और पासवर्ड आवश्यक हैं।', 'error')
            return redirect(url_for('auth.register'))
            
        if len(name) > 150 or len(license_code) > 100 or len(password) < 4:
            flash('Password must be at least 4 characters; name and license code must be valid. / विवरण मान्य नहीं हैं।', 'error')
            return redirect(url_for('auth.register'))
            
        # Check if license code is taken
        existing = Clinic.query.filter_by(license_code=license_code).first()
        if existing:
            flash('License Code is already registered! / यह लाइसेंस कोड पहले से पंजीकृत है।', 'error')
            return redirect(url_for('auth.register'))
            
        try:
            clinic = Clinic(
                name=name,
                license_code=license_code,
                address=address,
                contact_number=contact,
                email=email
            )
            clinic.set_password(password)
            db.session.add(clinic)
            db.session.commit()
            
            # Auto login new clinic with session fixation protection
            saved_csrf = session.get('csrf_token')
            session.clear()
            session.permanent = True
            session['csrf_token'] = saved_csrf
            session['clinic_id'] = clinic.clinic_id
            session['clinic_name'] = clinic.name
            session['active_role'] = 'receptionist'
            session['network_status'] = 'online'
            
            log = AuditLog(clinic_id=clinic.clinic_id, action='Register Clinic', details='Clinic registered & logged in.')
            db.session.add(log)
            db.session.commit()
            
            flash(f'Account created successfully for {clinic.name}! / खाता सफलतापूर्वक बनाया गया!', 'success')
            return redirect(url_for('dashboard.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'error')
            return redirect(url_for('auth.register'))
            
    return render_template('auth/register.html')

@auth_bp.route('/demo-login', methods=['POST'])
def demo_login():
    try:
        clinic = seed_demo_clinic()
        saved_csrf = session.get('csrf_token')
        session.clear()
        session.permanent = True
        session['csrf_token'] = saved_csrf
        session['clinic_id'] = clinic.clinic_id
        session['clinic_name'] = clinic.name
        session['active_role'] = 'receptionist'
        session['network_status'] = 'online'
        
        log = AuditLog(clinic_id=clinic.clinic_id, action='Demo Login', details='Logged in via Demo Mode.')
        db.session.add(log)
        db.session.commit()
        
        flash('Demo Clinic loaded successfully! / डेमो क्लिनिक लोड हुआ!', 'success')
        return redirect(url_for('dashboard.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'Demo seeding failed: {str(e)}', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    if 'clinic_id' in session:
        log = AuditLog(clinic_id=session['clinic_id'], action='Logout', details='Logged out.')
        db.session.add(log)
        db.session.commit()
        
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/switch-role', methods=['POST'])
@login_required
def switch_role():
    data = request.get_json() or {}
    new_role = data.get('role')
    if new_role in ['receptionist', 'doctor']:
        session['active_role'] = new_role
        
        log = AuditLog(clinic_id=session['clinic_id'], action='Switch Role', details=f'Switched active view to {new_role}.')
        db.session.add(log)
        db.session.commit()
        
        return jsonify({'success': True, 'role': new_role})
    return jsonify({'success': False, 'message': 'Invalid role'}), 400

@auth_bp.route('/toggle-network', methods=['POST'])
@login_required
def toggle_network():
    current_status = session.get('network_status', 'online')
    new_status = 'offline' if current_status == 'online' else 'online'
    session['network_status'] = new_status
    
    log = AuditLog(clinic_id=session['clinic_id'], action='Toggle Network', details=f'Network connectivity status set to {new_status}.')
    db.session.add(log)
    db.session.commit()
    
    return jsonify({'success': True, 'status': new_status})
