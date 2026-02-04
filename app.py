from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Function to connect to the database
def get_db_connection():
    conn = sqlite3.connect('clinic.db')
    conn.row_factory = sqlite3.Row
    return conn

# 1. Home Page / Dashboard (Based on Exp 8 Activity Diagram)
@app.route('/')
def index():
    return "<h1>Welcome to ClinicConnect</h1><p>Bilingual Appointment System</p>"

# 2. Patient Registration (Based on Exp 5 Use Case)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get data from the form
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        contact = request.form['contact']
        issue = request.form['issue']

        # Save to SQLite (Based on DFD Process 1.0)
        conn = get_db_connection()
        conn.execute('INSERT INTO patients (name, age, gender, contact_number, health_issue) VALUES (?, ?, ?, ?, ?)',
                     (name, age, gender, contact, issue))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)