# ClinicConnect: Appointment Management System

![Status](https://img.shields.io/badge/Status-Active-success) ![Language](https://img.shields.io/badge/Language-Python_3-blue) ![Framework](https://img.shields.io/badge/Framework-Flask-green) ![Architecture](https://img.shields.io/badge/Architecture-Offline--First-orange)

**ClinicConnect** is a specialized healthcare management solution designed to address the unique operational challenges of clinics in tier-2 and tier-3 cities. It is a lightweight, offline-first application that digitizes patient records and appointment scheduling, replacing inefficient manual registers with a streamlined, automated workflow.

---

## 1. Problem Statement & Business Case

The foundation of this project addresses a critical gap in rural and semi-urban healthcare management, where digital infrastructure is often unreliable.

* **The Challenge:** Small clinics currently rely on manual paper-based registers. This leads to severe scheduling conflicts, inability to track patient history, and chaotic overbooking during peak seasons (e.g., monsoons or flu outbreaks).
* **The Solution:** A robust, cost-effective system designed for staff with limited technical expertise.
    * **Offline Capability:** Fully functional without an active internet connection.
    * **Bilingual Support:** Native support for Hindi and English to ensure accessibility for local staff.
    * **Performance:** Engineered to run on low-spec hardware (2GB RAM) with sub-2-second response times.

---

## 2. Software Requirements Specification (SRS)

This system is built according to the **IEEE 830-1998 Standard**, ensuring rigorous adherence to functional and non-functional requirements.

### Functional Scope
* **Patient Management:** Digital registration, distinct identification, and medical history tracking.
* **Dynamic Scheduling:** Automated slot management that prevents double-booking.
* **Communication:** Integration with Twilio for automated SMS appointment confirmations and reminders.

### Stakeholder Analysis
* **Receptionists:** Benefit from a high-contrast, simplified UI that eliminates data entry errors during rapid walk-in registrations.
* **Doctors:** Gain access to a visualized dashboard of daily schedules, preventing burnout and improving care delivery.
* **Patients:** Experience reduced physical wait times and receive timely updates via SMS.

---

## 3. System Design & Architecture

This section details the visual modeling and technical blueprints used to architect the system. These models translate the functional requirements into a structured format for implementation.

### A. Structural Modeling (The Skeleton)
These diagrams define the static structure and data organization.

* **Class Diagram:** Defines the object-oriented structure, mapping key entities like `Patient`, `Doctor`, and `Appointment`, along with their attributes and relationships (e.g., one doctor handles multiple appointments).

* **Data Flow Diagram (DFD):** Visualizes the lifecycle of information—from user input at the reception desk, through the processing logic, to persistent storage in the SQLite database, and finally to report generation.


[Image of data flow diagram for clinic management system]


### B. Behavioral Modeling (The Logic)
These diagrams illustrate how the system handles workflows and responds to external events.

* **Use Case Diagrams:** Provides a high-level view of system boundaries, defining specific permissions for Receptionists (booking), Doctors (viewing), and Patients (receiving notifications).
* **State Transition Diagram:** Tracks the dynamic status of an appointment entity (e.g., `Scheduled` -> `Confirmed` -> `Completed` or `Cancelled`).
* **Activity Diagram:** Maps complex operational workflows, such as the specific decision tree a receptionist follows when handling a walk-in patient versus a pre-booked one.

### C. Interaction Modeling (The Flow)
* **Sequence Diagram:** Captures the chronological flow of messages between the User Interface (Frontend), the Backend Controller (Flask), and the Database. This is critical for understanding the "Book Appointment" atomic transaction.


---

## 4. Technical Implementation

The application follows a monolithic, offline-first architecture to ensure reliability in low-connectivity regions.

### Technology Stack
* **Backend Framework:** **Flask (Python 3.x)** - Handles routing, business logic, and ORM.
* **Database:** **SQLite3** - Serverless, file-based storage ensures the system requires no complex server setup.
* **Frontend:** **HTML5, CSS3, Jinja2** - Renders a responsive, bilingual user interface.
* **Utilities:** **Pandas** (Data processing) and **Twilio** (SMS Gateway).

### Repository Structure
| File/Directory | Description |
| :--- | :--- |
| `app.py` | Main controller handling HTTP routing, bilingual logic switching, and database interactions. |
| `database.py` | Initialization script that defines the schema and generates the local `clinic.db` file. |
| `requirements.txt` | Manifest of Python dependencies (Flask, Pandas, Twilio, etc.). |
| `/templates` | HTML view files for the Dashboard and Registration pages. |

### Database Schema
The relational model is implemented in `clinic.db` with three primary entities:
1.  **Patients:** Stores unique IDs, demographic details, and medical history.
2.  **Doctors:** Tracks specialization, IDs, and availability status.
3.  **Appointments:** The associative entity linking Patients and Doctors to specific time slots.

---

## 5. Installation & Setup

Follow these instructions to deploy the system locally.

### Prerequisites
* Python 3.x installed
* Git installed

### Steps
1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/niyati10000/ClinicConnect.git](https://github.com/niyati10000/ClinicConnect.git)
    cd ClinicConnect
    ```

2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Initialize the Database**
    Run the setup script to generate the local SQLite database file.
    ```bash
    python database.py
    ```

4.  **Run the Application**
    Start the Flask development server.
    ```bash
    python app.py
    ```

5.  **Access the Dashboard**
    Open your browser and navigate to:
    * **Dashboard:** `http://127.0.0.1:5000/`
    * **Registration:** `http://127.0.0.1:5000/register`
