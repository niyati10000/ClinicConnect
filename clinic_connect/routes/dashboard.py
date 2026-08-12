from flask import Blueprint, render_template, session, jsonify, redirect, url_for
from datetime import datetime, date, timedelta
from sqlalchemy import func
from clinic_connect.database import db
from clinic_connect.routes.auth import login_required
from clinic_connect.models import Patient, Doctor, Appointment, Prescription, Invoice

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    return render_template('dashboard.html')

@dashboard_bp.route('/api/stats')
@login_required
def get_stats():
    clinic_id = session['clinic_id']
    
    # 1. Total Patients
    total_patients = Patient.query.filter_by(clinic_id=clinic_id).count()
    
    # 2. Available Doctors
    available_doctors = Doctor.query.filter_by(clinic_id=clinic_id, availability_status='Available').count()
    
    # 3. Today's Appointments
    today_str = datetime.now().strftime('%Y-%m-%d')
    today_appointments = Appointment.query.filter_by(clinic_id=clinic_id, date=today_str).count()
    
    return jsonify({
        'patients': total_patients,
        'doctors': available_doctors,
        'appointments': today_appointments
    })

@dashboard_bp.route('/api/analytics-data')
@login_required
def get_analytics_data():
    clinic_id = session['clinic_id']
    
    # 1. Patient Registrations (last 10 days)
    ten_days_ago = date.today() - timedelta(days=10)
    reg_stats = db.session.query(
        Patient.registration_date, 
        func.count(Patient.patient_id)
    ).filter(
        Patient.clinic_id == clinic_id,
        Patient.registration_date >= ten_days_ago
    ).group_by(
        Patient.registration_date
    ).order_by(
        Patient.registration_date.asc()
    ).all()
    
    reg_labels = [r[0].strftime('%b %d') for r in reg_stats]
    reg_counts = [r[1] for r in reg_stats]

    # Fallback to empty display if no registrations exist
    if not reg_stats:
        reg_labels = ['No Data']
        reg_counts = [0]
        
    # 2. Doctor Workload (Appointments per Doctor)
    workload = db.session.query(
        Doctor.name,
        func.count(Appointment.appointment_id)
    ).join(
        Appointment, Doctor.doctor_id == Appointment.doctor_id
    ).filter(
        Doctor.clinic_id == clinic_id
    ).group_by(
        Doctor.name
    ).all()
    
    doc_labels = [w[0] for w in workload]
    doc_counts = [w[1] for w in workload]
    
    # 3. Appointment Status Distribution
    status_stats = db.session.query(
        Appointment.status,
        func.count(Appointment.appointment_id)
    ).filter(
        Appointment.clinic_id == clinic_id
    ).group_by(
        Appointment.status
    ).all()
    
    status_labels = [s[0] for s in status_stats]
    status_counts = [s[1] for s in status_stats]
    
    # 4. Top Diagnoses (Common health issues)
    diagnoses = db.session.query(
        Prescription.diagnosis,
        func.count(Prescription.prescription_id)
    ).join(
        Appointment, Prescription.appointment_id == Appointment.appointment_id
    ).filter(
        Appointment.clinic_id == clinic_id,
        Prescription.diagnosis != None,
        Prescription.diagnosis != ''
    ).group_by(
        Prescription.diagnosis
    ).order_by(
        func.count(Prescription.prescription_id).desc()
    ).limit(5).all()
    
    diag_labels = [d[0] for d in diagnoses]
    diag_counts = [d[1] for d in diagnoses]
    
    return jsonify({
        'registrations': {
            'labels': reg_labels,
            'data': reg_counts
        },
        'workload': {
            'labels': doc_labels,
            'data': doc_counts
        },
        'status': {
            'labels': status_labels,
            'data': status_counts
        },
        'diagnoses': {
            'labels': diag_labels,
            'data': diag_counts
        }
    })

@dashboard_bp.route('/api/docs')
@login_required
def api_docs():
    return render_template('api_docs.html')

