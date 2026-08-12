from clinic_connect.database import db

class Doctor(db.Model):
    __tablename__ = 'doctors'
    
    doctor_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    clinic_id = db.Column(db.Integer, db.ForeignKey('clinics.clinic_id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=True)
    working_hours_start = db.Column(db.String(10), default='09:00', nullable=False)
    working_hours_end = db.Column(db.String(10), default='17:00', nullable=False)
    availability_status = db.Column(db.String(20), default='Available', nullable=False)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='doctor', cascade='all, delete-orphan', lazy=True)
