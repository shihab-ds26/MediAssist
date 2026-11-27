
import streamlit as st
import pandas as pd
from database.db_connection import get_connection
from datetime import datetime

st.set_page_config(
    page_title="MediAssist | Patient Requests",
    page_icon="🏥",
    layout="wide"
)

# =====================================
# PROFESSIONAL CSS DESIGN
# =====================================

st.markdown("""
<style>

.stApp {
    background-color: #F2F6FC;
    color: #18324D;
}

h1, h2, h3, h4 {
    color: #12365A !important;
    font-weight: 750 !important;
}

p, label, li,
[data-testid="stWidgetLabel"] * {
    color: #263F59 !important;
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid #D7E3F0;
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0 4px 12px rgba(20,55,90,0.07);
}

[data-testid="stMetricLabel"] {
    color: #425E78 !important;
}

[data-testid="stMetricValue"] {
    color: #12365A !important;
}

.stTextInput input,
.stTextArea textarea,
.stSelectbox div[data-baseweb="select"] {
    background-color: white !important;
    color: #17324D !important;
}

.stButton > button,
.stFormSubmitButton > button {
    background-color: #126B87 !important;
    color: white !important;
    border: none;
    border-radius: 9px;
    min-height: 42px;
    font-weight: 700;
}

.stButton > button:hover {
    background-color: #0D526B !important;
}

[data-testid="stForm"] {
    background: white;
    border: 1px solid #DCE6F0;
    border-radius: 14px;
    padding: 20px;
}

</style>
""", unsafe_allow_html=True)


# =====================================
# DATABASE FUNCTIONS
# =====================================

def get_patients():

    connection = get_connection()

    patients = connection.execute("""
        SELECT patient_id, full_name, room_number
        FROM patients
        WHERE is_active = 1
        ORDER BY patient_id DESC
    """).fetchall()

    connection.close()

    return patients


def get_requests():

    connection = get_connection()

    requests = connection.execute("""
        SELECT
            r.request_id,
            p.full_name,
            r.patient_id,
            r.request_type,
            p.room_number,
            r.priority,
            r.description,
            r.status,
            r.created_at
        FROM patient_requests r
        JOIN patients p
        ON r.patient_id = p.patient_id
        ORDER BY r.request_id DESC
    """).fetchall()

    connection.close()

    return requests


def add_request(patient_id, request_type,
                description, priority):

    connection = get_connection()

    connection.execute("""
        INSERT INTO patient_requests
        (patient_id, request_type, description, priority, status)
        VALUES (?, ?, ?, ?, 'Pending')
    """, (
        patient_id,
        request_type,
        description,
        priority
    ))

    connection.commit()
    connection.close()


def update_request_status(request_id, status):

    connection = get_connection()

    connection.execute("""
        UPDATE patient_requests
        SET status = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE request_id = ?
    """, (status, request_id))

    connection.commit()
    connection.close()


# =====================================
# PAGE HEADER
# =====================================

st.title("Patient Requests")
st.caption("Manage and monitor hospital service requests.")

st.divider()


# =====================================
# REQUEST STATISTICS
# =====================================

requests = get_requests()

total_requests = len(requests)

pending_requests = sum(
    1 for r in requests if r["status"] == "Pending"
)

progress_requests = sum(
    1 for r in requests if r["status"] == "In Progress"
)

completed_requests = sum(
    1 for r in requests if r["status"] == "Completed"
)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Requests", total_requests)
col2.metric("Pending Requests", pending_requests)
col3.metric("In Progress", progress_requests)
col4.metric("Completed", completed_requests)

st.divider()


# =====================================
# NEW REQUEST FORM
# =====================================

st.subheader("Create New Patient Request")
st.caption("Register a service request for an existing patient.")

patients = get_patients()

if patients:

    patient_options = {
        f"Patient #{p['patient_id']} - {p['full_name']} (Room {p['room_number'] or 'N/A'})":
        p["patient_id"]
        for p in patients
    }

    with st.form("new_request_form"):

        selected_patient = st.selectbox(
            "Select Patient",
            options=list(patient_options.keys())
        )

        col1, col2 = st.columns(2)

        with col1:

            request_type = st.selectbox(
                "Request Type",
                [
                    "Medicine Request",
                    "Food Request",
                    "Report Request",
                    "Assistance Request",
                    "Other Request"
                ]
            )

        with col2:

            priority = st.selectbox(
                "Priority",
                ["Normal", "High", "Urgent"]
            )

        description = st.text_area(
            "Request Description",
            placeholder="Enter the patient's service request..."
        )

        submitted = st.form_submit_button(
            "Submit Patient Request",
            use_container_width=True
        )

        if submitted:

            patient_id = patient_options[selected_patient]

            if not description.strip():

                st.error("Please enter a request description.")

            else:

                add_request(
                    patient_id,
                    request_type,
                    description.strip(),
                    priority
                )

                st.success("Patient request registered successfully!")
                st.rerun()

else:

    st.warning(
        "No active patients found. Please register a patient first."
    )


st.divider()


# =====================================
# ALL PATIENT REQUESTS
# =====================================

st.subheader("All Patient Requests")

requests = get_requests()

if requests:

    search = st.text_input(
        "Search Request",
        placeholder="Search by patient name or request ID..."
    )

    status_filter = st.selectbox(
        "Filter by Status",
        ["All", "Pending", "In Progress", "Completed"]
    )

    filtered_requests = []

    for r in requests:

        matches_search = (
            search.strip().lower() in str(r["full_name"]).lower()
            or search.strip() in str(r["request_id"])
            if search.strip()
            else True
        )

        matches_status = (
            status_filter == "All"
            or r["status"] == status_filter
        )

        if matches_search and matches_status:
            filtered_requests.append(r)

    if filtered_requests:

        table_data = []

        for r in filtered_requests:

            table_data.append({
                "Request ID": r["request_id"],
                "Patient Name": r["full_name"],
                "Patient ID": r["patient_id"],
                "Request Type": r["request_type"],
                "Room": r["room_number"] or "N/A",
                "Priority": r["priority"],
                "Status": r["status"],
                "Date": r["created_at"]
            })

        df = pd.DataFrame(table_data)

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        # =====================================
        # UPDATE REQUEST STATUS
        # =====================================

        st.subheader("Update Request Status")

        request_options = {
            f"Request #{r['request_id']} - {r['full_name']} - {r['request_type']}":
            r["request_id"]
            for r in filtered_requests
        }

        with st.form("update_status_form"):

            selected_request = st.selectbox(
                "Select Request",
                options=list(request_options.keys())
            )

            new_status = st.selectbox(
                "New Status",
                ["Pending", "In Progress", "Completed"]
            )

            update_button = st.form_submit_button(
                "Update Request Status",
                use_container_width=True
            )

            if update_button:

                request_id = request_options[selected_request]

                update_request_status(
                    request_id,
                    new_status
                )

                st.success("Request status updated successfully!")
                st.rerun()

    else:

        st.info("No requests match your search.")

else:

    st.info("No patient requests have been registered yet.")

st.divider()

st.caption("MediAssist | Smart Hospital Service & Automation System")
