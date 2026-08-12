from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from clinic_connect.database import db
from clinic_connect.routes.auth import login_required
from clinic_connect.models import Patient, Appointment, Prescription, AuditLog

patients_bp = Blueprint('patients', __name__, url_prefix='/patients')

@patients_bp.route('/')
@login_required
def index():
    clinic_id = session['clinic_id']
    query = request.args.get('q', '').strip()
    
    if query:
        # Search by name or contact number
        patients = Patient.query.filter(
            Patient.clinic_id == clinic_id,
            (Patient.name.like(f"%{query}%")) | (Patient.contact_number.like(f"%{query}%"))
        ).order_by(Patient.registration_date.desc()).all()
    else:
        patients = Patient.query.filter_by(clinic_id=clinic_id).order_by(Patient.registration_date.desc()).all()
        
    return render_template('patients/list.html', patients=patients, query=query)

@patients_bp.route('/register', methods=['GET', 'POST'])
@login_required
def register():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age = request.form.get('age')
        gender = request.form.get('gender')
        contact = request.form.get('contact', '').strip()
        issue = request.form.get('issue', '').strip()
        
        # Validations
        if not name or not contact:
            flash('Name and Contact Number are required fields! / नाम और संपर्क आवश्यक हैं।', 'error')
            return redirect(url_for('patients.register'))
            
        try:
            clinic_id = session['clinic_id']
            patient = Patient(
                clinic_id=clinic_id,
                name=name,
                age=int(age) if age else None,
                gender=gender,
                contact_number=contact,
                health_issue=issue
            )
            db.session.add(patient)
            db.session.commit()
            
            # Audit log
            log = AuditLog(
                clinic_id=clinic_id,
                action='Register Patient',
                details=f'Registered new patient {name} (ID: {patient.patient_id}).'
            )
            db.session.add(log)
            db.session.commit()
            
            flash(f'Patient registered successfully! ID: {patient.patient_id} / रोगी पंजीकरण सफल!', 'success')
            
            # Check if they want to book an appointment immediately
            if request.form.get('book_now') == 'yes':
                return redirect(url_for('appointments.book', patient_id=patient.patient_id))
                
            return redirect(url_for('patients.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Registration failed: {str(e)}', 'error')
            return redirect(url_for('patients.register'))
            
    return render_template('patients/register.html')

@patients_bp.route('/<int:patient_id>')
@login_required
def details(patient_id):
    clinic_id = session['clinic_id']
    
    # Security: IDOR prevention (verify clinic ownership)
    patient = Patient.query.filter_by(patient_id=patient_id, clinic_id=clinic_id).first_or_404()
    
    # Load patient appointments
    appointments = Appointment.query.filter_by(patient_id=patient_id).order_by(Appointment.date.desc(), Appointment.time_slot.desc()).all()
    
    # Vitals history processing for visual charts/sparklines
    vitals_history = []
    for appt in appointments:
        if appt.prescription and appt.prescription.symptoms:
            try:
                # Try parsing symptoms for vital indicators
                symptom_str = appt.prescription.symptoms
                # Vitals format: "BP: 120/80, HR: 72 bpm, Temp: 98.6 F, Wt: 70 kg"
                # Let's write a simple parser to display it elegantly
                bp = "N/A"
                hr = "N/A"
                temp = "N/A"
                weight = "N/A"
                
                parts = [p.strip() for p in symptom_str.split('|') if '|' in symptom_str]
                if parts and len(parts) >= 2:
                    # Format: Vitals: BP: 120/80 | HR: 72 | Temp: 98.6 | Wt: 70 || Symptoms: cough
                    vitals_part = parts[0]
                    for item in vitals_part.split(','):
                        if 'BP:' in item: bp = item.replace('BP:', '').strip()
                        elif 'HR:' in item: hr = item.replace('HR:', '').strip()
                        elif 'Temp:' in item: temp = item.replace('Temp:', '').strip()
                        elif 'Wt:' in item: weight = item.replace('Wt:', '').strip()
                
                if bp != "N/A" or hr != "N/A":
                    vitals_history.append({
                        'date': appt.date,
                        'bp': bp,
                        'hr': hr,
                        'temp': temp,
                        'weight': weight
                    })
            except Exception:
                pass
                
    return render_template('patients/details.html', patient=patient, appointments=appointments, vitals_history=vitals_history)
