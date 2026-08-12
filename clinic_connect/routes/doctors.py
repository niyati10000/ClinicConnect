import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from clinic_connect.database import db
from clinic_connect.routes.auth import login_required, doctor_required
from clinic_connect.models import Doctor, Appointment, Prescription, Patient, Inventory, Invoice, AuditLog

doctors_bp = Blueprint('doctors', __name__, url_prefix='/doctors')

@doctors_bp.route('/')
@login_required
def index():
    clinic_id = session['clinic_id']
    doctors = Doctor.query.filter_by(clinic_id=clinic_id).all()
    return render_template('doctors/list.html', doctors=doctors)

@doctors_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    # Allow registering new doctors
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        spec = request.form.get('specialization', '').strip()
        start = request.form.get('working_hours_start', '09:00')
        end = request.form.get('working_hours_end', '17:00')
        
        if not name:
            flash('Doctor Name is required! / डॉक्टर का नाम आवश्यक है।', 'error')
            return redirect(url_for('doctors.add'))
            
        try:
            clinic_id = session['clinic_id']
            doc = Doctor(
                clinic_id=clinic_id,
                name=name,
                specialization=spec,
                working_hours_start=start,
                working_hours_end=end,
                availability_status='Available'
            )
            db.session.add(doc)
            db.session.commit()
            
            # Audit log
            log = AuditLog(
                clinic_id=clinic_id,
                action='Add Doctor',
                details=f'Added new doctor {name} ({spec}).'
            )
            db.session.add(log)
            db.session.commit()
            
            flash(f'Doctor {name} added successfully! / डॉक्टर पंजीकरण सफल!', 'success')
            return redirect(url_for('doctors.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to add doctor: {str(e)}', 'error')
            return redirect(url_for('doctors.add'))
            
    return render_template('doctors/add.html')

@doctors_bp.route('/toggle-status/<int:doctor_id>', methods=['POST'])
@login_required
def toggle_status(doctor_id):
    clinic_id = session['clinic_id']
    doctor = Doctor.query.filter_by(doctor_id=doctor_id, clinic_id=clinic_id).first_or_404()
    
    current_status = doctor.availability_status
    new_status = 'Away' if current_status == 'Available' else 'Available'
    doctor.availability_status = new_status
    
    # Audit log
    log = AuditLog(
        clinic_id=clinic_id,
        action='Toggle Doctor Availability',
        details=f'Set {doctor.name} status to {new_status}.'
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f'{doctor.name} is now marked as {new_status}.', 'success')
    return redirect(url_for('doctors.index'))

@doctors_bp.route('/consultation/<int:appointment_id>', methods=['GET', 'POST'])
@doctor_required
def consultation(appointment_id):
    clinic_id = session['clinic_id']
    
    # Security: Verify ownership
    appt = Appointment.query.filter_by(appointment_id=appointment_id, clinic_id=clinic_id).first_or_404()
    patient = appt.patient
    
    # Check if already completed
    if appt.status == 'Completed':
        flash('This consultation has already been completed. / यह परामर्श पहले ही पूरा हो चुका है।', 'warning')
        return redirect(url_for('patients.details', patient_id=patient.patient_id))
        
    if request.method == 'POST':
        bp = request.form.get('bp', '').strip()
        hr = request.form.get('hr', '').strip()
        temp = request.form.get('temp', '').strip()
        weight = request.form.get('weight', '').strip()
        symptoms_desc = request.form.get('symptoms', '').strip()
        diagnosis = request.form.get('diagnosis', '').strip()
        
        # Parse medications from dynamically submitted form arrays
        drug_names = request.form.getlist('med_name[]')
        dosages = request.form.getlist('med_dosage[]')
        frequencies = request.form.getlist('med_frequency[]')
        durations = request.form.getlist('med_duration[]')
        
        meds_list = []
        med_cost = 0.0
        
        for i in range(len(drug_names)):
            d_name = drug_names[i].strip()
            if not d_name:
                continue
                
            dosage = dosages[i].strip() if i < len(dosages) else ''
            freq = frequencies[i].strip() if i < len(frequencies) else ''
            dur = durations[i].strip() if i < len(durations) else ''
            
            meds_list.append({
                'name': d_name,
                'dosage': dosage,
                'frequency': freq,
                'duration': dur
            })
            
            # Deduct stock if drug is found in Inventory & calculate billing
            # We look for a match in inventory
            inv_item = Inventory.query.filter(
                Inventory.clinic_id == clinic_id,
                Inventory.name.like(f"%{d_name}%")
            ).first()
            
            if inv_item:
                # Estimate total quantity to deduct
                # Duration parsed for digits: e.g. "5 days" -> 5. Frequency: e.g. "3 times daily" -> 3. Total = 15.
                qty = 1
                try:
                    dur_digits = ''.join(c for c in dur if c.isdigit())
                    duration_val = int(dur_digits) if dur_digits else 1
                    
                    freq_val = 1
                    if 'twice' in freq.lower() or '2 times' in freq.lower(): freq_val = 2
                    elif 'thrice' in freq.lower() or '3 times' in freq.lower(): freq_val = 3
                    elif 'four' in freq.lower() or '4 times' in freq.lower(): freq_val = 4
                    
                    qty = duration_val * freq_val
                except Exception:
                    qty = 1
                
                # Update inventory quantity
                old_qty = inv_item.stock_quantity
                new_qty = max(0, old_qty - qty)
                inv_item.stock_quantity = new_qty
                
                # Update Billing cost
                med_cost += qty * inv_item.unit_price
                
        # Format vitals & symptoms: "BP: 120/80, HR: 72, Temp: 98.6, Wt: 70 || Symptoms: high fever"
        vitals_formatted = f"BP: {bp or 'N/A'}, HR: {hr or 'N/A'}, Temp: {temp or 'N/A'}, Wt: {weight or 'N/A'}"
        symptoms_payload = f"{vitals_formatted} || {symptoms_desc}"
        
        try:
            # Create prescription
            prescription = Prescription(
                appointment_id=appt.appointment_id,
                symptoms=symptoms_payload,
                diagnosis=diagnosis,
                medicine_details=json.dumps(meds_list)
            )
            db.session.add(prescription)
            
            # Create itemized invoice
            consultation_fee = 300.0 # Standard local doctor fee
            invoice = Invoice(
                clinic_id=clinic_id,
                patient_id=patient.patient_id,
                appointment_id=appt.appointment_id,
                consultation_fee=consultation_fee,
                medicine_fee=med_cost,
                total_amount=consultation_fee + med_cost,
                status='Pending'
            )
            db.session.add(invoice)
            
            # Mark appointment Completed
            appt.status = 'Completed'
            
            # Audit log
            log = AuditLog(
                clinic_id=clinic_id,
                action='Complete Consultation',
                details=f'Completed consultation for appointment #{appt.appointment_id}. Created prescription and invoice.'
            )
            db.session.add(log)
            db.session.commit()
            
            flash('Consultation notes saved successfully! Invoice generated. / परामर्श नोट्स सहेजे गए!', 'success')
            return redirect(url_for('patients.details', patient_id=patient.patient_id))
        except Exception as e:
            db.session.rollback()
            flash(f'Consultation save failed: {str(e)}', 'error')
            return redirect(url_for('doctors.consultation', appointment_id=appt.appointment_id))
            
    # Load patient active inventory options for the autocomplete helper
    med_choices = [item.name for item in Inventory.query.filter_by(clinic_id=clinic_id).all()]
            
    return render_template('doctors/consultation.html', appt=appt, patient=patient, med_choices=med_choices)

@doctors_bp.route('/print-prescription/<int:appointment_id>')
@login_required
def print_prescription(appointment_id):
    clinic_id = session['clinic_id']
    appt = Appointment.query.filter_by(appointment_id=appointment_id, clinic_id=clinic_id).first_or_404()
    
    if not appt.prescription:
        flash('No prescription details available for this appointment. / पर्चा उपलब्ध नहीं है।', 'error')
        return redirect(url_for('patients.details', patient_id=appt.patient_id))
        
    return render_template('doctors/prescription_print.html', appt=appt)
