# System Design and Architecture

## Overview
This directory contains the visual modeling artifacts and technical blueprints for the Clinic Appointment Management System. These documents translate the functional requirements defined in the SRS into structured technical specifications used for backend development and database implementation.

The design documentation follows standard UML (Unified Modeling Language) practices to define the system's structure, behavior, and interaction logic.

## 1. Structural Modeling
These models define the static architecture and data organization of the application.



* **Class Diagram (`class diagram.pdf`)**
    * **Purpose:** Defines the object-oriented structure of the system.
    * **Key Entities:** Mapped objects include `Patient`, `Doctor`, and `Appointment`.
    * **Details:** Specifies attributes, methods, and the cardinal relationships (e.g., one-to-many associations) between entities.

* **Data Flow Diagram (DFD) (`dfd_design.pdf`)**
    * **Purpose:** Visualizes the movement of information through the system.
    * **Scope:** Traces the lifecycle of data from user input (Entry), through processing logic, to persistent storage in the SQLite database, and finally to output generation (Reports/Reminders).



## 2. Behavioral Modeling
These diagrams illustrate how the system responds to external events and manages workflows over time.



* **Use Case Diagrams (`Overall use case.pdf`)**
    * **Purpose:** Provides a high-level functional view of the system boundaries.
    * **Actors:** Defines the specific accessibility and permissions for Receptionists, Doctors, and Patients.

* **Activity Diagram (`Activity diagram.pdf`)**
    * **Purpose:** Maps the operational workflow and sequential logic.
    * **Scenario:** details the step-by-step decision paths for core processes, such as handling a walk-in patient registration.

* **State Transition Diagram (`State transition diagram.pdf`)**
    * **Purpose:** Tracks the lifecycle of dynamic entities.
    * **Scenario:** Focuses on the status changes of an `Appointment` object (e.g., `Scheduled` $\rightarrow$ `Confirmed` $\rightarrow$ `Completed` or `Cancelled`).



[Image of state machine diagram example]


## 3. Interaction Modeling
These diagrams capture the chronological communication between system components.



[Image of sequence diagram booking system]


* **Sequence Diagram (`Sequence diagram.pdf`)**
    * **Purpose:** Illustrates the message flow between the User Interface, Backend Controllers, and the Database.
    * **Focus:** Details the precise order of operations required for the "Book Appointment" function.

## Documentation Inventory

| File Name | Diagram Type | Technical Focus |
| :--- | :--- | :--- |
| **Overall use case.pdf** | Behavioral | High-level system scope and actor interactions. |
| **dfd_design.pdf** | Structural | Data movement, inputs, and outputs. |
| **class diagram.pdf** | Structural | Database schema mapping and object relationships. |
| **Sequence diagram.pdf** | Interaction | Chronological logic flow for booking appointments. |
| **Activity diagram.pdf** | Behavioral | Operational workflows and decision trees. |
| **State transition diagram.pdf** | Behavioral | Lifecycle management of records. |

## Tooling and Setup
The diagrams in this repository were generated using standard modeling tools. To view or edit the source files, the following setup is recommended:

* **PDF Viewer:** Any standard PDF reader (Adobe Acrobat, Chrome, Preview) is sufficient for reviewing the exported documentation.
* **Modeling Software:** (Specify the tool used, e.g., StarUML, Lucidchart, or Draw.io) is required to edit the source logic files.
