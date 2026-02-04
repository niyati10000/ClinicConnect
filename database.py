import sqlite3

def init_db():
    # Connect to SQLite (it will create the file if it doesn't exist)
    conn = sqlite3.connect('clinic.db')
    cursor = conn.cursor()

    # 1. Create Patient Table (Based on Exp 6)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            contact_number TEXT NOT NULL,
            health_issue TEXT
        )
    ''')

    # 2. Create Doctor Table (Based on Exp 6)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT,
            working_hours TEXT,
            availability_status TEXT DEFAULT 'Available'
        )
    ''')

    # 3. Create Appointment Table (Based on Exp 4 & 6)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            doctor_id INTEGER,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            type TEXT, -- consultation, follow-up, or diagnostic
            status TEXT DEFAULT 'Scheduled',
            FOREIGN KEY (patient_id) REFERENCES patients (patient_id),
            FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id)
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully with tables: Patients, Doctors, and Appointments.")

if __name__ == "__main__":
    init_db()