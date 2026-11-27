
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import time

from database.db_connection import get_connection


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="MediAssist | Hospital Map",
    page_icon="🗺️",
    layout="wide"
)


# ==========================================
# PREMIUM DESIGN
# ==========================================

st.markdown("""
<style>
.stApp {
    background-color: #F3F8FE;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    max-width: 1450px;
}

h1, h2, h3, h4 {
    color: #17365D !important;
    font-weight: 800 !important;
}

p, label, span {
    color: #263B53;
}

[data-testid="stMetric"] {
    background: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #DCE8F5;
}

[data-testid="stDataFrame"] {
    border: 1px solid #DCE8F5;
    border-radius: 12px;
}

.stButton > button {
    background: #1269AE;
    color: white !important;
    border-radius: 9px;
    font-weight: 700;
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
# ANIMATION SETTINGS
# ==========================================

ANIMATION_DURATION = 8
ANIMATION_INTERVAL = 0.2


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_navigation_data():

    connection = get_connection()

    robot = connection.execute("""
        SELECT *
        FROM robot_status
        WHERE id = 1
    """).fetchone()

    active_task = None

    if robot and robot["current_task_id"] is not None:

        active_task = connection.execute("""
            SELECT
                t.task_id,
                t.task_type,
                t.destination,
                t.status,
                p.full_name,
                p.room_number

            FROM robot_tasks t

            LEFT JOIN patient_requests r
            ON t.request_id = r.request_id

            LEFT JOIN patients p
            ON r.patient_id = p.patient_id

            WHERE t.task_id = ?
        """, (robot["current_task_id"],)).fetchone()

    patient_rooms = connection.execute("""
        SELECT DISTINCT room_number
        FROM patients
        WHERE room_number IS NOT NULL
        AND TRIM(room_number) != ''
    """).fetchall()

    connection.close()

    return robot, active_task, patient_rooms


# ==========================================
# HOSPITAL MAP LOCATIONS
# ==========================================

locations = {
    "Main Entrance": (0, 0),
    "Reception": (2, 0),
    "Waiting Area": (4, 0),
    "Medicine Room": (2, 2),
    "Nurse Station": (4, 2),
    "Emergency Room": (0, 4),
    "Laboratory": (2, 4),
    "Report Collection": (4, 4),
    "Robot Parking": (6, 0)
}


# ==========================================
# LOAD DATABASE INFORMATION
# ==========================================

st.title("🗺️ Hospital Navigation System")

st.caption(
    "Smart Hospital Layout & Animated Virtual Robot Navigation"
)

st.divider()

try:

    robot, active_task, patient_rooms = get_navigation_data()

except Exception as error:

    st.error(
        "Unable to load navigation information from database."
    )

    st.exception(error)

    st.stop()


# ==========================================
# ADD PATIENT ROOMS TO MAP
# ==========================================

room_key_by_destination = {}

room_values = sorted(
    {
        str(row["room_number"]).strip()
        for row in patient_rooms
        if row["room_number"] is not None
        and str(row["room_number"]).strip()
    }
)

for index, room_number in enumerate(room_values):

    if room_number in locations:

        room_key_by_destination[room_number] = room_number

        continue

    room_label = f"Patient Room {room_number}"

    locations[room_label] = (
        8,
        4 - (index * 2)
    )

    room_key_by_destination[room_number] = room_label


# ==========================================
# ROBOT STATUS INFORMATION
# ==========================================

robot_moving = (
    robot is not None
    and robot["status"] == "Moving"
)

if robot:

    current_location_value = (
        robot["current_location"]
        or "Robot Parking"
    )

    current_location_value = str(
        current_location_value
    ).strip()

else:

    current_location_value = "Robot Parking"


robot_destination = None
robot_task_id = None

patient_name = "Not Assigned"
task_type = "Not Assigned"


if robot_moving:

    if active_task:

        robot_destination = (
            active_task["destination"]
            or robot["current_destination"]
        )

        robot_task_id = active_task["task_id"]

        patient_name = (
            active_task["full_name"]
            or "Unknown Patient"
        )

        task_type = active_task["task_type"]

    else:

        robot_destination = robot["current_destination"]

        robot_task_id = robot["current_task_id"]


# ==========================================
# LOCATION RESOLVER
# ==========================================

def resolve_location(location_value):

    location_value = str(
        location_value or "Robot Parking"
    ).strip()

    if location_value in room_key_by_destination:

        return room_key_by_destination[location_value]

    if location_value in locations:

        return location_value

    location_label = f"Other Location: {location_value}"

    if location_label not in locations:

        existing_y = [
            position[1]
            for position in locations.values()
        ]

        next_y = min(existing_y) - 2

        locations[location_label] = (
            10,
            next_y
        )

    return location_label


# ==========================================
# RESOLVE START & DESTINATION
# ==========================================

robot_start_key = resolve_location(
    current_location_value
)

if robot_moving:

    destination_value = str(
        robot_destination or "Unknown Room"
    ).strip()

    route_destination = resolve_location(
        destination_value
    )

else:

    available_destinations = [
        name
        for name in locations
        if name != robot_start_key
    ]

    if not available_destinations:

        available_destinations = list(locations.keys())

    route_destination = None


# ==========================================
# NAVIGATION CONTROLS
# ==========================================

st.subheader("📍 Navigation Controls")


if robot_moving:

    st.info(
        "🤖 Active robot task detected. "
        "The 8-second virtual movement animation is enabled."
    )

    st.write(
        f"**Active Task:** #{robot_task_id or 'Unknown'}"
    )

    st.write(
        f"**Patient:** {patient_name}"
    )

    st.write(
        f"**Task Type:** {task_type}"
    )

    st.write(
        f"**Starting Location:** {robot_start_key}"
    )

    st.write(
        f"**Destination:** {route_destination}"
    )

else:

    st.success(
        f"Robot is idle at: {robot_start_key}"
    )

    route_destination = st.selectbox(
        "Select Manual Destination",
        available_destinations
    )

    st.caption(
        "Manual route preview only. "
        "Selecting a destination does not move the robot."
    )


# ==========================================
# MAP COORDINATES
# ==========================================

start_x, start_y = locations[robot_start_key]

dest_x, dest_y = locations[route_destination]


# ==========================================
# CREATE HOSPITAL MAP
# ==========================================

def create_hospital_map(progress):

    robot_x = start_x + (
        dest_x - start_x
    ) * progress

    robot_y = start_y + (
        dest_y - start_y
    ) * progress

    fig = go.Figure()

    # Hospital locations

    for room, (x, y) in locations.items():

        if room == "Robot Parking":

            color = "#64748B"
            symbol = "square"

        elif room == route_destination:

            color = "#DC2626"
            symbol = "star"

        else:

            color = "#2563EB"
            symbol = "circle"

        fig.add_trace(go.Scatter(

            x=[x],
            y=[y],

            mode="markers+text",

            marker=dict(
                size=27,
                color=color,
                symbol=symbol,
                line=dict(
                    width=2,
                    color="white"
                )
            ),

            text=[room],

            textposition="bottom center",

            textfont=dict(
                size=11,
                color="#17365D"
            ),

            name=room,

            hovertemplate=room + "<extra></extra>"

        ))

    # Planned route

    if robot_start_key != route_destination:

        fig.add_trace(go.Scatter(

            x=[start_x, dest_x],
            y=[start_y, dest_y],

            mode="lines",

            line=dict(
                color="#F59E0B",
                width=5,
                dash="dash"
            ),

            name="Planned Route",

            hoverinfo="skip"

        ))

    # Robot marker

    fig.add_trace(go.Scatter(

        x=[robot_x],
        y=[robot_y],

        mode="markers+text",

        marker=dict(
            size=33,
            color="#16A34A",
            symbol="circle",
            line=dict(
                width=3,
                color="white"
            )
        ),

        text=["🤖 Robot"],

        textposition="top center",

        textfont=dict(
            size=13,
            color="#17365D"
        ),

        name="Robot Position"

    ))

    # Map layout

    all_x = [
        position[0]
        for position in locations.values()
    ]

    all_y = [
        position[1]
        for position in locations.values()
    ]

    fig.update_layout(

        height=580,

        plot_bgcolor="white",
        paper_bgcolor="white",

        xaxis=dict(
            visible=False,
            range=[
                min(-1, min(all_x) - 2),
                max(10, max(all_x) + 2)
            ]
        ),

        yaxis=dict(
            visible=False,
            range=[
                min(-2, min(all_y) - 2),
                max(6, max(all_y) + 2)
            ],
            scaleanchor="x",
            scaleratio=1
        ),

        margin=dict(
            l=20,
            r=20,
            t=30,
            b=50
        ),

        legend=dict(
            orientation="h",
            y=-0.12
        )

    )

    return fig


# ==========================================
# ANIMATION STATE
# ==========================================

if "animation_finished_task" not in st.session_state:

    st.session_state.animation_finished_task = None


current_task_key = (
    str(robot_task_id)
    if robot_moving and robot_task_id is not None
    else None
)


# ==========================================
# MAP DISPLAY
# ==========================================

st.divider()

st.subheader("🏥 Live Virtual Hospital Map")

map_placeholder = st.empty()

progress_placeholder = st.empty()

animation_message = st.empty()


# ==========================================
# 8-SECOND ROBOT ANIMATION
# ==========================================

if robot_moving:

    if (
        st.session_state.animation_finished_task
        != current_task_key
    ):

        animation_message.info(
            "🤖 Robot movement started! "
            "Watch the robot travel towards its destination."
        )

        animation_start_time = time.monotonic()

        progress = 0

        while progress < 1:

            elapsed_time = (
                time.monotonic() - animation_start_time
            )

            progress = min(
                elapsed_time / ANIMATION_DURATION,
                1.0
            )

            # Update map position

            fig = create_hospital_map(progress)

            map_placeholder.plotly_chart(
                fig,
                use_container_width=True
            )

            # Update progress bar

            percentage = int(progress * 100)

            progress_placeholder.progress(
                percentage,
                text=(
                    f"Robot Movement Progress: "
                    f"{percentage}%"
                )
            )

            if progress >= 1:

                break

            time.sleep(ANIMATION_INTERVAL)

        # Save animation completion in session

        st.session_state.animation_finished_task = (
            current_task_key
        )

        animation_message.success(
            f"✅ Arrival Simulation Complete! "
            f"Robot has reached {route_destination}."
        )

    else:

        # Keep robot at destination after animation

        map_placeholder.plotly_chart(
            create_hospital_map(1.0),
            use_container_width=True
        )

        progress_placeholder.progress(
            100,
            text="Robot Movement Progress: 100%"
        )

        animation_message.success(
            f"✅ Robot has reached {route_destination}. "
            "Complete the task from Robot Control."
        )

else:

    # Manual preview or idle position

    map_placeholder.plotly_chart(
        create_hospital_map(0),
        use_container_width=True
    )

    progress_placeholder.empty()

    animation_message.info(
        "Robot is stationary. Start a task from Robot Control "
        "to see the 8-second movement animation."
    )


# ==========================================
# MAP LEGEND
# ==========================================

st.caption(
    "Green = Robot | Red = Destination | "
    "Orange = Planned Route | Blue = Hospital Location"
)


# ==========================================
# ROBOT NAVIGATION INFORMATION
# ==========================================

st.divider()

st.subheader("🤖 Robot Navigation Information")

col1, col2, col3 = st.columns(3)

with col1:

    st.metric(
        "Robot Status",
        "Moving" if robot_moving else "Idle"
    )

with col2:

    st.metric(
        "Active Task",
        f"#{robot_task_id}" if robot_task_id else "None"
    )

with col3:

    st.metric(
        "Total Locations",
        len(locations)
    )


if robot_moving:

    if (
        st.session_state.animation_finished_task
        == current_task_key
    ):

        st.success(
            f"Robot has virtually reached {route_destination}. "
            "Please complete the task from Robot Control."
        )

    else:

        st.info(
            f"Robot is travelling from {robot_start_key} "
            f"towards {route_destination}."
        )

else:

    st.success(
        f"Robot is currently located at {robot_start_key}."
    )


# ==========================================
# LOCATION INFORMATION
# ==========================================

st.divider()

st.subheader("📋 Hospital Location Information")

location_data = []

for room, (x, y) in locations.items():

    if room == "Robot Parking":

        room_type = "Robot Parking"

    elif room.startswith("Patient Room"):

        room_type = "Patient Room"

    elif room.startswith("Other Location"):

        room_type = "Other / Custom Location"

    else:

        room_type = "Hospital Department"

    location_data.append({

        "Hospital Location": room,

        "Map X": x,

        "Map Y": y,

        "Location Type": room_type

    })


location_df = pd.DataFrame(location_data)

st.dataframe(
    location_df,
    use_container_width=True,
    hide_index=True
)


# ==========================================
# IMPORTANT INFORMATION
# ==========================================

st.divider()

st.info(
    "This is an educational virtual navigation system. "
    "Robot movement is simulated over 8 seconds on the hospital map. "
    "The saved database location is updated when the task is completed "
    "from Robot Control. This map does not represent actual GPS, "
    "physical robot movement, or measured distance."
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
