import json
from clinic_connect.database import db
from clinic_connect.models import Clinic, Patient, Doctor, Appointment, Prescription, Inventory, Invoice, SyncLog

def test_multi_tenancy_isolation(app, client):
    """Verify that Clinic A cannot retrieve or query Clinic B records"""
    with app.app_context():
        # Create Clinic A
        clinic_a = Clinic(name='Clinic A', license_code='code-a', password_hash='hash')
        # Create Clinic B
        clinic_b = Clinic(name='Clinic B', license_code='code-b', password_hash='hash')
        db.session.add_all([clinic_a, clinic_b])
        db.session.commit()
        
        # Patient A registered to Clinic A
        patient_a = Patient(clinic_id=clinic_a.clinic_id, name='Patient A', contact_number='1234')
        # Patient B registered to Clinic B
        patient_b = Patient(clinic_id=clinic_b.clinic_id, name='Patient B', contact_number='5678')
        db.session.add_all([patient_a, patient_b])
        db.session.commit()
        
        # Capture IDs before context closes and session expires attributes
        clinic_a_id = clinic_a.clinic_id
        
    # Simulate logging into Clinic A
    with client.session_transaction() as sess:
        sess['clinic_id'] = clinic_a_id
        sess['clinic_name'] = 'Clinic A'
        sess['active_role'] = 'receptionist'
        sess['network_status'] = 'online'
        
    # Query Clinic A Patients list
    res = client.get('/patients/')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert 'Patient A' in html
    assert 'Patient B' not in html # Verification: Isolation working!

def test_scheduling_conflict_prevention(app, client):
    """Verify that slot collision checks block duplicate bookings"""
    with app.app_context():
        clinic = Clinic(name='Clinic A', license_code='code-a', password_hash='hash')
        db.session.add(clinic)
        db.session.commit()
        
        patient = Patient(clinic_id=clinic.clinic_id, name='Patient A', contact_number='1234')
        doc = Doctor(clinic_id=clinic.clinic_id, name='Dr. Kumar', specialization='Cardio')
        db.session.add_all([patient, doc])
        db.session.commit()
        
        # Pre-book slot
        appt = Appointment(
            clinic_id=clinic.clinic_id,
            patient_id=patient.patient_id,
            doctor_id=doc.doctor_id,
            date='2026-08-01',
            time_slot='10:00 AM',
            status='Scheduled'
        )
        db.session.add(appt)
        db.session.commit()
        
        # Capture variables
        clinic_id = clinic.clinic_id
        patient_id = patient.patient_id
        doctor_id = doc.doctor_id
        
    with client.session_transaction() as sess:
        sess['clinic_id'] = clinic_id
        sess['clinic_name'] = 'Clinic A'
        sess['active_role'] = 'receptionist'
        
    # Try booking duplicate slot (POST request)
    res = client.post('/appointments/book', data={
        'patient_id': patient_id,
        'doctor_id': doctor_id,
        'date': '2026-08-01',
        'time_slot': '10:00 AM',
        'type': 'consultation'
    }, follow_redirects=True)
    
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    # Should yield a flash error stating slot conflict
    assert 'Conflict' in html

def test_inventory_decrement_and_billing(app, client):
    """Verify that prescriptions decrement stock and update billing correctly"""
    with app.app_context():
        clinic = Clinic(name='Clinic A', license_code='code-a', password_hash='hash')
        db.session.add(clinic)
        db.session.commit()
        
        patient = Patient(clinic_id=clinic.clinic_id, name='Patient A', contact_number='1234')
        doc = Doctor(clinic_id=clinic.clinic_id, name='Dr. Kumar', specialization='Cardio')
        db.session.add_all([patient, doc])
        db.session.commit()
        
        appt = Appointment(
            clinic_id=clinic.clinic_id,
            patient_id=patient.patient_id,
            doctor_id=doc.doctor_id,
            date='2026-08-01',
            time_slot='10:00 AM',
            status='Scheduled'
        )
        db.session.add(appt)
        
        # Add drug to stock
        item = Inventory(clinic_id=clinic.clinic_id, name='Paracetamol 650mg', stock_quantity=100, unit_price=2.0)
        db.session.add(item)
        db.session.commit()
        
        # Capture IDs
        clinic_id = clinic.clinic_id
        appt_id = appt.appointment_id
        item_id = item.item_id
        
    with client.session_transaction() as sess:
        sess['clinic_id'] = clinic_id
        sess['clinic_name'] = 'Clinic A'
        sess['active_role'] = 'doctor' # Doctor required for consultation room
        
    # Prescribe Paracetamol for 5 days, 3 times daily (SOS/Thrice -> 15 units deduction)
    res = client.post(f'/doctors/consultation/{appt_id}', data={
        'bp': '120/80',
        'hr': '72',
        'temp': '98.6',
        'weight': '70',
        'symptoms': 'Headache',
        'diagnosis': 'Migraine',
        'med_name[]': ['Paracetamol 650mg'],
        'med_dosage[]': ['1 tablet'],
        'med_frequency[]': ['Thrice daily (8h)'],
        'med_duration[]': ['5 days']
    }, follow_redirects=True)
    
    assert res.status_code == 200
    
    with app.app_context():
        # Verify stock decreased by 15 units (100 - 15 = 85)
        stock_item = Inventory.query.get(item_id)
        assert stock_item.stock_quantity == 85
        
        # Verify invoice totals (300.0 consultation + 15 * 2.0 meds = 330.0)
        invoice = Invoice.query.filter_by(appointment_id=appt_id).first()
        assert invoice is not None
        assert invoice.medicine_fee == 30.0
        assert invoice.total_amount == 330.0
        assert invoice.status == 'Pending'

def test_offline_sms_queue_sync_lifecycle(app, client):
    """Verify that offline bookings queue notifications, and online sync flushes them"""
    with app.app_context():
        clinic = Clinic(name='Clinic A', license_code='code-a', password_hash='hash')
        db.session.add(clinic)
        db.session.commit()
        
        patient = Patient(clinic_id=clinic.clinic_id, name='Patient A', contact_number='1234')
        doc = Doctor(clinic_id=clinic.clinic_id, name='Dr. Kumar', specialization='Cardio')
        db.session.add_all([patient, doc])
        db.session.commit()
        
        patient_id = patient.patient_id
        doc_id = doc.doctor_id
        clinic_id = clinic.clinic_id
        
    # 1. Set network status to OFFLINE
    with client.session_transaction() as sess:
        sess['clinic_id'] = clinic_id
        sess['clinic_name'] = 'Clinic A'
        sess['active_role'] = 'receptionist'
        sess['network_status'] = 'offline'
        
    # Book appointment offline
    res = client.post('/appointments/book', data={
        'patient_id': patient_id,
        'doctor_id': doc_id,
        'date': '2026-08-01',
        'time_slot': '11:00 AM',
        'type': 'consultation'
    }, follow_redirects=True)
    
    assert res.status_code == 200
    
    with app.app_context():
        # Verify SMS log was queued as Pending
        log = SyncLog.query.filter_by(clinic_id=clinic_id, recipient='1234').first()
        assert log is not None
        assert log.status == 'Pending'
        
    # 2. Toggle network status to ONLINE
    with client.session_transaction() as sess:
        sess['network_status'] = 'online'
        
    # Trigger Sync Execution
    res = client.post('/sync/execute')
    assert res.status_code == 200
    data = json.loads(res.data.decode('utf-8'))
    assert data['success'] is True
    assert data['synced_count'] == 1
    
    with app.app_context():
        # Verify status is now Sent
        log = SyncLog.query.filter_by(clinic_id=clinic_id, recipient='1234').first()
        assert log.status == 'Sent'
        assert log.synced_at is not None

def test_brute_force_rate_limiting(app, client):
    """Verify that multiple failed login attempts trigger the 5-minute lockout"""
    with app.app_context():
        clinic = Clinic(name='Clinic Secure', license_code='sec-code', password_hash='hash')
        clinic.set_password('correct_pass')
        db.session.add(clinic)
        db.session.commit()
        
    # Simulate 5 failed login attempts
    for _ in range(5):
        client.post('/auth/login', data={'license_code': 'sec-code', 'password': 'wrong_pass'}, follow_redirects=True)
        
    # 6th attempt should be blocked by rate limiter
    res = client.post('/auth/login', data={'license_code': 'sec-code', 'password': 'correct_pass'}, follow_redirects=True)
    html = res.data.decode('utf-8')
    assert 'locked' in html.lower() or 'too many' in html.lower()

def test_clinic_self_registration(app, client):
    """Verify that a new organization can register and receives an isolated partition"""
    res = client.post('/auth/register', data={
        'name': 'Metro Health Clinic',
        'license_code': 'metro-88',
        'password': 'metro_secret_password',
        'address': 'Sector 14, Main Road',
        'contact': '+91 9876543210',
        'email': 'contact@metrohealth.com'
    }, follow_redirects=True)
    
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert 'Dashboard' in html or 'Metro Health Clinic' in html
    
    with app.app_context():
        clinic = Clinic.query.filter_by(license_code='metro-88').first()
        assert clinic is not None
        assert clinic.name == 'Metro Health Clinic'
        assert clinic.check_password('metro_secret_password') is True
