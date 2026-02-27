# ClinicConnect: Appointment Management System

![Status](https://img.shields.io/badge/Status-Active-success) ![Language](https://img.shields.io/badge/Language-Python_3-blue) ![Framework](https://img.shields.io/badge/Framework-Flask-green) ![Architecture](https://img.shields.io/badge/Architecture-Offline--First-orange)

**ClinicConnect** is a specialized healthcare management solution designed to address the unique operational challenges of clinics in tier-2 and tier-3 cities. It is a lightweight, offline-first application that digitizes patient records and appointment scheduling, replacing inefficient manual registers with a streamlined, automated workflow.

---

## 1. Key Features

* **Offline-First Architecture:** Engineered to remain fully functional without an active internet connection, ensuring reliability in regions with unstable digital infrastructure.
* **Native Bilingual Support:** Deep integration of both Hindi and English interfaces to ensure accessibility and ease of use for local clinic staff.
* **Optimized for Low-Spec Hardware:** Designed to operate smoothly on legacy systems (minimum 2GB RAM) while maintaining sub-2-second response times.
* **Automated Communication:** Integrated Twilio API for sending automated SMS appointment confirmations and reminders to patients.
* **Dynamic Scheduling:** Automated slot management logic that strictly prevents double-booking and manages high patient volumes efficiently.

---

## 2. Problem Statement & Business Case

Small clinics in rural and semi-urban areas currently rely heavily on manual, paper-based registers. This operational model presents severe limitations:
* High frequency of scheduling conflicts and double-bookings.
* Inability to accurately track or retrieve patient medical histories.
* Chaotic overbooking during peak periods, such as monsoon seasons or flu outbreaks.

**ClinicConnect** provides a robust, cost-effective digital alternative tailored specifically for staff with limited technical expertise. By automating data entry and schedule visualization, it eliminates errors during rapid walk-in registrations, prevents doctor burnout, and drastically reduces physical wait times for patients. Engineered to run on low-spec hardware (2GB RAM) with sub-2-second response times.

---

## 3. Software Requirements Specification (SRS)

This system is architected in alignment with the **IEEE 830-1998 Standard**, ensuring rigorous adherence to both functional capabilities and strict environmental constraints.

### A. Functional Requirements
* **Patient Management Engine:** Digital registration with auto-generated Unique IDs, comprehensive demographic profiling, and medical history tracking.
* **Dynamic Scheduling System:** Algorithmic slot management that actively calculates doctor availability and strictly prevents double-booking.
* **Communication Gateway:** Asynchronous integration with the Twilio API to dispatch automated SMS appointment confirmations and reminders.
* **Analytics Dashboard:** Real-time aggregation of clinic metrics, including daily patient footfall, active appointments, and doctor availability statuses.

### B. Non-Functional Requirements (NFRs)
* **Reliability (Offline-First):** Must maintain 100% core functionality without internet access, utilizing local SQLite file-based storage.
* **Accessibility:** Must provide native, seamless toggling between English and Hindi (हिंदी) without requiring page reloads or external translation plugins.
* **Performance Constraints:** Engineered to execute smoothly on legacy clinic hardware (minimum 2GB RAM / Dual-Core processors) with sub-2-second query response times.

### C. Stakeholder Impact Analysis
* **Receptionists (Operators):** Benefit from a high-contrast, minimalist UI that reduces cognitive load and eliminates data-entry errors during rapid walk-in registrations.
* **Doctors (Providers):** Gain access to a clean, visualized dashboard of their daily schedule, minimizing administrative fatigue and improving care delivery.
* **Patients (End-Users):** Experience drastically reduced physical wait times through structured slotting and receive immediate digital confirmation of their appointments.

---

## 4. System Design & Architecture

This section details the visual modeling and technical blueprints used to architect the system. These models translate the functional requirements into a structured format for implementation.

### A. Structural Modeling (The Skeleton)
These diagrams define the static structure and data organization.

* **Class Diagram:** Defines the object-oriented structure, mapping key entities like `Patient`, `Doctor`, and `Appointment`, along with their attributes and relationships (e.g., one doctor handles multiple appointments).

* **Data Flow Diagram (DFD):** Visualizes the lifecycle of information—from user input at the reception desk, through the processing logic, to persistent storage in the SQLite database, and finally to report generation.


### B. Behavioral Modeling (The Logic)
These diagrams illustrate how the system handles workflows and responds to external events.

* **Use Case Diagrams:** Provides a high-level view of system boundaries, defining specific permissions for Receptionists (booking), Doctors (viewing), and Patients (receiving notifications).
* **State Transition Diagram:** Tracks the dynamic status of an appointment entity (e.g., `Scheduled` -> `Confirmed` -> `Completed` or `Cancelled`).
* **Activity Diagram:** Maps complex operational workflows, such as the specific decision tree a receptionist follows when handling a walk-in patient versus a pre-booked one.

### C. Interaction Modeling (The Flow)
* **Sequence Diagram:** Captures the chronological flow of messages between the User Interface (Frontend), the Backend Controller (Flask), and the Database. This is critical for understanding the "Book Appointment" atomic transaction.


---

## 5. Technical Implementation

The application follows a monolithic, offline-first architecture to ensure reliability in low-connectivity regions.

### Technology Stack
* **Backend Framework:** **Flask (Python 3.x)** - Handles routing, business logic, and ORM.
* **Database:** **SQLite3** - Serverless, file-based storage ensures the system requires no complex server setup.
* **Frontend:** **HTML5, CSS3, Jinja2** - Renders a responsive, bilingual user interface.
* **Utilities:** **Pandas** (Data processing) and **Twilio** (SMS Gateway).

### Repository Structure
| File/Directory | Description |
| :--- | :--- |
| `app.py` | Main Flask controller with 10+ routes for patients, doctors, and appointments. |
| `database.py` | Database initialization script pre-loaded with sample doctors data. |
| `requirements.txt` | Manifest of Python dependencies (Flask, Pandas, Twilio, etc.). |
| `clinic.db` | SQLite database (auto-generated upon initialization). |
| `/templates` | Directory containing all HTML Jinja2 view files. |
| ├── `index.html` | Home dashboard with live statistics and navigation. |
| ├── `register.html` | Bilingual patient registration form. |
| ├── `patients.html` | List view of all registered patients. |
| ├── `doctors.html` | Grid view of all doctors and their specializations. |
| ├── `appointments.html` | Complete appointment manager with status tracking. |
| └── `patient_detail.html` | Individual patient view displaying medical history. |

### Available Routes (Endpoints)
| Route | Method | Description |
| :--- | :--- | :--- |
| `/` or `/home` | GET | Renders the home dashboard with statistics. |
| `/register` | GET/POST | Handles the patient registration form submission. |
| `/patients` | GET | Displays all registered patients. |
| `/doctors` | GET | Displays the doctor directory. |
| `/appointments` | GET | Displays all scheduled and past appointments. |
| `/patient/<id>` | GET | Fetches details for a specific single patient. |
| `/appointment/cancel/<id>`| GET | Logic to cancel an active appointment. |
| `/api/stats` | GET | JSON API endpoint feeding data to the dashboard. |

### Database Schema

The system uses a lightweight SQLite database (`clinic.db`) with three main tables to keep everything organized:

**1. Patients Table**
* **Purpose:** Stores all patient records and medical details.
* **What it saves:** Patient ID, Name, Age, Gender, Contact Number, Health Issue, and the Date they registered.

**2. Doctors Table**
* **Purpose:** Manages the clinic's medical staff and their schedules.
* **What it saves:** Doctor ID, Name, Specialization (e.g., Cardiologist), Working Hours, and Current Availability.
* *Note: This table comes pre-loaded with 6 sample doctors so you can test the system immediately.*

**3. Appointments Table**
* **Purpose:** The core table that connects a Patient to a specific Doctor for a visit.
* **What it saves:** Appointment ID, the chosen Date and Time, the Type of visit (Walk-in/Pre-booked), and the Status (Scheduled, Completed, or Cancelled).



## 6. Installation & Setup

Follow these instructions to deploy the system locally.

### Prerequisites
* Python 3.x installed
* Git installed

### Steps

1. **Clone the Repository**
   ```bash
   git clone [https://github.com/niyati10000/ClinicConnect.git](https://github.com/niyati10000/ClinicConnect.git)
   cd ClinicConnect

2.  **Install Dependencies**
   pip install -r requirements.txt

3.  **Initialize the Database**
    Run the setup script to generate the local SQLite database file (clinic.db).
    python database.py

5.  **Run the Application**
    Start the Flask development server.
    python app.py

6. **Access the Application**
   Open your browser and navigate to the following local addresses to explore the system:

   * **Main Dashboard:** `http://127.0.0.1:5000/`
   * **Patient Registration:** `http://127.0.0.1:5000/register`
   * **View All Patients:** `http://127.0.0.1:5000/patients`
   * **Doctor Directory:** `http://127.0.0.1:5000/doctors`
   * **Manage Appointments:** `http://127.0.0.1:5000/appointments`

**video reference**



https://github.com/user-attachments/assets/58867e4b-b174-42a2-8414-df63612f2863




