
import streamlit as st
import pandas as pd

from datetime import date, datetime
from database.db_connection import get_connection


# ==========================================
# PAGE CONFIGURATION & CUSTOM CSS
# ==========================================

st.set_page_config(
    page_title="MediAssist | Patient Management",
    page_icon="🏥",
    layout="wide"
)

st.markdown("""
<style>

/* ==================================
   MEDIASSIST PROFESSIONAL THEME
================================== */

.stApp {
    background-color: #F2F6FC !important;
    color: #18324D !important;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Main headings */
h1, h2, h3, h4, h5, h6 {
    color: #12365A !important;
    font-weight: 750 !important;
}

/* All normal text */
p, label, li,
.stMarkdown,
.stCaption,
[data-testid="stWidgetLabel"],
[data-testid="stMarkdownContainer"] p {
    color: #263F59 !important;
}

/* Section captions */
.stCaption,
[data-testid="stCaptionContainer"] {
    color: #526B83 !important;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #D7E3F0 !important;
    padding: 20px !important;
    border-radius: 15px !important;
    box-shadow: 0 4px 14px rgba(20, 55, 90, 0.08);
}

[data-testid="stMetricLabel"],
[data-testid="stMetricLabel"] p {
    color: #425E78 !important;
    font-weight: 600 !important;
}

[data-testid="stMetricValue"],
[data-testid="stMetricValue"] div {
    color: #12365A !important;
    font-weight: 750 !important;
}

/* Input fields */
.stTextInput label,
.stNumberInput label,
.stSelectbox label,
.stDateInput label,
.stRadio label,
.stCheckbox label {
    color: #173B5E !important;
    font-weight: 650 !important;
}

/* Text input text */
.stTextInput input,
.stNumberInput input,
.stDateInput input {
    color: #17324D !important;
    background-color: #FFFFFF !important;
    border: 1px solid #B8CADD !important;
    border-radius: 9px !important;
}

/* Placeholder text */
.stTextInput input::placeholder,
.stNumberInput input::placeholder {
    color: #70869B !important;
    opacity: 1 !important;
}

/* Selectbox */
.stSelectbox div[data-baseweb="select"] {
    background-color: #FFFFFF !important;
    border-radius: 9px !important;
}

.stSelectbox div[data-baseweb="select"] * {
    color: #17324D !important;
}

/* Date picker */
.stDateInput div[data-baseweb="input"] {
    background-color: #FFFFFF !important;
    border-radius: 9px !important;
}

.stDateInput input {
    color: #17324D !important;
}

/* Radio and checkbox */
.stRadio p,
.stCheckbox p {
    color: #173B5E !important;
}

/* Buttons */
.stButton > button,
.stFormSubmitButton > button {
    background-color: #126B87 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 9px !important;
    min-height: 43px !important;
    font-weight: 700 !important;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background-color: #0D526B !important;
    color: #FFFFFF !important;
    border: none !important;
}

/* Data table */
[data-testid="stDataFrame"] {
    border: 1px solid #D4E0EC !important;
    border-radius: 12px !important;
}

/* Expanders */
[data-testid="stExpander"] {
    background-color: #FFFFFF !important;
    border: 1px solid #D4E0EC !important;
    border-radius: 12px !important;
}

[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary p {
    color: #173B5E !important;
    font-weight: 650 !important;
}

/* Form background */
[data-testid="stForm"] {
    background-color: #FFFFFF !important;
    border: 1px solid #DCE6F0 !important;
    border-radius: 15px !important;
    padding: 20px !important;
}

/* Dividers */
hr {
    border-color: #D5E1ED !important;
}

/* Success and warning messages */
[data-testid="stAlert"] {
    border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)




# ==========================================
# DATABASE FUNCTIONS
# ==========================================

def prepare_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(patients)")
    columns = [column["name"] for column in cursor.fetchall()]

    # Add archive support to existing database
    if "is_active" not in columns:

        cursor.execute("""
            ALTER TABLE patients
            ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1
        """)

    connection.commit()
    connection.close()


def get_all_patients(show_archived=False):

    connection = get_connection()

    if show_archived:

        query = """
            SELECT *
            FROM patients
            WHERE is_active = 0
            ORDER BY patient_id DESC
        """

    else:

        query = """
            SELECT *
            FROM patients
            WHERE is_active = 1
            ORDER BY patient_id DESC
        """

    patients = pd.read_sql_query(query, connection)

    connection.close()

    return patients


def register_patient(
    full_name,
    age,
    gender,
    phone,
    room_number
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO patients
        (
            full_name,
            age,
            gender,
            phone,
            room_number,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        full_name,
        age,
        gender,
        phone,
        room_number,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    connection.commit()
    connection.close()


def archive_patient(patient_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE patients
        SET is_active = 0
        WHERE patient_id = ?
    """, (patient_id,))

    connection.commit()
    connection.close()


def restore_patient(patient_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE patients
        SET is_active = 1
        WHERE patient_id = ?
    """, (patient_id,))

    connection.commit()
    connection.close()


# ==========================================
# MAIN PAGE
# ==========================================

def show_patient_management():

    prepare_database()

    st.title("🏥 Patient Management")

    st.caption(
        "Manage patient registration, records and daily admissions."
    )

    st.divider()

    patients = get_all_patients()

    # ======================================
    # STATISTICS CARDS
    # ======================================

    total_patients = len(patients)

    male_count = (
        len(patients[patients["gender"] == "Male"])
        if not patients.empty else 0
    )

    female_count = (
        len(patients[patients["gender"] == "Female"])
        if not patients.empty else 0
    )

    today = date.today().isoformat()

    today_count = (
        len(
            patients[
                patients["created_at"].astype(str).str[:10] == today
            ]
        )
        if not patients.empty else 0
    )

    st.subheader("Patient Overview")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Total Patients", total_patients)
    col2.metric("Male Patients", male_count)
    col3.metric("Female Patients", female_count)
    col4.metric("Today's Registration", today_count)

    st.divider()

    # ======================================
    # REGISTRATION FORM
    # ======================================

    st.subheader("➕ Register New Patient")

    with st.form("patient_registration_form"):

        col1, col2 = st.columns(2)

        with col1:

            full_name = st.text_input(
                "Patient Full Name *",
                placeholder="Enter patient name"
            )

            age = st.number_input(
                "Age *",
                min_value=1,
                max_value=120,
                value=25
            )

            gender = st.selectbox(
                "Gender *",
                ["Male", "Female", "Other"]
            )

        with col2:

            phone = st.text_input(
                "Phone Number",
                placeholder="Enter phone number"
            )

            room_number = st.text_input(
                "Room Number *",
                placeholder="Enter room number"
            )

        submitted = st.form_submit_button(
            "Register Patient",
            use_container_width=True
        )

        if submitted:

            if not full_name.strip():

                st.error("Please enter patient name.")

            elif not room_number.strip():

                st.error("Please enter room number.")

            else:

                register_patient(
                    full_name.strip(),
                    int(age),
                    gender,
                    phone.strip(),
                    room_number.strip()
                )

                st.success("Patient registered successfully!")

                st.rerun()

    st.divider()

    # ======================================
    # PATIENT DIRECTORY
    # ======================================

    st.subheader("📋 Patient Directory")

    patients = get_all_patients()

    if not patients.empty:

        filter_col1, filter_col2 = st.columns(2)

        with filter_col1:

            search = st.text_input(
                "🔍 Search Patient",
                placeholder="Search by name or Patient ID"
            )

        with filter_col2:

            gender_filter = st.selectbox(
                "Filter by Gender",
                ["All", "Male", "Female", "Other"]
            )

        date_mode = st.radio(
            "Registration Date",
            ["All Dates", "Select Date"],
            horizontal=True
        )

        selected_date = None

        if date_mode == "Select Date":

            selected_date = st.date_input(
                "Choose Registration Date",
                value=date.today()
            )

        filtered = patients.copy()

        if search.strip():

            search_text = search.strip()

            filtered = filtered[
                filtered["full_name"].str.contains(
                    search_text,
                    case=False,
                    na=False
                )
                |
                filtered["patient_id"].astype(str).str.contains(
                    search_text
                )
            ]

        if gender_filter != "All":

            filtered = filtered[
                filtered["gender"] == gender_filter
            ]

        if selected_date:

            filtered = filtered[
                filtered["created_at"].astype(str).str[:10]
                == selected_date.isoformat()
            ]

        st.caption(
            f"Showing {len(filtered)} patient records"
        )

        if filtered.empty:

            st.info("No matching patient records found.")

        else:

            display_data = filtered[
                [
                    "patient_id",
                    "full_name",
                    "age",
                    "gender",
                    "phone",
                    "room_number",
                    "created_at"
                ]
            ].copy()

            display_data.columns = [
                "Patient ID",
                "Patient Name",
                "Age",
                "Gender",
                "Phone",
                "Room",
                "Registration Date"
            ]

            st.dataframe(
                display_data,
                use_container_width=True,
                hide_index=True
            )

    else:

        st.info("No active patient records available.")

    st.divider()

    # ======================================
    # ARCHIVE PATIENT
    # ======================================

    st.subheader("🗂️ Manage Patient Records")

    st.caption(
        "Archive a patient to remove them from the active list "
        "without deleting their historical records."
    )

    active_patients = get_all_patients()

    if not active_patients.empty:

        patient_options = {
            f"ID: {row.patient_id} | {row.full_name}": row.patient_id
            for row in active_patients.itertuples()
        }

        selected_patient = st.selectbox(
            "Select Patient to Archive",
            list(patient_options.keys())
        )

        confirm_archive = st.checkbox(
            "I confirm that I want to archive this patient."
        )

        if st.button(
            "Archive Patient",
            use_container_width=True
        ):

            if confirm_archive:

                archive_patient(
                    patient_options[selected_patient]
                )

                st.success("Patient archived successfully!")

                st.rerun()

            else:

                st.warning("Please confirm before archiving.")

    else:

        st.info("There are no active patients to archive.")

    # ======================================
    # RESTORE ARCHIVED PATIENT
    # ======================================

    archived_patients = get_all_patients(
        show_archived=True
    )

    if not archived_patients.empty:

        with st.expander("View Archived Patients"):

            archived_options = {
                f"ID: {row.patient_id} | {row.full_name}": row.patient_id
                for row in archived_patients.itertuples()
            }

            selected_archived = st.selectbox(
                "Select Patient to Restore",
                list(archived_options.keys()),
                key="restore_patient"
            )

            if st.button("Restore Patient"):

                restore_patient(
                    archived_options[selected_archived]
                )

                st.success("Patient restored successfully!")

                st.rerun()


# ==========================================
# RUN PAGE
# ==========================================

if __name__ == "__main__":
    show_patient_management()
