
from database.db_connection import get_connection


def create_tables():

    connection = get_connection()
    cursor = connection.cursor()

    # 1. Patients Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            phone TEXT,
            room_number TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 2. Patient Requests Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            request_type TEXT NOT NULL,
            description TEXT,
            priority TEXT DEFAULT 'Normal',
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (patient_id)
                REFERENCES patients(patient_id)
        )
    """)

    # 3. Medical Reports Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medical_reports (
            report_id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            report_name TEXT NOT NULL,
            requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expected_at TIMESTAMP,
            status TEXT DEFAULT 'Pending',

            FOREIGN KEY (patient_id)
                REFERENCES patients(patient_id)
        )
    """)

    # 4. Robot Tasks Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS robot_tasks (
            task_id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER,
            task_type TEXT NOT NULL,
            destination TEXT NOT NULL,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,

            FOREIGN KEY (request_id)
                REFERENCES patient_requests(request_id)
        )
    """)

    # 5. Robot Status Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS robot_status (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            status TEXT DEFAULT 'Idle',
            current_task_id INTEGER,
            current_destination TEXT,
            current_location TEXT DEFAULT 'Robot Parking',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (current_task_id)
                REFERENCES robot_tasks(task_id)
        )
    """)

    # =====================================
    # SAFE DATABASE MIGRATION
    # Add current_location to existing DB
    # =====================================

    cursor.execute("PRAGMA table_info(robot_status)")
    columns = [column["name"] for column in cursor.fetchall()]

    if "current_location" not in columns:
        cursor.execute("""
            ALTER TABLE robot_status
            ADD COLUMN current_location TEXT DEFAULT 'Robot Parking'
        """)

    # Fill location for existing robot record
    cursor.execute("""
        UPDATE robot_status
        SET current_location = 'Robot Parking'
        WHERE id = 1 AND (
            current_location IS NULL
            OR current_location = ''
        )
    """)

    # Create indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_patient_name
        ON patients(full_name)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_request_patient
        ON patient_requests(patient_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_report_patient
        ON medical_reports(patient_id)
    """)

    # Initialize robot status
    cursor.execute("""
        INSERT OR IGNORE INTO robot_status
        (id, status, current_location)
        VALUES (1, 'Idle', 'Robot Parking')
    """)

    connection.commit()
    connection.close()

    print("===================================")
    print("MediAssist Database Updated!")
    print("All 5 tables are ready.")
    print("Robot location tracking is enabled.")
    print("===================================")


if __name__ == "__main__":
    create_tables()
