
import streamlit as st
import pandas as pd

from datetime import date, datetime
from database.db_connection import get_connection


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="MediAssist | Medical Reports",
    page_icon="🩺",
    layout="wide"
)


# ==========================================
# PROFESSIONAL LIGHT BLUE DESIGN
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #F2F6FC;
}

[data-testid="stAppViewContainer"] {
    background-color: #F2F6FC;
}

[data-testid="stHeader"] {
    background-color: #F2F6FC;
}

/* HEADINGS */

h1, h2, h3 {
    color: #17365D !important;
    font-weight: 800 !important;
}

/* NORMAL TEXT */

.stMarkdown p,
.stCaption {
    color: #344563 !important;
}

/* FORM LABELS */

.stTextInput label,
.stTextArea label,
.stSelectbox label,
.stDateInput label,
.stRadio label,
[data-testid="stWidgetLabel"] p {
    color: #17365D !important;
    font-weight: 700 !important;
    opacity: 1 !important;
}

/* INPUT FIELDS */

.stTextInput input,
.stTextArea textarea,
.stDateInput input {
    background-color: #FFFFFF !important;
    color: #17365D !important;
    -webkit-text-fill-color: #17365D !important;
    border: 1px solid #B8CBE0 !important;
    border-radius: 8px !important;
    opacity: 1 !important;
}

/* PLACEHOLDER TEXT */

.stTextInput input::placeholder,
.stTextArea textarea::placeholder {
    color: #71839A !important;
    -webkit-text-fill-color: #71839A !important;
    opacity: 1 !important;
}

/* SELECTBOX */

[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border: 1px solid #B8CBE0 !important;
    border-radius: 8px !important;
}

[data-baseweb="select"] span,
[data-baseweb="select"] input {
    color: #17365D !important;
    -webkit-text-fill-color: #17365D !important;
    opacity: 1 !important;
}

/* DROPDOWN OPTIONS */

[data-baseweb="popover"] {
    background-color: #FFFFFF !important;
}

[data-baseweb="menu"] {
    background-color: #FFFFFF !important;
}

[data-baseweb="menu"] li {
    color: #17365D !important;
    background-color: #FFFFFF !important;
}

[data-baseweb="menu"] li:hover {
    background-color: #E8F3FC !important;
}

/* DATE INPUT */

[data-testid="stDateInput"] input {
    background-color: #FFFFFF !important;
    color: #17365D !important;
}

/* METRICS */

[data-testid="stMetric"] {
    background-color: #FFFFFF;
    padding: 16px;
    border: 1px solid #DCE6F1;
    border-radius: 12px;
}

[data-testid="stMetricLabel"] {
    color: #526581 !important;
}

[data-testid="stMetricValue"] {
    color: #17365D !important;
}

/* BUTTONS */

.stButton button,
.stFormSubmitButton button {
    background-color: #1677C8 !important;
    color: #FFFFFF !important;
    border-radius: 8px;
    font-weight: 700;
    border: none;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    background-color: #105FA3 !important;
    color: #FFFFFF !important;
}

/* DATAFRAME */

[data-testid="stDataFrame"] {
    border: 1px solid #DCE6F1;
    border-radius: 10px;
}

/* TABS */

.stTabs [data-baseweb="tab"] {
    color: #34516F !important;
    font-weight: 700 !important;
}

.stTabs [aria-selected="true"] {
    color: #1677C8 !important;
}

/* FOOTER */

.footer-text {
    color: #526581;
    text-align: center;
    font-weight: 600;
    padding: 15px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# REPORT CATEGORY AND REPORT TYPE LIST
# ==========================================

REPORT_TYPES = {

    "Pathology / Laboratory": [
        "Blood Test",
        "CBC (Complete Blood Count)",
        "Blood Sugar / Glucose",
        "HbA1c",
        "Lipid Profile",
        "Liver Function Test (LFT)",
        "Kidney Function Test (KFT)",
        "Thyroid Function Test (TFT)",
        "Urine R/E",
        "Urine Culture",
        "Stool Test",
        "Electrolyte Test",
        "Vitamin D Test",
        "Vitamin B12 Test",
        "Dengue Test",
        "Malaria Test",
        "Other / Custom Report"
    ],

    "Radiology / Imaging": [
        "X-Ray",
        "Ultrasound",
        "CT Scan",
        "MRI Scan",
        "Mammography",
        "Doppler Study",
        "Other / Custom Report"
    ],

    "Cardiology": [
        "ECG / EKG",
        "Echocardiogram (ECHO)",
        "TMT / Stress Test",
        "Holter Monitoring",
        "Other / Custom Report"
    ],

    "Neurology": [
        "EEG",
        "EMG",
        "Nerve Conduction Study",
        "Other / Custom Report"
    ],

    "Special Investigations": [
        "Endoscopy",
        "Colonoscopy",
        "Biopsy",
        "Histopathology",
        "Pulmonary Function Test",
        "Other / Custom Report"
    ],

    "Other Department": [
        "Medical Examination",
        "Physical Assessment",
        "Eye Examination",
        "Dental Examination",
        "Other / Custom Report"
    ]
}


# ==========================================
# DATABASE PREPARATION
# ==========================================

def prepare_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("PRAGMA table_info(medical_reports)")

    existing_columns = {
        row["name"] for row in cursor.fetchall()
    }

    required_columns = {
        "checkup_date": "TEXT",
        "doctor_name": "TEXT",
        "result": "TEXT",
        "doctor_notes": "TEXT",
        "report_category": "TEXT"
    }

    for column, data_type in required_columns.items():

        if column not in existing_columns:

            cursor.execute(
                f"ALTER TABLE medical_reports ADD COLUMN {column} {data_type}"
            )

    connection.commit()
    connection.close()


# ==========================================
# LOAD PATIENTS
# ==========================================

def load_patients():

    connection = get_connection()

    patients = pd.read_sql_query("""
        SELECT
            patient_id,
            full_name,
            age,
            gender,
            room_number
        FROM patients
        WHERE is_active = 1
        ORDER BY full_name
    """, connection)

    connection.close()

    return patients


# ==========================================
# LOAD MEDICAL REPORTS
# ==========================================

def load_reports():

    connection = get_connection()

    reports = pd.read_sql_query("""
        SELECT
            m.report_id,
            m.patient_id,
            p.full_name,
            m.report_category,
            m.report_name,
            m.checkup_date,
            m.doctor_name,
            m.result,
            m.doctor_notes,
            m.status,
            m.requested_at

        FROM medical_reports m

        LEFT JOIN patients p
        ON m.patient_id = p.patient_id

        ORDER BY m.report_id DESC
    """, connection)

    connection.close()

    return reports


# ==========================================
# SAVE MEDICAL REPORT
# ==========================================

def save_medical_report(
    patient_id,
    report_category,
    report_name,
    checkup_date,
    doctor_name,
    result,
    doctor_notes,
    status
):

    connection = get_connection()
    cursor = connection.cursor()

    report_data = {

        "patient_id": patient_id,

        "report_category": report_category,

        "report_name": report_name,

        "requested_at": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),

        # Retained for compatibility with the existing database.
        "expected_at": str(checkup_date),

        "checkup_date": str(checkup_date),

        "doctor_name": doctor_name,

        "result": result,

        "doctor_notes": doctor_notes,

        "status": status
    }

    cursor.execute("PRAGMA table_info(medical_reports)")

    available_columns = {
        row["name"] for row in cursor.fetchall()
    }

    insert_columns = [
        column
        for column in report_data
        if column in available_columns
    ]

    column_names = ", ".join(insert_columns)

    placeholders = ", ".join(
        ["?"] * len(insert_columns)
    )

    values = [
        report_data[column]
        for column in insert_columns
    ]

    cursor.execute(
        f"""
        INSERT INTO medical_reports ({column_names})
        VALUES ({placeholders})
        """,
        values
    )

    connection.commit()
    connection.close()


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

try:

    prepare_database()

except Exception as e:

    st.error("Database initialization failed.")
    st.code(str(e))
    st.stop()


# ==========================================
# PAGE HEADER
# ==========================================

st.title("🩺 Medical Report Management")

st.caption(
    "Manage different types of medical reports for hospital patients."
)

st.divider()


# ==========================================
# LOAD DATA
# ==========================================

try:

    patients = load_patients()
    reports = load_reports()

except Exception as e:

    st.error("Unable to load medical report data.")
    st.code(str(e))
    st.stop()


# ==========================================
# REPORT OVERVIEW
# ==========================================

st.subheader("Medical Report Overview")

col1, col2, col3, col4 = st.columns(4)

total_reports = len(reports)

completed_reports = (
    int((reports["status"] == "Completed").sum())
    if not reports.empty else 0
)

pending_reports = (
    int((reports["status"] == "Pending").sum())
    if not reports.empty else 0
)

total_patients = (
    reports["patient_id"].nunique()
    if not reports.empty else 0
)

with col1:
    st.metric("Total Reports", total_reports)

with col2:
    st.metric("Completed", completed_reports)

with col3:
    st.metric("Pending", pending_reports)

with col4:
    st.metric("Patients with Reports", total_patients)


st.divider()


# ==========================================
# MAIN TABS
# ==========================================

tab1, tab2 = st.tabs([
    "➕ Add New Medical Report",
    "📋 All Medical Reports"
])


# ==========================================
# TAB 1: ADD NEW REPORT
# ==========================================

with tab1:

    st.subheader("Add New Medical Report")

    st.info(
        "Select a patient, choose a report category and report type, "
        "then enter the report information."
    )

    if not patients.empty:

        patient_options = {

            f'{row["full_name"]} | ID: {row["patient_id"]}': int(
                row["patient_id"]
            )

            for _, row in patients.iterrows()
        }

        with st.form("medical_report_form"):

            st.markdown("### 1. Patient Information")

            selected_patient = st.selectbox(
                "Select Patient",
                options=list(patient_options.keys())
            )

            st.divider()

            st.markdown("### 2. Report Information")

            report_category = st.selectbox(
                "Select Report Category",
                options=list(REPORT_TYPES.keys())
            )

            available_report_types = REPORT_TYPES[
                report_category
            ]

            selected_report_type = st.selectbox(
                "Select Report Type",
                options=available_report_types
            )

            custom_report_name = ""

            if selected_report_type == "Other / Custom Report":

                custom_report_name = st.text_input(
                    "Enter Custom Report Name",
                    placeholder="Example: Special Blood Investigation"
                )

            col1, col2 = st.columns(2)

            with col1:

                checkup_date = st.date_input(
                    "Checkup / Report Date",
                    value=date.today()
                )

            with col2:

                doctor_name = st.text_input(
                    "Doctor / Specialist Name",
                    placeholder="Enter doctor name"
                )

            st.divider()

            st.markdown("### 3. Report Findings")

            result = st.text_area(
                "Report Result / Findings",
                placeholder="Enter report findings...",
                height=130
            )

            doctor_notes = st.text_area(
                "Doctor's Notes",
                placeholder="Enter additional notes...",
                height=100
            )

            status = st.selectbox(
                "Report Status",
                ["Completed", "Pending"]
            )

            st.divider()

            submit = st.form_submit_button(
                "💾 Save Medical Report",
                use_container_width=True
            )

            if submit:

                final_report_name = (
                    custom_report_name.strip()
                    if selected_report_type == "Other / Custom Report"
                    else selected_report_type
                )

                if not final_report_name:

                    st.error(
                        "Please enter the custom report name."
                    )

                elif not doctor_name.strip():

                    st.error(
                        "Please enter the doctor / specialist name."
                    )

                elif status == "Completed" and not result.strip():

                    st.error(
                        "Please enter report findings for a completed report."
                    )

                else:

                    try:

                        selected_patient_id = patient_options[
                            selected_patient
                        ]

                        save_medical_report(

                            selected_patient_id,

                            report_category,

                            final_report_name,

                            checkup_date,

                            doctor_name.strip(),

                            result.strip(),

                            doctor_notes.strip(),

                            status
                        )

                        st.success(
                            "Medical report saved successfully!"
                        )

                        st.rerun()

                    except Exception as e:

                        st.error(
                            "Unable to save medical report."
                        )

                        st.code(str(e))

    else:

        st.warning(
            "No active patients found. Please register a patient first."
        )


# ==========================================
# TAB 2: ALL MEDICAL REPORTS
# ==========================================

with tab2:

    st.subheader("All Medical Reports")

    if not reports.empty:

        # SEARCH

        search = st.text_input(
            "Search Medical Reports",
            placeholder="Search by patient name, report name or category..."
        )

        filtered_reports = reports.copy()

        if search.strip():

            search_text = search.strip()

            filtered_reports = filtered_reports[
                filtered_reports["full_name"].astype(str).str.contains(
                    search_text,
                    case=False,
                    na=False
                )
                |
                filtered_reports["report_name"].astype(str).str.contains(
                    search_text,
                    case=False,
                    na=False
                )
                |
                filtered_reports["report_category"].astype(str).str.contains(
                    search_text,
                    case=False,
                    na=False
                )
            ]

        # FILTERS

        col1, col2 = st.columns(2)

        with col1:

            category_options = [
                "All Categories"
            ] + sorted(
                filtered_reports["report_category"]
                .dropna()
                .unique()
                .tolist()
            )

            selected_category = st.selectbox(
                "Filter by Category",
                category_options
            )

        with col2:

            status_options = [
                "All Status",
                "Completed",
                "Pending"
            ]

            selected_status = st.selectbox(
                "Filter by Status",
                status_options
            )

        if selected_category != "All Categories":

            filtered_reports = filtered_reports[
                filtered_reports["report_category"]
                == selected_category
            ]

        if selected_status != "All Status":

            filtered_reports = filtered_reports[
                filtered_reports["status"]
                == selected_status
            ]

        # DISPLAY TABLE

        display_columns = [
            "report_id",
            "patient_id",
            "full_name",
            "report_category",
            "report_name",
            "checkup_date",
            "doctor_name",
            "status"
        ]

        display_names = {
            "report_id": "Report ID",
            "patient_id": "Patient ID",
            "full_name": "Patient Name",
            "report_category": "Category",
            "report_name": "Report Type",
            "checkup_date": "Checkup Date",
            "doctor_name": "Doctor",
            "status": "Status"
        }

        st.dataframe(
            filtered_reports[display_columns].rename(
                columns=display_names
            ),
            use_container_width=True,
            hide_index=True
        )

        st.caption(
            f"Showing {len(filtered_reports)} medical report(s)."
        )

        # REPORT DETAILS

        st.divider()

        st.markdown("### View Report Details")

        report_ids = filtered_reports["report_id"].tolist()

        if report_ids:

            selected_report_id = st.selectbox(
                "Select Report ID",
                report_ids
            )

            selected_report = filtered_reports[
                filtered_reports["report_id"]
                == selected_report_id
            ].iloc[0]

            st.markdown("#### Patient and Report Information")

            col1, col2 = st.columns(2)

            with col1:

                st.write(
                    "**Patient:**",
                    selected_report["full_name"]
                )

                st.write(
                    "**Patient ID:**",
                    selected_report["patient_id"]
                )

                st.write(
                    "**Report Category:**",
                    selected_report["report_category"]
                )

                st.write(
                    "**Report Type:**",
                    selected_report["report_name"]
                )

            with col2:

                st.write(
                    "**Checkup Date:**",
                    selected_report["checkup_date"]
                )

                st.write(
                    "**Doctor:**",
                    selected_report["doctor_name"]
                )

                st.write(
                    "**Status:**",
                    selected_report["status"]
                )

            st.markdown("#### Report Findings")

            st.write(
                selected_report["result"]
                if pd.notna(selected_report["result"])
                else "No findings entered."
            )

            st.markdown("#### Doctor's Notes")

            st.write(
                selected_report["doctor_notes"]
                if pd.notna(selected_report["doctor_notes"])
                else "No additional notes."
            )

    else:

        st.info(
            "No medical reports have been added yet. "
            "Use the Add New Medical Report tab to create one."
        )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.markdown("""
<div class="footer-text">
    Developed by Shihab | Stat 40 Batch
</div>
""", unsafe_allow_html=True)
