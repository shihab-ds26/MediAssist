import plotly.express as px
from datetime import datetime
import streamlit as st
import pandas as pd

from database.db_connection import get_connection


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="MediAssist | Robot Control",
    page_icon="🤖",
    layout="wide"
)


# ==========================================
# PREMIUM NATIVE STREAMLIT DESIGN
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #F1F6FC;
}

.block-container {
    max-width: 1450px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

h1, h2, h3, h4 {
    color: #123B63 !important;
    font-weight: 800 !important;
}

p, label, span {
    color: #34536F;
}

[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #D8E7F5;
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 3px 12px rgba(20, 65, 105, 0.05);
}

[data-testid="stMetricLabel"] {
    color: #55738F !important;
    font-weight: 700 !important;
}

[data-testid="stMetricValue"] {
    color: #123B63 !important;
    font-weight: 800 !important;
}

div[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF;
    border: 1px solid #D8E7F5;
    border-radius: 16px;
    padding: 12px;
}

.stButton > button,
.stFormSubmitButton > button {
    background: #1269AE;
    color: #FFFFFF !important;
    border: none;
    border-radius: 9px;
    font-weight: 700;
    min-height: 42px;
}

.stButton > button:hover,
.stFormSubmitButton > button:hover {
    background: #084D86;
    color: #FFFFFF !important;
}

div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div {
    background: #FFFFFF !important;
    border-color: #C8DCEC !important;
    border-radius: 9px !important;
}

.stProgress > div > div {
    background-color: #DCEAF7;
}

.stProgress > div > div > div {
    background-color: #1685D4;
}

[data-testid="stDataFrame"] {
    border: 1px solid #D8E7F5;
    border-radius: 12px;
}

hr {
    border-color: #D8E7F5;
}

.footer-text {
    text-align: center;
    color: #66819A;
    font-size: 13px;
    font-weight: 700;
    padding: 18px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# DATABASE FUNCTIONS
# ==========================================

def get_robot_status():

    connection = get_connection()

    robot = connection.execute("""
        SELECT *
        FROM robot_status
        WHERE id = 1
    """).fetchone()

    connection.close()

    return robot


def get_available_requests():

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


def get_all_tasks():

    connection = get_connection()

    tasks = connection.execute("""
        SELECT
            t.task_id,
            t.request_id,
            t.task_type,
            t.destination,
            t.status,
            t.created_at,
            t.started_at,
            t.completed_at,
            p.full_name

        FROM robot_tasks t

        LEFT JOIN patient_requests r
        ON t.request_id = r.request_id

        LEFT JOIN patients p
        ON r.patient_id = p.patient_id

        ORDER BY t.task_id DESC
    """).fetchall()

    connection.close()

    return tasks


def create_robot_task(request):

    connection = get_connection()

    connection.execute("""
        INSERT INTO robot_tasks
        (request_id, task_type, destination, status)
        VALUES (?, ?, ?, 'Pending')
    """, (
        request["request_id"],
        request["request_type"],
        request["room_number"] or "Unknown Room"
    ))

    connection.commit()
    connection.close()


# ==========================================
# START ROBOT TASK
# ==========================================

def start_robot_task(task_id):

    connection = get_connection()

    robot = connection.execute("""
        SELECT *
        FROM robot_status
        WHERE id = 1
    """).fetchone()

    if not robot or robot["status"] == "Moving":
        connection.close()
        return False

    task = connection.execute("""
        SELECT *
        FROM robot_tasks
        WHERE task_id = ?
    """, (task_id,)).fetchone()

    if not task or task["status"] != "Pending":
        connection.close()
        return False

    # Start selected task
    connection.execute("""
        UPDATE robot_tasks
        SET status = 'In Progress',
            started_at = CURRENT_TIMESTAMP
        WHERE task_id = ?
    """, (task_id,))

    # Update robot status
    # Previous current_location remains unchanged.
    connection.execute("""
        UPDATE robot_status
        SET status = 'Moving',
            current_task_id = ?,
            current_destination = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = 1
    """, (
        task_id,
        task["destination"]
    ))

    connection.commit()
    connection.close()

    return True


# ==========================================
# COMPLETE ROBOT TASK
# ==========================================

def complete_robot_task(task_id):

    connection = get_connection()

    robot = connection.execute("""
        SELECT *
        FROM robot_status
        WHERE id = 1
    """).fetchone()

    if not robot or robot["current_task_id"] != task_id:
        connection.close()
        return False

    # Get completed task destination
    task = connection.execute("""
        SELECT request_id, destination
        FROM robot_tasks
        WHERE task_id = ?
    """, (task_id,)).fetchone()

    if not task:
        connection.close()
        return False

    # Mark robot task completed
    connection.execute("""
        UPDATE robot_tasks
        SET status = 'Completed',
            completed_at = CURRENT_TIMESTAMP
        WHERE task_id = ?
    """, (task_id,))

    # Update patient request
    if task["request_id"] is not None:

        connection.execute("""
            UPDATE patient_requests
            SET status = 'Completed',
                updated_at = CURRENT_TIMESTAMP
            WHERE request_id = ?
        """, (task["request_id"],))

    # IMPORTANT:
    # Save destination as robot's latest location.
    # Do not reset location to Robot Parking.

    connection.execute("""
        UPDATE robot_status
        SET status = 'Idle',
            current_task_id = NULL,
            current_location = ?,
            current_destination = NULL,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = 1
    """, (task["destination"],))

    connection.commit()
    connection.close()

    return True


# ==========================================
# PAGE HEADER
# ==========================================

st.title("🤖 Robot Control Center")

st.caption(
    "Virtual Hospital Robot Simulation & Task Management System"
)

st.divider()


# ==========================================
# LOAD DATA
# ==========================================

robot = get_robot_status()
tasks = get_all_tasks()

total_tasks = len(tasks)

pending_tasks = sum(
    1 for task in tasks
    if task["status"] == "Pending"
)

progress_tasks = sum(
    1 for task in tasks
    if task["status"] == "In Progress"
)

completed_tasks = sum(
    1 for task in tasks
    if task["status"] == "Completed"
)


# ==========================================
# PERFORMANCE OVERVIEW
# ==========================================

st.subheader("📊 Robot Performance Overview")

a, b, c, d = st.columns(4)

a.metric("Total Tasks", total_tasks)
b.metric("Pending Tasks", pending_tasks)
c.metric("In Progress", progress_tasks)
d.metric("Completed Tasks", completed_tasks)

st.divider()


# ==========================================
# VIRTUAL ROBOT SIMULATION
# ==========================================

st.header("🚀 Virtual Robot Simulation")

left, right = st.columns([1.5, 1], gap="large")


# ==========================================
# HOSPITAL NAVIGATION
# ==========================================

with left:

    with st.container(border=True):

        st.subheader("🏥 Hospital Navigation")

        if robot:

            current_location = (
                robot["current_location"]
                or "Robot Parking"
            )

            current_destination = (
                robot["current_destination"]
                or "No Active Destination"
            )

            if robot["status"] == "Moving":

                st.info("🔵 ROBOT IN MOTION")

                progress_value = 55

                robot_stage = (
                    f"Robot is travelling from "
                    f"{current_location} towards "
                    f"{current_destination}"
                )

            else:

                st.success("🟢 ROBOT IDLE")

                progress_value = 0

                robot_stage = (
                    f"Robot is currently located at "
                    f"{current_location}"
                )

        else:

            current_location = "Unknown"

            current_destination = "Not Assigned"

            progress_value = 0

            robot_stage = "Robot information unavailable"

            st.error("Robot status unavailable.")

        st.divider()

        start_col, robot_col, destination_col = st.columns(3)

        with start_col:

            st.markdown("## 🏥")

            st.markdown("**CURRENT LOCATION**")

            st.caption(current_location)

        with robot_col:

            st.markdown("## 🤖")

            st.markdown("**ROBOT**")

            if robot and robot["status"] == "Moving":
                st.caption("Moving")
            else:
                st.caption("Idle")

        with destination_col:

            st.markdown("## 📍")

            st.markdown("**DESTINATION**")

            st.caption(current_destination)

        st.progress(
            progress_value,
            text=f"Illustrative Progress: {progress_value}%"
        )

        st.caption(robot_stage)

        st.caption(
            "Virtual corridor simulation. "
            "This is not actual robot movement or measured distance."
        )


# ==========================================
# ROBOT INFORMATION
# ==========================================

with right:

    with st.container(border=True):

        st.subheader("📡 Robot Information")

        if robot:

            if robot["status"] == "Moving":

                st.info("Robot Status: Active")

            else:

                st.success("Robot Status: Idle")

            current_task = (
                robot["current_task_id"]
                if robot["current_task_id"] is not None
                else "No Active Task"
            )

            destination = (
                robot["current_destination"]
                or "No Active Destination"
            )

            location = (
                robot["current_location"]
                or "Robot Parking"
            )

            st.metric(
                "Current Task ID",
                current_task
            )

            st.markdown("---")

            st.markdown("**📍 LAST KNOWN LOCATION**")

            st.info(str(location))

            st.markdown("**🎯 CURRENT DESTINATION**")

            st.info(str(destination))

            st.markdown("**⚙️ SYSTEM STATUS**")

            st.write("Database: Connected")

            st.write("Robot Controller: Online")

            st.write("Simulation: Active")

        else:

            st.error("Robot information not found.")


st.divider()


# ==========================================
# CREATE ROBOT TASK
# ==========================================

st.header("📋 Create Robot Task")

st.caption(
    "Convert an existing patient request into a robot task."
)

available_requests = get_available_requests()

if available_requests:

    request_options = {
        (
            f"Request #{r['request_id']} | "
            f"{r['full_name']} | "
            f"{r['request_type']} | "
            f"Room {r['room_number'] or 'N/A'}"
        ): r
        for r in available_requests
    }

    with st.form("create_robot_task_form"):

        selected_request = st.selectbox(
            "Select Patient Request",
            options=list(request_options.keys())
        )

        create_button = st.form_submit_button(
            "➕ Create Robot Task",
            use_container_width=True
        )

        if create_button:

            request = request_options[selected_request]

            create_robot_task(request)

            st.success("Robot task created successfully!")

            st.rerun()

else:

    st.info(
        "No new patient requests are available for robot task creation."
    )


st.divider()


# ==========================================
# ROBOT TASK MANAGEMENT
# ==========================================

st.header("🎮 Robot Task Management")

st.caption(
    "Select a task to start or complete the virtual robot operation."
)

tasks = get_all_tasks()

if tasks:

    task_options = {
        (
            f"Task #{t['task_id']} | "
            f"{t['full_name'] or 'Unknown Patient'} | "
            f"{t['task_type']} | "
            f"{t['status']}"
        ): t
        for t in tasks
        if t["status"] in ["Pending", "In Progress"]
    }

    if task_options:

        selected_task_label = st.selectbox(
            "Select Robot Task",
            options=list(task_options.keys())
        )

        selected_task = task_options[selected_task_label]

        col1, col2 = st.columns(2, gap="large")

        with col1:

            with st.container(border=True):

                st.caption("SELECTED TASK")

                st.subheader(
                    f"Task #{selected_task['task_id']}"
                )

                st.write(
                    f"**Patient:** "
                    f"{selected_task['full_name'] or 'Unknown'}"
                )

                st.write(
                    f"**Task Type:** {selected_task['task_type']}"
                )

                st.write(
                    f"**Destination:** {selected_task['destination']}"
                )

                st.write(
                    f"**Status:** {selected_task['status']}"
                )

        with col2:

            with st.container(border=True):

                st.caption("ROBOT ACTIONS")

                if selected_task["status"] == "Pending":

                    if st.button(
                        "▶ Start Robot Task",
                        use_container_width=True
                    ):

                        success = start_robot_task(
                            selected_task["task_id"]
                        )

                        if success:
                            st.success("Robot task started!")
                        else:
                            st.error(
                                "Robot is busy or task cannot be started."
                            )

                        st.rerun()

                elif selected_task["status"] == "In Progress":

                    st.info(
                        "Robot is currently processing this task."
                    )

                    if st.button(
                        "✓ Complete Robot Task",
                        use_container_width=True
                    ):

                        success = complete_robot_task(
                            selected_task["task_id"]
                        )

                        if success:
                            st.success(
                                "Robot task completed! "
                                "Latest location saved successfully."
                            )
                        else:
                            st.error(
                                "This task is not the robot's current task."
                            )

                        st.rerun()

    else:

        st.info("No pending or active robot tasks.")

else:

    st.info("No robot tasks have been created yet.")


st.divider()


# ==========================================
# ROBOT TASK HISTORY & ANALYTICS
# ==========================================

st.header("📜 Robot Task History & Analytics")

tasks = get_all_tasks()

if tasks:

    history_data = []
    activity_data = []
    completed_dates = []

    for task in tasks:

        created_at = pd.to_datetime(
            task["created_at"],
            errors="coerce"
        )

        started_at = pd.to_datetime(
            task["started_at"],
            errors="coerce"
        )

        completed_at = pd.to_datetime(
            task["completed_at"],
            errors="coerce"
        )

        # Calculate task duration

        duration = None

        if (
            pd.notna(started_at)
            and pd.notna(completed_at)
        ):

            duration = (
                completed_at - started_at
            ).total_seconds()

        if duration is not None and duration >= 0:
            duration_text = f"{duration:.0f} seconds"
        else:
            duration_text = "Not Available"

        # Task history

        history_data.append({

            "Task ID": task["task_id"],

            "Patient": task["full_name"] or "Unknown",

            "Task Type": task["task_type"],

            "Destination": task["destination"],

            "Status": task["status"],

            "Started At": (
                str(task["started_at"])
                if task["started_at"]
                else "Not Started"
            ),

            "Completed At": (
                str(task["completed_at"])
                if task["completed_at"]
                else "Not Completed"
            ),

            "Duration": duration_text

        })

        # Activity log: task created

        if pd.notna(created_at):

            activity_data.append({

                "Task ID": task["task_id"],
                "Activity": "Task Created",
                "Date & Time": created_at,
                "Patient": task["full_name"] or "Unknown"

            })

        # Activity log: task started

        if pd.notna(started_at):

            activity_data.append({

                "Task ID": task["task_id"],
                "Activity": "Robot Started",
                "Date & Time": started_at,
                "Patient": task["full_name"] or "Unknown"

            })

        # Activity log: task completed

        if pd.notna(completed_at):

            activity_data.append({

                "Task ID": task["task_id"],
                "Activity": "Task Completed",
                "Date & Time": completed_at,
                "Patient": task["full_name"] or "Unknown"

            })

            completed_dates.append(
                completed_at.date()
            )

    # ======================================
    # COMPLETION TIME ANALYTICS
    # ======================================

    st.subheader("⏱️ Task Completion Time")

    durations = []

    for task in tasks:

        started = pd.to_datetime(
            task["started_at"],
            errors="coerce"
        )

        completed = pd.to_datetime(
            task["completed_at"],
            errors="coerce"
        )

        if pd.notna(started) and pd.notna(completed):

            seconds = (
                completed - started
            ).total_seconds()

            if seconds >= 0:
                durations.append(seconds)

    avg_duration = (
        sum(durations) / len(durations)
        if durations else 0
    )

    duration_col1, duration_col2, duration_col3 = st.columns(3)

    duration_col1.metric(
        "Measured Tasks",
        len(durations)
    )

    duration_col2.metric(
        "Average Completion Time",
        f"{avg_duration:.1f} sec"
        if durations else "N/A"
    )

    duration_col3.metric(
        "Total Completed Tasks",
        completed_tasks
    )

    st.caption(
        "Completion time is calculated from database start and completion timestamps. "
        "It is not the same as the 8-second map animation duration."
    )

    st.divider()

    
    # ======================================
    # DAILY TASK PERFORMANCE - DONUT CHART
    # ======================================

    st.subheader("📊 Robot Task Performance")

    performance_data = pd.DataFrame({

        "Task Status": [
            "Completed",
            "Pending",
            "In Progress"
        ],

        "Total Tasks": [
            completed_tasks,
            pending_tasks,
            progress_tasks
        ]

    })

    performance_data = performance_data[
        performance_data["Total Tasks"] > 0
    ]

    if not performance_data.empty:

        fig_performance = px.pie(

            performance_data,

            names="Task Status",

            values="Total Tasks",

            hole=0.62,

            color="Task Status",

            color_discrete_map={
                "Completed": "#16A34A",
                "Pending": "#F59E0B",
                "In Progress": "#1685D4"
            }

        )

        fig_performance.update_traces(

            textposition="inside",

            textinfo="label+value+percent",

            textfont=dict(
                size=13,
                color="white"
            ),

            marker=dict(
                line=dict(
                    color="white",
                    width=3
                )
            )

        )

        fig_performance.update_layout(

            height=420,

            paper_bgcolor="white",

            plot_bgcolor="white",

            font=dict(
                color="#17365D",
                size=13
            ),

            showlegend=True,

            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.12,
                xanchor="center",
                x=0.5
            ),

            margin=dict(
                l=30,
                r=30,
                t=35,
                b=65
            ),

            annotations=[
                dict(
                    text=f"<b>{total_tasks}</b><br>Total Tasks",
                    x=0.5,
                    y=0.5,
                    showarrow=False,
                    font=dict(
                        size=19,
                        color="#17365D"
                    )
                )
            ]

        )

        st.plotly_chart(
            fig_performance,
            use_container_width=True
        )

    else:

        st.info(
            "No robot tasks available for performance analysis yet."
        )

    # ======================================
    # COMPLETE TASK HISTORY
    # ======================================

    st.subheader("📋 Complete Task History")

    history_df = pd.DataFrame(history_data)

    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    # ======================================
    # ROBOT ACTIVITY LOG
    # ======================================

    st.subheader("🕒 Robot Activity Log")

    if activity_data:

        activity_df = pd.DataFrame(activity_data)

        activity_df = activity_df.sort_values(
            "Date & Time",
            ascending=False
        )

        activity_df["Date & Time"] = (
            activity_df["Date & Time"]
            .dt.strftime("%Y-%m-%d %H:%M:%S")
        )

        st.dataframe(
            activity_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No robot activity has been recorded yet."
        )

else:

    st.info(
        "Robot task history is currently empty."
    )


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.markdown(
    '<div class="footer-text">'
    'Developed by Shihab | Stat 40 Batch'
    '</div>',
    unsafe_allow_html=True
)
