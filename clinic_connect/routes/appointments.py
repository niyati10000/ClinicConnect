from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime
from clinic_connect.database import db
from clinic_connect.routes.auth import login_required, receptionist_required
from clinic_connect.models import Appointment, Patient, Doctor, SyncLog, AuditLog

appointments_bp = Blueprint('appointments', __name__, url_prefix='/appointments')

# Standard time slots for clinic doctors
PRESET_SLOTS = [
    "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM", 
    "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM", 
    "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM", 
    "04:00 PM", "04:30 PM"
]

@appointments_bp.route('/')
@login_required
def index():
    clinic_id = session['clinic_id']
    appointments = Appointment.query.filter_by(clinic_id=clinic_id)\
        .order_by(Appointment.date.desc(), Appointment.time_slot.desc()).all()
    return render_template('appointments/list.html', appointments=appointments)

@appointments_bp.route('/api/available-slots')
@login_required
def get_available_slots():
    clinic_id = session['clinic_id']
    doctor_id = request.args.get('doctor_id', type=int)
    date_str = request.args.get('date', '').strip()
    
    if not doctor_id or not date_str:
        return jsonify({'error': 'Missing parameters'}), 400
        
    # Verify doctor belongs to the clinic
    doctor = Doctor.query.filter_by(doctor_id=doctor_id, clinic_id=clinic_id).first_or_404()
    
    # Query booked slots (excluding cancelled ones)
    booked = Appointment.query.filter(
        Appointment.clinic_id == clinic_id,
        Appointment.doctor_id == doctor_id,
        Appointment.date == date_str,
        Appointment.status.in_(['Scheduled', 'Completed'])
    ).all()
    
    booked_slots = [a.time_slot for a in booked]
    
    slots_data = []
    for slot in PRESET_SLOTS:
        # Check doctor working hours
        # E.g. Dr. Vikram works 09:00 to 15:00. 04:00 PM would be out of bounds.
        # We can implement a simple bounds checker
        is_within_hours = True
        try:
            slot_time = datetime.strptime(slot, "%I:%M %p").time()
            start_time = datetime.strptime(doctor.working_hours_start, "%H:%M").time()
            end_time = datetime.strptime(doctor.working_hours_end, "%H:%M").time()
            is_within_hours = start_time <= slot_time <= end_time
        except Exception:
            pass
            
        slots_data.append({
            'time': slot,
            'available': is_within_hours and (slot not in booked_slots)
        })
        
    return jsonify({'slots': slots_data})

@appointments_bp.route('/book', methods=['GET', 'POST'])
@receptionist_required
def book():
    clinic_id = session['clinic_id']
    
    if request.method == 'POST':
        patient_id = request.form.get('patient_id', type=int)
        doctor_id = request.form.get('doctor_id', type=int)
        date_str = request.form.get('date')
        time_slot = request.form.get('time_slot')
        appt_type = request.form.get('type', 'consultation')
        notes = request.form.get('notes', '').strip()
        
        if not patient_id or not doctor_id or not date_str or not time_slot:
            flash('All booking fields are required! / सभी विवरण आवश्यक हैं।', 'error')
            return redirect(url_for('appointments.book', patient_id=patient_id))
            
        # Security: Verify ownership of patient and doctor
        patient = Patient.query.filter_by(patient_id=patient_id, clinic_id=clinic_id).first_or_404()
        doctor = Doctor.query.filter_by(doctor_id=doctor_id, clinic_id=clinic_id).first_or_404()
        
        # Backend double-booking conflict detection
        conflict = Appointment.query.filter(
            Appointment.clinic_id == clinic_id,
            Appointment.doctor_id == doctor_id,
            Appointment.date == date_str,
            Appointment.time_slot == time_slot,
            Appointment.status.in_(['Scheduled', 'Completed'])
        ).first()
        
        if conflict:
            flash('Conflict: This slot is already booked for this doctor! / संघर्ष: यह स्लॉट पहले से ही बुक है।', 'error')
            return redirect(url_for('appointments.book', patient_id=patient_id))
            
        try:
            appt = Appointment(
                clinic_id=clinic_id,
                patient_id=patient_id,
                doctor_id=doctor_id,
                date=date_str,
                time_slot=time_slot,
                type=appt_type,
                status='Scheduled',
                notes=notes
            )
            db.session.add(appt)
            db.session.commit()
            
            # Setup SMS details
            recipient = patient.contact_number
            msg = f"Dear {patient.name}, your appointment with {doctor.name} at {session.get('clinic_name')} is scheduled for {date_str} at {time_slot}."
            
            # Send/Queue Notification based on network toggle
            is_offline = session.get('network_status') == 'offline'
            status = 'Pending' if is_offline else 'Sent'
            
            sync_log = SyncLog(
                clinic_id=clinic_id,
                recipient=recipient,
                message_body=msg,
                status=status
            )
            if not is_offline:
                sync_log.synced_at = datetime.utcnow()
                
            db.session.add(sync_log)
            
            # Audit Log
            audit = AuditLog(
                clinic_id=clinic_id,
                action='Book Appointment',
                details=f'Booked appointment #{appt.appointment_id} for Patient {patient.name} with {doctor.name} on {date_str} at {time_slot}. SMS status: {status}.'
            )
            db.session.add(audit)
            db.session.commit()
            
            if is_offline:
                flash(f'Appointment booked successfully! System is offline; notification queued. ID: {appt.appointment_id} / अपॉइंटमेंट बुक हो गया, एसएमएस कतार में है।', 'success')
            else:
                flash(f'Appointment booked successfully! SMS confirmation sent. ID: {appt.appointment_id} / अपॉइंटमेंट बुकिंग सफल!', 'success')
                
            return redirect(url_for('appointments.index'))
        except Exception as e:
            db.session.rollback()
            flash(f'Booking failed: {str(e)}', 'error')
            return redirect(url_for('appointments.book', patient_id=patient_id))
            
    # GET view prefill
    prefill_patient_id = request.args.get('patient_id', type=int)
    
    patients = Patient.query.filter_by(clinic_id=clinic_id).order_by(Patient.name.asc()).all()
    doctors = Doctor.query.filter_by(clinic_id=clinic_id, availability_status='Available').order_by(Doctor.name.asc()).all()
    
    return render_template('appointments/book.html', patients=patients, doctors=doctors, prefill_patient_id=prefill_patient_id)

@appointments_bp.route('/cancel/<int:appointment_id>', methods=['POST'])
@receptionist_required
def cancel(appointment_id):
    clinic_id = session['clinic_id']
    appt = Appointment.query.filter_by(appointment_id=appointment_id, clinic_id=clinic_id).first_or_404()
    
    if appt.status != 'Scheduled':
        flash('Only Scheduled appointments can be cancelled. / केवल निर्धारित अपॉइंटमेंट रद्द किए जा सकते हैं।', 'warning')
        return redirect(url_for('appointments.index'))
        
    try:
        appt.status = 'Cancelled'
        
        # Setup SMS Cancellation details
        patient = appt.patient
        recipient = patient.contact_number
        msg = f"Dear {patient.name}, your appointment with {appt.doctor.name} on {appt.date} at {appt.time_slot} has been CANCELLED."
        
        is_offline = session.get('network_status') == 'offline'
        status = 'Pending' if is_offline else 'Sent'
        
        sync_log = SyncLog(
            clinic_id=clinic_id,
            recipient=recipient,
            message_body=msg,
            status=status
        )
        if not is_offline:
            sync_log.synced_at = datetime.utcnow()
            
        db.session.add(sync_log)
        
        # Audit Log
        audit = AuditLog(
            clinic_id=clinic_id,
            action='Cancel Appointment',
            details=f'Cancelled appointment #{appt.appointment_id} for Patient {patient.name}. SMS status: {status}.'
        )
        db.session.add(audit)
        db.session.commit()
        
        flash('Appointment cancelled successfully! / अपॉइंटमेंट रद्द कर दिया गया!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Cancellation failed: {str(e)}', 'error')
        
    return redirect(url_for('appointments.index'))
