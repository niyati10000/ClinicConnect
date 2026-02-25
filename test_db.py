import sqlite3

def test_connection():
    conn = sqlite3.connect('clinic.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check patients table structure
    cursor.execute("PRAGMA table_info(patients)")
    columns = cursor.fetchall()
    print("Patients table columns:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # Check if there are any patients
    cursor.execute("SELECT COUNT(*) as count FROM patients")
    count = cursor.fetchone()[0]
    print(f"\nTotal patients: {count}")
    
    # Show sample patient if exists
    if count > 0:
        cursor.execute("SELECT * FROM patients LIMIT 1")
        patient = cursor.fetchone()
        print(f"\nSample patient: {dict(patient)}")
    
    conn.close()

if __name__ == "__main__":
    test_connection()