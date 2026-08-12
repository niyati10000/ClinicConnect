from datetime import date
from clinic_connect.database import db

class Patient(db.Model):
    __tablename__ = 'patients'
    
    patient_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.clinic_id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=True)
    gender = db.Column(db.String(20), nullable=True)
    contact_number = db.Column(db.String(20), nullable=False)
    health_issue = db.Column(db.Text, nullable=True)
    registration_date = db.Column(db.Date, default=date.today)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='patient', cascade='all, delete-orphan', lazy=True)
    invoices = db.relationship('Invoice', backref='patient', cascade='all, delete-orphan', lazy=True)
