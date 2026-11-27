# MediAssist
### Smart Hospital Service & Automation System

**Making Hospital Services Easier.**

MediAssist is an educational hospital service management and automation project designed to make hospital operations more organized and efficient through digital management, rule-based automation, and virtual robot simulation.

---

## Project Overview

MediAssist provides a centralized platform for managing patient information, hospital service requests, medical reports, and virtual robot tasks.

The system demonstrates how software-based automation can help organize hospital services and reduce manual coordination.

## Project Objectives

- Organize patient information digitally.
- Manage hospital service requests efficiently.
- Maintain medical report records.
- Automate task classification using predefined rules.
- Simulate robot task management and movement.
- Monitor hospital activities through an interactive dashboard.
- Generate downloadable patient and request reports.

## Main Features

### 1. Overview Dashboard
- Patient statistics
- Request analytics
- Robot task performance
- Patient registration trends

### 2. Patient Management
- Register new patients
- View and search patient records
- Filter patient information
- Archive and restore patient records

### 3. Patient Requests
- Create hospital service requests
- Select request types and priorities
- Track request status
- Update request progress

### 4. Medical Report Management
- Add medical report records
- Organize reports by category
- Store report findings and doctor notes
- Track report status

### 5. Reports & Export
- Generate individual patient reports
- Generate combined patient request reports
- Export reports as PDF files

### 6. Robot Control
- Create robot delivery tasks
- Start and complete tasks
- Track robot status
- View task history and performance

### 7. AI & Automation
- Rule-based request classification
- Automated task creation
- Duplicate task prevention

### 8. Hospital Map
- Virtual hospital layout
- Robot location tracking
- Task destination display
- Simulated robot movement

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| Streamlit | Web application interface |
| SQLite | Database management |
| Pandas | Data handling |
| Plotly | Interactive charts |
| ReportLab | PDF generation |

## Database Structure

The project uses an SQLite database with five main tables:

- `patients`
- `patient_requests`
- `medical_reports`
- `robot_tasks`
- `robot_status`

## Project Folder Structure

```text
MediAssist/
│
├── app.py
├── requirements.txt
├── README.md
│
├── database/
│   ├── __init__.py
│   ├── db_connection.py
│   ├── setup_db.py
│   └── mediassist.db
│
├── pages/
│   ├── overview.py
│   ├── patient_management.py
│   ├── patient_requests.py
│   ├── robot_control.py
│   ├── ai_automation.py
│   ├── hospital_map.py
│   ├── reports.py
│   └── medical_reports.py
│
└── assets/
```

## Installation & Run Instructions

### Step 1: Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
```

### Step 2: Open the Project Folder

```bash
cd MediAssist
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Initialize the Database

If the database has not been initialized:

```bash
python -m database.setup_db
```

### Step 5: Run the Application

```bash
streamlit run app.py
```

The application will open in your default web browser.

## Project Limitations

- The robot operates through virtual simulation, not physical hardware.
- The automation module uses predefined rules; it is not a trained machine-learning model.
- The project is an educational prototype, not a production hospital management system.
- Only fictional or demonstration data should be used.

## Developer Information

**Developed by:** Shihab  
**Batch:** Statistics 40 Batch  
**Institution:** Rajshahi College  
**Department:** Statistics

---

### Project Tagline

**MediAssist — Making Hospital Services Easier.**