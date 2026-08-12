from datetime import datetime
from clinic_connect.database import db
from werkzeug.security import generate_password_hash, check_password_hash

class Clinic(db.Model):
    __tablename__ = 'clinics'
    
    clinic_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    license_code = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    contact_number = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships for cascade deletion and easy querying
    patients = db.relationship('Patient', backref='clinic', cascade='all, delete-orphan', lazy=True)
    doctors = db.relationship('Doctor', backref='clinic', cascade='all, delete-orphan', lazy=True)
    appointments = db.relationship('Appointment', backref='clinic', cascade='all, delete-orphan', lazy=True)
    sync_logs = db.relationship('SyncLog', backref='clinic', cascade='all, delete-orphan', lazy=True)
    inventory = db.relationship('Inventory', backref='clinic', cascade='all, delete-orphan', lazy=True)
    invoices = db.relationship('Invoice', backref='clinic', cascade='all, delete-orphan', lazy=True)
    audit_logs = db.relationship('AuditLog', backref='clinic', cascade='all, delete-orphan', lazy=True)

    def set_password(self, password):
        """Secure PBKDF2 hashing"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password hash"""
        return check_password_hash(self.password_hash, password)
