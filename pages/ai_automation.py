
import streamlit as st
import pandas as pd

from database.db_connection import get_connection


# =====================================
# PAGE CONFIGURATION
# =====================================

st.set_page_config(
    page_title="MediAssist | AI Automation",
    page_icon="🧠",
    layout="wide"
)


# =====================================
# PROFESSIONAL CSS
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
.stSelectbox div[data-baseweb="select"] {
    background-color: white !important;
    color: #17324D !important;
}

.stButton > button {
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

[data-testid="stExpander"] {
    background: white;
    border: 1px solid #D4E0EC;
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)


# =====================================
# DATABASE FUNCTIONS
# =====================================

def get_all_requests():

    connection = get_connection()

    requests = connection.execute("""
        SELECT
            r.request_id,
            r.patient_id,
            p.full_name,
            p.room_number,
            r.request_type,
            r.description,
            r.priority,
            r.status,
            r.created_at

        FROM patient_requests r

        JOIN patients p
        ON r.patient_id = p.patient_id

        ORDER BY r.request_id DESC
    """).fetchall()

    connection.close()

    return requests


def get_unassigned_requests():

    connection = get_connection()

    requests = connection.execute("""
        SELECT
            r.request_id,
            r.patient_id,
            p.full_name,
            p.room_number,
            r.request_type,
            r.description,
            r.priority,
            r.status

        FROM patient_requests r

        JOIN patients p
        ON r.patient_id = p.patient_id

        WHERE r.status != 'Completed'

        AND NOT EXISTS (
            SELECT 1
            FROM robot_tasks t
            WHERE t.request_id = r.request_id
        )

        ORDER BY r.request_id DESC
    """).fetchall()

    connection.close()

    return requests


def get_robot_tasks():

    connection = get_connection()

    tasks = connection.execute("""
        SELECT
            t.task_id,
            t.request_id,
            t.task_type,
            t.destination,
            t.status,
            t.created_at

        FROM robot_tasks t

        ORDER BY t.task_id DESC
    """).fetchall()

    connection.close()

    return tasks


# =====================================
# RULE-BASED CLASSIFICATION
# =====================================

def classify_request(request):

    request_type = request["request_type"].lower()

    description = (
        request["description"] or ""
    ).lower()

    combined_text = request_type + " " + description

    # Medicine Request
    if "medicine" in combined_text:

        return {
            "category": "Medicine Service",
            "task_type": "Medicine Delivery",
            "reason": "Medicine-related service request identified."
        }

    # Food Request
    elif any(word in combined_text for word in [
        "food", "meal", "lunch", "dinner"
    ]):

        return {
            "category": "Food Service",
            "task_type": "Food Delivery",
            "reason": "Food-related service request identified."
        }

    # Report Request
    elif "report" in combined_text:

        return {
            "category": "Report Service",
            "task_type": "Report Delivery",
            "reason": "Medical report service request identified."
        }

    # Assistance Request
    elif any(word in combined_text for word in [
        "assistance", "help", "support"
    ]):

        return {
            "category": "General Assistance",
            "task_type": "Assistance Service",
            "reason": "General assistance request identified."
        }

    # Other Request
    else:

        return {
            "category": "Other Service",
            "task_type": "General Service",
            "reason": "Other hospital service request identified."
        }


# =====================================
# AUTOMATIC ROBOT TASK GENERATION
# =====================================

def generate_robot_task(request, classification):

    connection = get_connection()

    existing_task = connection.execute("""
        SELECT task_id
        FROM robot_tasks
        WHERE request_id = ?
    """, (request["request_id"],)).fetchone()

    if existing_task:

        connection.close()
        return False

    connection.execute("""
        INSERT INTO robot_tasks
        (request_id, task_type, destination, status)
        VALUES (?, ?, ?, 'Pending')
    """, (
        request["request_id"],
        classification["task_type"],
        request["room_number"] or "Unknown Room"
    ))

    connection.commit()
    connection.close()

    return True


# =====================================
# PAGE HEADER
# =====================================

st.title("AI & Automation Center")

st.caption(
    "Analyze hospital service requests and generate robot tasks."
)

st.divider()


# =====================================
# DASHBOARD STATISTICS
# =====================================

all_requests = get_all_requests()
unassigned_requests = get_unassigned_requests()
all_tasks = get_robot_tasks()

total_requests = len(all_requests)

analyzed_requests = total_requests - len(unassigned_requests)

pending_analysis = len(unassigned_requests)

generated_tasks = len(all_tasks)

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Requests",
    total_requests
)

col2.metric(
    "Analyzed Requests",
    analyzed_requests
)

col3.metric(
    "Pending Analysis",
    pending_analysis
)

col4.metric(
    "Generated Robot Tasks",
    generated_tasks
)


st.divider()


# =====================================
# REQUEST ANALYSIS
# =====================================

st.subheader("AI Request Classification")

st.write(
    "Select an unassigned patient request for automatic classification."
)

if unassigned_requests:

    request_options = {
        (
            f"Request #{r['request_id']} | "
            f"{r['full_name']} | "
            f"{r['request_type']} | "
            f"Room {r['room_number'] or 'N/A'}"
        ): r

        for r in unassigned_requests
    }

    selected_label = st.selectbox(
        "Select Patient Request",
        options=list(request_options.keys())
    )

    selected_request = request_options[selected_label]

    with st.container(border=True):

        st.markdown("**Selected Request Details**")

        col1, col2 = st.columns(2)

        with col1:

            st.write(
                f"Patient: {selected_request['full_name']}"
            )

            st.write(
                f"Patient ID: {selected_request['patient_id']}"
            )

            st.write(
                f"Request Type: {selected_request['request_type']}"
            )

        with col2:

            st.write(
                f"Room: {selected_request['room_number'] or 'N/A'}"
            )

            st.write(
                f"Priority: {selected_request['priority']}"
            )

            st.write(
                f"Status: {selected_request['status']}"
            )

        st.write("**Description:**")

        st.write(
            selected_request["description"] or "No description provided."
        )

    if st.button(
        "Analyze Selected Request",
        use_container_width=True
    ):

        result = classify_request(selected_request)

        st.session_state["ai_analysis"] = {
            "request_id": selected_request["request_id"],
            "result": result
        }

    analysis = st.session_state.get("ai_analysis")

    if (
        analysis
        and analysis["request_id"] == selected_request["request_id"]
    ):

        result = analysis["result"]

        st.divider()

        st.success("Request Analysis Completed")

        col1, col2 = st.columns(2)

        with col1:

            st.metric(
                "Identified Category",
                result["category"]
            )

        with col2:

            st.metric(
                "Recommended Robot Task",
                result["task_type"]
            )

        st.info(
            "Analysis Explanation: " + result["reason"]
        )

        st.caption(
            "This is a rule-based educational classification demo, "
            "not a trained medical AI model."
        )

        if st.button(
            "Generate Automatic Robot Task",
            use_container_width=True
        ):

            success = generate_robot_task(
                selected_request,
                result
            )

            if success:

                st.session_state.pop("ai_analysis", None)

                st.success(
                    "Robot task generated successfully!"
                )

                st.rerun()

            else:

                st.warning(
                    "A robot task already exists for this request."
                )

else:

    st.success(
        "All available patient requests have been assigned or completed."
    )


st.divider()


# =====================================
# REQUEST ANALYSIS SUMMARY
# =====================================

st.subheader("Request Analysis Summary")

all_requests = get_all_requests()

if all_requests:

    category_counts = {}

    for request in all_requests:

        result = classify_request(request)

        category = result["category"]

        category_counts[category] = (
            category_counts.get(category, 0) + 1
        )

    chart_data = pd.DataFrame({
        "Service Category": list(category_counts.keys()),
        "Number of Requests": list(category_counts.values())
    })

    st.bar_chart(
        chart_data.set_index("Service Category")
    )

else:

    st.info("No request data is available for analysis.")


st.divider()


# =====================================
# AUTOMATION HISTORY
# =====================================

st.subheader("Automation & Robot Task History")

all_tasks = get_robot_tasks()

if all_tasks:

    history_data = []

    for task in all_tasks:

        history_data.append({

            "Task ID": task["task_id"],

            "Request ID": task["request_id"],

            "Task Type": task["task_type"],

            "Destination": task["destination"],

            "Status": task["status"],

            "Created At": task["created_at"]

        })

    history_df = pd.DataFrame(history_data)

    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True
    )

else:

    st.info("No automated robot tasks have been generated yet.")


st.divider()

st.caption(
    "MediAssist | Smart Hospital Service & Automation System"
)
