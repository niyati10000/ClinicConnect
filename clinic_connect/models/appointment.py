from clinic_connect.database import db

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    appointment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.clinic_id', ondelete='CASCADE'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.doctor_id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.String(10), nullable=False)  # Format: YYYY-MM-DD
    time_slot = db.Column(db.String(10), nullable=False)  # Format: 09:30 AM
    type = db.Column(db.String(50), default='consultation', nullable=True)  # consultation, checkup, emergency
    status = db.Column(db.String(20), default='Scheduled', nullable=False)  # Scheduled, Completed, Cancelled
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    # uselist=False makes it a 1-to-1 relationship
    prescription = db.relationship('Prescription', backref='appointment', uselist=False, cascade='all, delete-orphan')
    invoice = db.relationship('Invoice', backref='appointment', uselist=False, cascade='all, delete-orphan')
