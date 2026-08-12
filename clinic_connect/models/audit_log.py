from datetime import datetime
from clinic_connect.database import db

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.clinic_id', ondelete='CASCADE'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
