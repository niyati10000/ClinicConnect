from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clinicconnect-secret-key-2024'

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('clinic.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
def init_db():
    conn = sqlite3.connect('clinic.db')
    cursor = conn.cursor()
    
    # Create patients table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            contact_number TEXT NOT NULL,
            health_issue TEXT,
            registration_date TEXT DEFAULT CURRENT_DATE
        )
    ''')
    
    # Create doctors table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT,
            working_hours TEXT,
            availability_status TEXT DEFAULT 'Available'
        )
    ''')
    
    # Insert sample doctors if table is empty
    cursor.execute("SELECT COUNT(*) FROM doctors")
    if cursor.fetchone()[0] == 0:
        sample_doctors = [
            ('Dr. Rajesh Kumar', 'Cardiologist', '9 AM - 5 PM', 'Available'),
            ('Dr. Priya Sharma', 'Pediatrician', '10 AM - 6 PM', 'Available'),
            ('Dr. Amit Patel', 'Orthopedic', '8 AM - 4 PM', 'Available'),
            ('Dr. Sneha Reddy', 'Dermatologist', '11 AM - 7 PM', 'Available'),
            ('Dr. Vikram Mehta', 'Neurologist', '9 AM - 3 PM', 'Available'),
            ('Dr. Anjali Desai', 'Gynecologist', '10 AM - 5 PM', 'Available')
        ]
        cursor.executemany('INSERT INTO doctors (name, specialization, working_hours, availability_status) VALUES (?, ?, ?, ?)', sample_doctors)
    
    # Create appointments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            doctor_id INTEGER,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            type TEXT,
            status TEXT DEFAULT 'Scheduled',
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
            FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

# Initialize DB on startup
init_db()

# ==================== ROUTES ====================

# Home Page
@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')

# API Stats
@app.route('/api/stats')
def get_stats():
    conn = get_db_connection()
    patients = conn.execute('SELECT COUNT(*) as count FROM patients').fetchone()['count']
    doctors = conn.execute('SELECT COUNT(*) as count FROM doctors WHERE availability_status = "Available"').fetchone()['count']
    today = datetime.now().strftime('%Y-%m-%d')
    appointments = conn.execute('SELECT COUNT(*) as count FROM appointments WHERE date = ?', (today,)).fetchone()['count']
    conn.close()
    return jsonify({
        'patients': patients,
        'doctors': doctors,
        'appointments': appointments
    })

# Patient Registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            name = request.form['name']
            age = request.form['age']
            gender = request.form['gender']
            contact = request.form['contact']
            issue = request.form.get('issue', '')
            preferred_date = request.form.get('preferred_date', '')
            
            if not name or not age or not gender or not contact:
                flash('All required fields must be filled! / सभी आवश्यक फ़ील्ड भरें!', 'error')
                return redirect(url_for('register'))
            
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO patients (name, age, gender, contact_number, health_issue) 
                VALUES (?, ?, ?, ?, ?)
            ''', (name, age, gender, contact, issue))
            
            patient_id = cursor.lastrowid
            
            # If preferred date is provided, create an appointment
            if preferred_date:
                # Get first available doctor
                doctor = conn.execute('SELECT doctor_id FROM doctors WHERE availability_status = "Available" LIMIT 1').fetchone()
                if doctor:
                    cursor.execute('''
                        INSERT INTO appointments (patient_id, doctor_id, date, time, type, status)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (patient_id, doctor['doctor_id'], preferred_date, '10:00 AM', 'consultation', 'Scheduled'))
            
            conn.commit()
            conn.close()
            
            flash(f'Patient registered successfully! Patient ID: {patient_id} / रोगी पंजीकरण सफल!', 'success')
            return redirect(url_for('view_patients'))  # Redirect to patients list after registration
            
        except Exception as e:
            flash(f'Error: {str(e)} / त्रुटि: {str(e)}', 'error')
            return redirect(url_for('register'))
    
    return render_template('register.html')

# View all patients
@app.route('/patients')
def view_patients():
    conn = get_db_connection()
    patients = conn.execute('SELECT * FROM patients ORDER BY registration_date DESC').fetchall()
    conn.close()
    return render_template('patients.html', patients=patients)

# View all doctors
@app.route('/doctors')
def view_doctors():
    conn = get_db_connection()
    doctors = conn.execute('SELECT * FROM doctors').fetchall()
    conn.close()
    return render_template('doctors.html', doctors=doctors)

# View all appointments
@app.route('/appointments')
def view_appointments():
    conn = get_db_connection()
    appointments = conn.execute('''
        SELECT a.*, p.name as patient_name, d.name as doctor_name, d.specialization 
        FROM appointments a
        JOIN patients p ON a.patient_id = p.patient_id
        JOIN doctors d ON a.doctor_id = d.doctor_id
        ORDER BY a.date DESC, a.time DESC
    ''').fetchall()
    conn.close()
    return render_template('appointments.html', appointments=appointments)

# View single patient details
@app.route('/patient/<int:patient_id>')
def view_patient(patient_id):
    conn = get_db_connection()
    patient = conn.execute('SELECT * FROM patients WHERE patient_id = ?', (patient_id,)).fetchone()
    
    # Get patient's appointments
    appointments = conn.execute('''
        SELECT a.*, d.name as doctor_name, d.specialization 
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE a.patient_id = ?
        ORDER BY a.date DESC
    ''', (patient_id,)).fetchall()
    
    conn.close()
    
    if patient is None:
        flash('Patient not found! / रोगी नहीं मिला!', 'error')
        return redirect(url_for('view_patients'))
    
    return render_template('patient_detail.html', patient=patient, appointments=appointments)

# Cancel appointment
@app.route('/appointment/cancel/<int:appointment_id>')
def cancel_appointment(appointment_id):
    conn = get_db_connection()
    conn.execute('UPDATE appointments SET status = ? WHERE appointment_id = ?', ('Cancelled', appointment_id))
    conn.commit()
    conn.close()
    flash('Appointment cancelled successfully! / अपॉइंटमेंट रद्द कर दिया गया!', 'success')
    return redirect(url_for('view_appointments'))

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)