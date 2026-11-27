
import streamlit as st


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="MediAssist",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==========================================
# REGISTER ALL PAGES
# ==========================================

navigation = st.navigation(
    {
        "MAIN MENU": [
            st.Page(
                "pages/overview.py",
                title="Overview Dashboard",
                icon="🏠",
                default=True
            )
        ],

        "MANAGEMENT": [
            st.Page(
                "pages/patient_management.py",
                title="Patient Management",
                icon="👥"
            ),
            st.Page(
                "pages/patient_requests.py",
                title="Patient Requests",
                icon="📋"
            ),
            st.Page(
                "pages/medical_reports.py",
                title="Medical Report Management",
                icon="🩺"
            ),
            st.Page(
                "pages/reports.py",
                title="Reports & Export",
                icon="📊"
            )
        ],

        "ROBOT & AI": [
            st.Page(
                "pages/robot_control.py",
                title="Robot Control",
                icon="🤖"
            ),
            st.Page(
                "pages/ai_automation.py",
                title="AI & Automation",
                icon="🧠"
            ),
            st.Page(
                "pages/hospital_map.py",
                title="Hospital Map",
                icon="🗺️"
            )
        ]
    },
    position="hidden"
)


# ==========================================
# CUSTOM SIDEBAR DESIGN
# ==========================================

st.markdown("""
<style>

.stApp {
    background-color: #F3F7FC;
}

[data-testid="stSidebar"] {
    background-color: #102C46;
}

[data-testid="stSidebar"] > div:first-child {
    padding: 20px 16px;
}

/* SIDEBAR TEXT */

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: #FFFFFF !important;
}

/* BRAND TITLE */

.brand-title {
    color: #BFE8FF !important;
    font-size: 31px !important;
    font-weight: 900 !important;
    letter-spacing: 0.5px;
    line-height: 1.4;
    opacity: 1 !important;
    text-shadow: none !important;
    -webkit-font-smoothing: antialiased;
}

/* BRAND SUBTITLE */

.brand-subtitle {
    color: #D5EAF8 !important;
    font-size: 13px;
    line-height: 1.6;
    opacity: 1 !important;
}

/* MENU HEADING */

.menu-heading {
    color: #70D6D0;
    font-size: 18px;
    font-weight: 800;
    letter-spacing: 0.7px;
    margin-top: 23px;
    margin-bottom: 10px;
}

/* NAVIGATION LINKS */

[data-testid="stSidebar"] a {
    color: #FFFFFF !important;
    font-size: 16px !important;
    font-weight: 600 !important;
    padding: 10px 12px !important;
    border-radius: 8px;
}

[data-testid="stSidebar"] a:hover {
    background-color: #285777 !important;
}

[data-testid="stSidebar"] a[aria-current="page"] {
    background-color: #167D91 !important;
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] hr {
    border-color: #49647B;
}

/* SIDEBAR STICKY FOOTER */

.sidebar-footer {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 280px;
    background-color: #102C46;
    padding: 14px 12px 18px 12px;
    border-top: 1px solid #49647B;
    text-align: center;
    z-index: 999999;
    box-sizing: border-box;
}

.sidebar-footer-title {
    color: #BFE8FF !important;
    font-size: 14px;
    font-weight: 800;
    letter-spacing: 0.3px;
    margin: 0;
}

.sidebar-footer-subtitle {
    color: #D5EAF8 !important;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.5px;
    margin-top: 4px;
}

/* MAIN CONTENT */

.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# SIDEBAR BRANDING & NAVIGATION
# ==========================================

with st.sidebar:

    st.markdown(
        '<div class="brand-title">🏥 MediAssist</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="brand-subtitle">'
        'Smart Hospital Service & Automation System'
        '</div>',
        unsafe_allow_html=True
    )

    st.divider()

    # MAIN MENU

    st.markdown(
        '<div class="menu-heading">MAIN MENU</div>',
        unsafe_allow_html=True
    )

    st.page_link(
        "pages/overview.py",
        label="Overview Dashboard",
        icon="🏠"
    )

    # MANAGEMENT

    st.markdown(
        '<div class="menu-heading">MANAGEMENT</div>',
        unsafe_allow_html=True
    )

    st.page_link(
        "pages/patient_management.py",
        label="Patient Management",
        icon="👥"
    )

    st.page_link(
        "pages/patient_requests.py",
        label="Patient Requests",
        icon="📋"
    )

    st.page_link(
        "pages/medical_reports.py",
        label="Medical Report Management",
        icon="🩺"
    )

    st.page_link(
        "pages/reports.py",
        label="Reports & Export",
        icon="📊"
    )

    # ROBOT & AI

    st.markdown(
        '<div class="menu-heading">ROBOT & AI</div>',
        unsafe_allow_html=True
    )

    st.page_link(
        "pages/robot_control.py",
        label="Robot Control",
        icon="🤖"
    )

    st.page_link(
        "pages/ai_automation.py",
        label="AI & Automation",
        icon="🧠"
    )

    st.page_link(
        "pages/hospital_map.py",
        label="Hospital Map",
        icon="🗺️"
    )

    # STICKY FOOTER

    st.markdown("""
    <div class="sidebar-footer">
        <div class="sidebar-footer-title">
            Developed by Shihab
        </div>
        <div class="sidebar-footer-subtitle">
            STAT 40 BATCH
        </div>
    </div>
    """, unsafe_allow_html=True)


# ==========================================
# RUN SELECTED PAGE
# ==========================================

navigation.run()
