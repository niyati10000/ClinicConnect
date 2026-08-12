from datetime import datetime
from clinic_connect.database import db

class SyncLog(db.Model):
    __tablename__ = 'sync_logs'
    
    log_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.clinic_id', ondelete='CASCADE'), nullable=False)
    recipient = db.Column(db.String(20), nullable=False)
    message_body = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)  # Pending, Sent, Failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    synced_at = db.Column(db.DateTime, nullable=True)
