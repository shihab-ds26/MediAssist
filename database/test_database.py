
from database.db_connection import get_connection


def test_database():

    connection = get_connection()
    cursor = connection.cursor()

    print("\n========== DATABASE TABLES ==========")

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        ORDER BY name
    """)

    tables = cursor.fetchall()

    for table in tables:
        print("Table:", table["name"])

    print("\n========== ADD DEMO PATIENT ==========")

    cursor.execute("""
        INSERT INTO patients
        (full_name, age, gender, phone, room_number)
        VALUES (?, ?, ?, ?, ?)
    """, (
        "Patient One",
        35,
        "Male",
        "01700000000",
        "204"
    ))

    connection.commit()

    print("Demo patient added successfully!")

    print("\n========== PATIENT RECORD ==========")

    cursor.execute("""
        SELECT *
        FROM patients
        ORDER BY patient_id DESC
        LIMIT 1
    """)

    patient = cursor.fetchone()

    if patient:
        for key in patient.keys():
            print(f"{key}: {patient[key]}")

    connection.close()

    print("\nDatabase testing completed!")


if __name__ == "__main__":
    test_database()
