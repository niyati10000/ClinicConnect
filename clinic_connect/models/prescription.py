from datetime import datetime
from clinic_connect.database import db

class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    
    prescription_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.appointment_id', ondelete='CASCADE'), unique=True, nullable=False)
    symptoms = db.Column(db.Text, nullable=True)
    diagnosis = db.Column(db.Text, nullable=True)
    medicine_details = db.Column(db.Text, nullable=True)  # JSON-encoded array of prescribed drugs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
