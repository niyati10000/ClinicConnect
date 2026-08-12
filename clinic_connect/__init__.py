import os
import json
import secrets
from flask import Flask, render_template, session, request, abort
from werkzeug.middleware.proxy_fix import ProxyFix
from clinic_connect.config import Config
from clinic_connect.database import db

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Apply ProxyFix to accurately read client IPs and HTTPS proto behind reverse proxies
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    
    # Initialize DB Context
    db.init_app(app)
    
    # Custom Jinja2 context functions & filters
    app.jinja_env.globals.update(len=len)
    
    @app.template_filter('loads')
    def loads_filter(s):
        try:
            return json.loads(s) if s else []
        except Exception:
            return []
            
    # Inject CSRF token into all templates
    @app.context_processor
    def inject_csrf_token():
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(32)
        return dict(csrf_token=session['csrf_token'])
        
    # ==================== CSRF DEFENSE MIDDLEWARE ====================
    
    @app.before_request
    def validate_csrf():
        # Ensure session has a CSRF token
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(32)
            
        # Skip validation during automated testing or if disabled
        if app.config.get('TESTING') or not app.config.get('WTF_CSRF_ENABLED', True):
            return
            
        # Only validate state-modifying HTTP methods
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            # Allow JSON API endpoints that authenticate via existing session state
            if request.is_json:
                return
                
            sent_token = request.form.get('csrf_token') or request.headers.get('X-CSRFToken')
            expected_token = session.get('csrf_token')
            
            if not sent_token or not expected_token or not secrets.compare_digest(sent_token, expected_token):
                # 403 Forbidden on CSRF token mismatch
                abort(403)
            
    # Register Blueprints
    from clinic_connect.routes.auth import auth_bp
    from clinic_connect.routes.dashboard import dashboard_bp
    from clinic_connect.routes.patients import patients_bp
    from clinic_connect.routes.doctors import doctors_bp
    from clinic_connect.routes.appointments import appointments_bp
    from clinic_connect.routes.billing import billing_bp
    from clinic_connect.routes.inventory import inventory_bp
    from clinic_connect.routes.sync import sync_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(patients_bp)
    app.register_blueprint(doctors_bp)
    app.register_blueprint(appointments_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(inventory_bp)
    app.register_blueprint(sync_bp)
    
    # ==================== SECURITY HEADERS MIDDLEWARE ====================
    
    @app.after_request
    def apply_security_headers(response):
        """Mitigates XSS, Clickjacking, and MIME sniffing attacks"""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com; "
            "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https://github.com https://user-attachments.githubusercontent.com;"
        )
        return response
        
    # ==================== ERROR HANDLERS (Information Leakage Mitigation) ====================
    
    @app.errorhandler(403)
    def handle_forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def handle_not_found(e):
        return render_template('errors/404.html'), 404
        
    @app.errorhandler(500)
    def handle_server_error(e):
        # We roll back session to clean state on failure
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # Self-initialize tables on startup
    with app.app_context():
        db.create_all()
        
    return app
