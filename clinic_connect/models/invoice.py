from datetime import datetime
from clinic_connect.database import db

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    invoice_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.clinic_id', ondelete='CASCADE'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id', ondelete='CASCADE'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.appointment_id', ondelete='CASCADE'), unique=True, nullable=False)
    consultation_fee = db.Column(db.Float, default=0.0, nullable=False)
    medicine_fee = db.Column(db.Float, default=0.0, nullable=False)
    total_amount = db.Column(db.Float, default=0.0, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)  # Pending, Paid
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
