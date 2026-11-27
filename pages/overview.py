
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta
from database.db_connection import get_connection


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="MediAssist | Overview",
    page_icon="🏥",
    layout="wide"
)


# ==========================================
# PREMIUM DASHBOARD THEME
# ==========================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #EAF4FF 0%, #F4F8FF 100%);
}

.block-container {
    max-width: 1550px;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}

h1, h2, h3, h4 {
    color: #102F50 !important;
    font-weight: 800 !important;
}

p, label, [data-testid="stCaptionContainer"] {
    color: #45617D !important;
}

[data-testid="stMetric"] {
    background: #FFFFFF;
    border: 1px solid #D5E5F5;
    border-radius: 16px;
    padding: 17px;
    box-shadow: 0 5px 18px rgba(25, 70, 120, 0.07);
}

[data-testid="stMetricLabel"] {
    color: #52708E !important;
    font-size: 14px !important;
    font-weight: 700 !important;
}

[data-testid="stMetricValue"] {
    color: #123B63 !important;
    font-size: 30px !important;
    font-weight: 800 !important;
}

[data-testid="stVerticalBlockBorderWrapper"] {
    background: #FFFFFF;
    border: 1px solid #D6E5F3;
    border-radius: 18px;
    padding: 14px;
    box-shadow: 0 5px 20px rgba(35, 75, 120, 0.06);
}

div[data-testid="stPlotlyChart"] {
    background: #FFFFFF !important;
    border-radius: 12px;
}

hr {
    border-color: #D2E2F1 !important;
}

.dashboard-subtitle {
    color: #52708E;
    font-size: 14px;
}

.robot-card {
    background: linear-gradient(135deg, #123B63, #176B87);
    border-radius: 16px;
    padding: 24px;
    color: white;
    min-height: 170px;
}

.robot-card h3 {
    color: white !important;
    margin-bottom: 8px;
}

.robot-card p {
    color: #E3F2FF !important;
}

.robot-destination {
    color: #FFFFFF;
    font-size: 22px;
    font-weight: 800;
}

.footer-text {
    text-align: center;
    color: #56718B;
    font-size: 13px;
    font-weight: 600;
    padding: 12px;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# CHART DESIGN SETTINGS
# ==========================================

CHART_COLORS = [
    "#2878D0",
    "#16A6A1",
    "#8064D8",
    "#F2A541",
    "#E36B83",
    "#42A5D8"
]


def chart_layout(fig, height=330):

    fig.update_layout(
        template="plotly_white",
        height=height,
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Arial",
            size=12,
            color="#29445F"
        ),
        margin=dict(
            l=20,
            r=20,
            t=35,
            b=25
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.15,
            xanchor="center",
            x=0.5,
            font=dict(color="#45617D")
        ),
        hoverlabel=dict(
            bgcolor="#123B63",
            font_color="#FFFFFF",
            font_size=13
        )
    )

    fig.update_xaxes(
        showgrid=False,
        zeroline=False,
        linecolor="#E1EAF3",
        tickfont=dict(color="#45617D")
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#EDF2F8",
        zeroline=False,
        linecolor="#E1EAF3",
        tickfont=dict(color="#45617D")
    )

    return fig


# ==========================================
# DONUT CHART FUNCTION
# ==========================================

def create_donut(labels, values, colors, title=""):

    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.63,
                marker=dict(
                    colors=colors,
                    line=dict(
                        color="#FFFFFF",
                        width=4
                    )
                ),
                textinfo="percent",
                textposition="inside",
                insidetextfont=dict(
                    color="#FFFFFF",
                    size=13,
                    family="Arial"
                ),
                hovertemplate=(
                    "<b>%{label}</b><br>"
                    "Total: %{value}<br>"
                    "Percentage: %{percent}"
                    "<extra></extra>"
                ),
                sort=False
            )
        ]
    )

    fig.update_layout(
        annotations=[
            dict(
                text=f"<b>{sum(values)}</b>",
                x=0.5,
                y=0.5,
                font=dict(
                    size=27,
                    color="#123B63"
                ),
                showarrow=False
            )
        ]
    )

    return chart_layout(fig, 320)


# ==========================================
# DATABASE DATA
# ==========================================

def get_dashboard_data():

    conn = get_connection()
    cur = conn.cursor()

    today = date.today()
    start_date = today - timedelta(days=13)

    cur.execute("""
        SELECT COUNT(*) FROM patients
        WHERE is_active = 1
    """)
    total_patients = cur.fetchone()[0]

    cur.execute("""
        SELECT COUNT(*) FROM patients
        WHERE is_active = 1
        AND DATE(created_at) = ?
    """, (today.isoformat(),))
    today_registrations = cur.fetchone()[0]

    cur.execute("""
        SELECT gender, COUNT(*) AS total
        FROM patients
        WHERE is_active = 1
        GROUP BY gender
    """)
    gender_rows = cur.fetchall()

    cur.execute("""
        SELECT DATE(created_at) AS day, COUNT(*) AS total
        FROM patients
        WHERE is_active = 1
        AND DATE(created_at) BETWEEN ? AND ?
        GROUP BY DATE(created_at)
        ORDER BY day
    """, (start_date.isoformat(), today.isoformat()))
    registration_rows = cur.fetchall()

    cur.execute("""
        SELECT COUNT(*) FROM patient_requests
    """)
    total_requests = cur.fetchone()[0]

    cur.execute("""
        SELECT status, COUNT(*) AS total
        FROM patient_requests
        GROUP BY status
    """)
    request_status_rows = cur.fetchall()

    cur.execute("""
        SELECT request_type, COUNT(*) AS total
        FROM patient_requests
        GROUP BY request_type
    """)
    request_type_rows = cur.fetchall()

    cur.execute("""
        SELECT COUNT(*) FROM robot_tasks
    """)
    total_robot_tasks = cur.fetchone()[0]

    cur.execute("""
        SELECT status, COUNT(*) AS total
        FROM robot_tasks
        GROUP BY status
    """)
    robot_rows = cur.fetchall()

    cur.execute("""
        SELECT status, current_destination
        FROM robot_status
        WHERE id = 1
    """)
    robot = cur.fetchone()

    conn.close()

    gender_counts = {
        str(r["gender"]): r["total"] for r in gender_rows
    }

    request_status = {
        str(r["status"]): r["total"] for r in request_status_rows
    }

    request_types = {
        str(r["request_type"]): r["total"] for r in request_type_rows
    }

    robot_counts = {
        str(r["status"]): r["total"] for r in robot_rows
    }

    registration_map = {
        r["day"]: r["total"] for r in registration_rows
    }

    days = pd.date_range(
        start=start_date,
        end=today,
        freq="D"
    )

    registration_df = pd.DataFrame({
        "Date": days,
        "Registrations": [
            registration_map.get(
                d.strftime("%Y-%m-%d"), 0
            )
            for d in days
        ]
    })

    return {
        "total_patients": total_patients,
        "today_registrations": today_registrations,
        "total_requests": total_requests,
        "total_robot_tasks": total_robot_tasks,
        "gender": gender_counts,
        "registration": registration_df,
        "request_status": request_status,
        "request_types": request_types,
        "robot_counts": robot_counts,
        "robot_status": robot["status"] if robot else "Unknown",
        "destination": (
            robot["current_destination"] or "Not Assigned"
            if robot else "Not Assigned"
        )
    }


stats = get_dashboard_data()


# ==========================================
# HEADER
# ==========================================

st.title("🏥 MediAssist Dashboard")

st.markdown(
    '<p class="dashboard-subtitle">'
    'Smart Hospital Service & Automation System'
    ' &nbsp; | &nbsp; '
    + date.today().strftime("%d %B %Y")
    + '</p>',
    unsafe_allow_html=True
)


# ==========================================
# TOP STATISTICS
# ==========================================

st.subheader("📊 Hospital Statistics")

a, b, c, d = st.columns(4)

a.metric(
    "Total Patients",
    stats["total_patients"],
    help="Currently active patients"
)

b.metric(
    "Today's Registrations",
    stats["today_registrations"]
)

c.metric(
    "Total Requests",
    stats["total_requests"]
)

d.metric(
    "Robot Tasks",
    stats["total_robot_tasks"]
)


# ==========================================
# HOSPITAL ANALYTICS
# ==========================================

st.divider()
st.header("📈 Hospital Analytics")


# ==========================================
# ROW ONE: GENDER + REGISTRATION
# ==========================================

left, right = st.columns(2, gap="large")


with left:

    with st.container(border=True):

        st.subheader("👥 Gender Analysis")
        st.caption("Active patient distribution")

        gender_labels = ["Male", "Female", "Other"]

        gender_values = [
            stats["gender"].get("Male", 0),
            stats["gender"].get("Female", 0),
            stats["gender"].get("Other", 0)
        ]

        fig = create_donut(
            gender_labels,
            gender_values,
            ["#2878D0", "#E36B83", "#16A6A1"]
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

        m, f, o = st.columns(3)

        m.metric("Male", gender_values[0])
        f.metric("Female", gender_values[1])
        o.metric("Other", gender_values[2])


with right:

    with st.container(border=True):

        st.subheader("📅 Registration Trend")
        st.caption("Patient registration over the last 14 days")

        reg_df = stats["registration"]

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=reg_df["Date"],
                y=reg_df["Registrations"],
                mode="lines+markers",
                name="Registrations",
                line=dict(
                    color="#2878D0",
                    width=4,
                    shape="spline"
                ),
                marker=dict(
                    size=8,
                    color="#16A6A1",
                    line=dict(
                        color="#FFFFFF",
                        width=2
                    )
                ),
                fill="tozeroy",
                fillcolor="rgba(40,120,208,0.10)",
                hovertemplate=(
                    "<b>%{x|%d %b}</b><br>"
                    "Registrations: %{y}"
                    "<extra></extra>"
                )
            )
        )

        fig.update_layout(
            showlegend=False,
            yaxis=dict(
                rangemode="tozero",
                dtick=1
            )
        )

        fig = chart_layout(fig, 360)

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )


# ==========================================
# ROW TWO: REQUEST TYPE + REQUEST STATUS
# ==========================================

st.divider()

left, right = st.columns(2, gap="large")


with left:

    with st.container(border=True):

        st.subheader("📋 Request Type Analysis")
        st.caption("Distribution of patient service requests")

        type_items = list(stats["request_types"].items())

        if type_items:

            type_items.sort(
                key=lambda item: item[1],
                reverse=True
            )

            type_labels = [item[0] for item in type_items]
            type_values = [item[1] for item in type_items]

            fig = create_donut(
                type_labels,
                type_values,
                CHART_COLORS
            )

            st.plotly_chart(
                fig,
                use_container_width=True,
                config={"displayModeBar": False}
            )

        else:
            st.info("No request data available.")


with right:

    with st.container(border=True):

        st.subheader("⏳ Request Status Analysis")
        st.caption("Current progress of patient requests")

        status_order = [
            "Pending",
            "In Progress",
            "Completed"
        ]

        status_values = [
            stats["request_status"].get(s, 0)
            for s in status_order
        ]

        fig = create_donut(
            status_order,
            status_values,
            ["#F2A541", "#2878D0", "#16A67A"]
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

        p, i, c = st.columns(3)

        p.metric("Pending", status_values[0])
        i.metric("In Progress", status_values[1])
        c.metric("Completed", status_values[2])


# ==========================================
# ROBOT OPERATIONS
# ==========================================

st.divider()
st.header("🤖 Robot Operations")


left, right = st.columns(2, gap="large")


with left:

    with st.container(border=True):

        st.subheader("🤖 Robot Current Status")
        st.caption("Live status from the robot database")

        robot_status = str(stats["robot_status"])
        status_lower = robot_status.lower()

        if status_lower == "idle":

            st.success("🟢 ROBOT IDLE")

        elif status_lower == "moving":

            st.info("🔵 ROBOT MOVING")

        else:

            st.warning("🟠 " + robot_status.upper())

        st.markdown(
            f"""
            <div class="robot-card">
                <h3>Robot Control Center</h3>
                <p>Current Destination</p>
                <div class="robot-destination">
                    📍 {stats["destination"]}
                </div>
                <p style="margin-top:15px;">
                    Total Tasks: {stats["total_robot_tasks"]}
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


with right:

    with st.container(border=True):

        st.subheader("🚀 Robot Task Analysis")
        st.caption("Robot task completion overview")

        robot_order = [
            "Pending",
            "In Progress",
            "Completed"
        ]

        robot_values = [
            stats["robot_counts"].get(s, 0)
            for s in robot_order
        ]

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=robot_values,
                y=robot_order,
                orientation="h",
                marker=dict(
                    color=[
                        "#F2A541",
                        "#2878D0",
                        "#16A67A"
                    ],
                    line=dict(
                        color="#FFFFFF",
                        width=2
                    )
                ),
                text=robot_values,
                textposition="outside",
                textfont=dict(
                    color="#29445F",
                    size=13
                ),
                hovertemplate=(
                    "<b>%{y}</b><br>"
                    "Total Tasks: %{x}"
                    "<extra></extra>"
                )
            )
        )

        fig.update_layout(
            showlegend=False,
            xaxis=dict(
                rangemode="tozero",
                dtick=1
            ),
            yaxis=dict(
                autorange="reversed"
            )
        )

        fig = chart_layout(fig, 350)

        st.plotly_chart(
            fig,
            use_container_width=True,
            config={"displayModeBar": False}
        )

        p, i, c = st.columns(3)

        p.metric("Pending", robot_values[0])
        i.metric("In Progress", robot_values[1])
        c.metric("Completed", robot_values[2])


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
