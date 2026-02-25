import sqlite3
import os

def init_db():
    """Initialize the database with all required tables"""
    
    # Remove existing database if you want a fresh start (optional)
    # if os.path.exists('clinic.db'):
    #     os.remove('clinic.db')
    
    # Connect to SQLite (it will create the file if it doesn't exist)
    conn = sqlite3.connect('clinic.db')
    cursor = conn.cursor()

    # 1. Create Patient Table
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

    # 2. Create Doctor Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT,
            working_hours TEXT,
            availability_status TEXT DEFAULT 'Available'
        )
    ''')

    # 3. Create Appointment Table
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
    print("✓ Database initialized successfully with all tables!")
    
    # Verify tables were created
    verify_tables()

def verify_tables():
    """Verify that all tables were created correctly"""
    conn = sqlite3.connect('clinic.db')
    cursor = conn.cursor()
    
    # Get list of tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("\n✓ Tables in database:")
    for table in tables:
        print(f"  - {table[0]}")
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"      • {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == "__main__":
    print("=" * 50)
    print("CLINIC DATABASE INITIALIZATION")
    print("=" * 50)
    init_db()