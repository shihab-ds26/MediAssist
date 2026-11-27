
import streamlit as st
import pandas as pd
import plotly.express as px

from io import BytesIO
from datetime import datetime
from xml.sax.saxutils import escape

from database.db_connection import get_connection

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)


# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="MediAssist | Reports & Export",
    page_icon="📊",
    layout="wide"
)


# ==========================================
# PROFESSIONAL DESIGN
# ==========================================

st.markdown("""
<style>

.stApp,
[data-testid="stAppViewContainer"] {
    background-color: #F2F6FC;
}

[data-testid="stHeader"] {
    background-color: #F2F6FC;
}

h1, h2, h3, h4 {
    color: #17365D !important;
}

.stMarkdown p {
    color: #344563;
}

/* TAB TEXT VISIBILITY */

.stTabs [data-baseweb="tab"] {
    color: #17365D !important;
    font-weight: 700 !important;
    background-color: transparent !important;
}

.stTabs [data-baseweb="tab"] p {
    color: #17365D !important;
    font-weight: 700 !important;
}

.stTabs [aria-selected="true"] {
    color: #0878C9 !important;
}

.stTabs [aria-selected="true"] p {
    color: #0878C9 !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    background-color: #0878C9 !important;
}

/* METRIC CARDS */

[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border: 1px solid #DCE6F1;
    padding: 18px;
    border-radius: 12px;
}

[data-testid="stMetricLabel"] {
    color: #526581 !important;
}

[data-testid="stMetricValue"] {
    color: #17365D !important;
}

/* INPUTS */

[data-testid="stTextInput"] label,
[data-testid="stSelectbox"] label {
    color: #17365D !important;
    font-weight: 600;
}

/* DATAFRAME */

[data-testid="stDataFrame"] {
    background-color: #FFFFFF;
    border-radius: 10px;
}

/* DOWNLOAD BUTTON */

.stDownloadButton button {
    background-color: #1677C8;
    color: #FFFFFF !important;
    border: none;
    border-radius: 8px;
    font-weight: 600;
}

.stDownloadButton button:hover {
    background-color: #105FA3;
    color: #FFFFFF !important;
}

</style>
""", unsafe_allow_html=True)


# ==========================================
# DATABASE FUNCTIONS
# ==========================================

def load_data():

    connection = get_connection()

    try:

        patients = pd.read_sql_query("""
            SELECT
                patient_id,
                full_name,
                age,
                gender,
                phone,
                room_number,
                created_at,
                is_active
            FROM patients
            ORDER BY patient_id DESC
        """, connection)

        requests = pd.read_sql_query("""
            SELECT
                r.request_id,
                r.patient_id,
                p.full_name,
                r.request_type,
                r.priority,
                r.status,
                r.created_at,
                r.updated_at
            FROM patient_requests r
            LEFT JOIN patients p
                ON r.patient_id = p.patient_id
            ORDER BY r.request_id DESC
        """, connection)

        return patients, requests

    finally:
        connection.close()


# ==========================================
# MEDICAL REPORT DATABASE FUNCTION
# ==========================================

def load_patient_medical_reports(patient_id):

    connection = get_connection()

    try:

        reports = pd.read_sql_query("""
            SELECT
                report_id AS "Report ID",
                report_category AS "Report Category",
                report_name AS "Report Name",
                checkup_date AS "Checkup Date",
                doctor_name AS "Doctor Name",
                result AS "Result / Findings",
                doctor_notes AS "Doctor Notes",
                requested_at AS "Requested At",
                expected_at AS "Expected At",
                status AS "Status"

            FROM medical_reports

            WHERE patient_id = ?

            ORDER BY report_id DESC

        """, connection, params=(patient_id,))

        return reports

    finally:
        connection.close()


# ==========================================
# PDF GENERATOR
# ==========================================

def generate_pdf(title, sections, landscape_mode=False):

    buffer = BytesIO()

    page_size = landscape(A4) if landscape_mode else A4

    doc = SimpleDocTemplate(
        buffer,
        pagesize=page_size,
        rightMargin=28,
        leftMargin=28,
        topMargin=35,
        bottomMargin=35
    )

    styles = getSampleStyleSheet()

    # TITLE STYLE

    title_style = ParagraphStyle(
        "MediAssistTitle",
        parent=styles["Title"],
        textColor=colors.HexColor("#17365D"),
        alignment=TA_CENTER,
        fontSize=19,
        spaceAfter=8
    )

    # SECTION HEADING

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#1677C8"),
        fontSize=12,
        spaceBefore=12,
        spaceAfter=8
    )

    # NORMAL TEXT

    normal_style = ParagraphStyle(
        "NormalCustom",
        parent=styles["Normal"],
        textColor=colors.HexColor("#26364A"),
        fontSize=8,
        leading=11,
        wordWrap="CJK"
    )

    # TABLE HEADER

    header_style = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        textColor=colors.HexColor("#17365D"),
        fontSize=8,
        leading=10,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        wordWrap="CJK"
    )

    elements = []

    # REPORT TITLE

    elements.append(
        Paragraph("MediAssist", title_style)
    )

    elements.append(
        Paragraph(
            escape(title),
            heading_style
        )
    )

    elements.append(
        Paragraph(
            "Hospital Service Management System",
            normal_style
        )
    )

    elements.append(Spacer(1, 8))

    elements.append(
        Paragraph(
            "Generated: " + datetime.now().strftime(
                "%d %B %Y, %I:%M %p"
            ),
            normal_style
        )
    )

    # ======================================
    # TABLE GENERATION
    # ======================================

    for section_title, dataframe in sections:

        elements.append(Spacer(1, 14))

        elements.append(
            Paragraph(
                escape(section_title),
                heading_style
            )
        )

        if dataframe.empty:

            elements.append(
                Paragraph(
                    "No records available.",
                    normal_style
                )
            )

            continue

        table_data = []

        # TABLE HEADER

        table_data.append([
            Paragraph(
                escape(str(column)),
                header_style
            )
            for column in dataframe.columns
        ])

        # TABLE BODY

        for _, row in dataframe.iterrows():

            row_data = []

            for value in row:

                if pd.isna(value):
                    value = ""

                row_data.append(
                    Paragraph(
                        escape(str(value)).replace("\n", "<br/>"),
                        normal_style
                    )
                )

            table_data.append(row_data)

        # ==================================
        # COLUMN WIDTH MANAGEMENT
        # ==================================

        column_count = len(dataframe.columns)

        if column_count == 10:

            # Medical Report Table

            col_widths = [
                42,   # Report ID
                75,   # Category
                80,   # Report Name
                60,   # Checkup Date
                75,   # Doctor Name
                100,  # Result
                110,  # Doctor Notes
                75,   # Requested At
                75,   # Expected At
                55    # Status
            ]

        else:

            available_width = (
                page_size[0] - doc.leftMargin - doc.rightMargin
            )

            col_widths = [
                available_width / column_count
                for _ in range(column_count)
            ]

        pdf_table = Table(
            table_data,
            colWidths=col_widths,
            repeatRows=1,
            hAlign="LEFT"
        )

        pdf_table.setStyle(TableStyle([

            # HEADER BACKGROUND

            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#DCEEFF")
            ),

            # HEADER TEXT

            (
                "TEXTCOLOR",
                (0, 0),
                (-1, 0),
                colors.HexColor("#17365D")
            ),

            # BODY BACKGROUND

            (
                "BACKGROUND",
                (0, 1),
                (-1, -1),
                colors.HexColor("#F2F6FC")
            ),

            # BODY TEXT

            (
                "TEXTCOLOR",
                (0, 1),
                (-1, -1),
                colors.HexColor("#26364A")
            ),

            # HEADER ALIGNMENT

            (
                "ALIGN",
                (0, 0),
                (-1, 0),
                "CENTER"
            ),

            # GRID

            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.5,
                colors.HexColor("#C5D6E8")
            ),

            # VERTICAL ALIGNMENT

            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE"
            ),

            # PADDING

            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                5
            ),

            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                8
            ),

        ]))

        elements.append(pdf_table)

    # FOOTER

    elements.append(Spacer(1, 25))

    elements.append(
        Paragraph(
            "Developed by Shihab | Stat 40 Batch",
            normal_style
        )
    )

    doc.build(elements)

    buffer.seek(0)

    return buffer.getvalue()


# ==========================================
# PAGE HEADER
# ==========================================

st.title("📊 Reports & Export")

st.caption(
    "Individual patient records and hospital service request reports."
)

st.divider()


# ==========================================
# MAIN APPLICATION
# ==========================================

try:

    patients, requests = load_data()

    # ======================================
    # OVERVIEW
    # ======================================

    st.subheader("Hospital Overview")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Patients", len(patients))

    with col2:

        active_count = (
            int((patients["is_active"] == 1).sum())
            if not patients.empty else 0
        )

        st.metric("Active Patients", active_count)

    with col3:
        st.metric("Total Requests", len(requests))

    st.divider()

    # ======================================
    # TABS
    # ======================================

    tab1, tab2, tab3 = st.tabs([
        "👥 Patient Reports",
        "📋 Request Reports",
        "📥 Export Center"
    ])

    # ======================================
    # TAB 1: PATIENT REPORTS
    # ======================================

    with tab1:

        st.subheader("Individual Patient Information")

        st.caption(
            "Search for a patient to view their individual information and complete medical report details."
        )

        if not patients.empty:

            search_patient = st.text_input(
                "Search Patient by Name or Patient ID",
                placeholder="Enter patient name or ID...",
                key="patient_view_search"
            )

            filtered_patients = patients.copy()

            if search_patient.strip():

                search_value = search_patient.strip().lower()

                filtered_patients = patients[
                    patients["full_name"].astype(str).str.lower().str.contains(
                        search_value,
                        na=False
                    )
                    |
                    patients["patient_id"].astype(str).str.contains(
                        search_value,
                        na=False
                    )
                ]

            if not filtered_patients.empty:

                patient_options = {
                    f'{row["full_name"]} | ID: {row["patient_id"]}':
                    int(row["patient_id"])
                    for _, row in filtered_patients.iterrows()
                }

                selected_label = st.selectbox(
                    "Select Patient",
                    list(patient_options.keys()),
                    key="patient_view_select"
                )

                selected_id = patient_options[selected_label]

                selected_patient = patients[
                    patients["patient_id"] == selected_id
                ].iloc[0]

                st.divider()

                st.markdown("### Patient Information")

                c1, c2, c3 = st.columns(3)

                c1.metric(
                    "Patient ID",
                    int(selected_patient["patient_id"])
                )

                c2.metric(
                    "Patient Name",
                    selected_patient["full_name"]
                )

                c3.metric(
                    "Age",
                    selected_patient["age"]
                )

                st.write(
                    "**Gender:**",
                    selected_patient["gender"]
                )

                st.write(
                    "**Room Number:**",
                    selected_patient["room_number"]
                )

                st.write(
                    "**Registration Date:**",
                    selected_patient["created_at"]
                )

                st.divider()

                st.markdown("### Medical Report Details")

                medical_reports = load_patient_medical_reports(
                    selected_id
                )

                if not medical_reports.empty:

                    st.dataframe(
                        medical_reports,
                        use_container_width=True,
                        hide_index=True
                    )

                else:

                    st.info(
                        "No medical report requests found for this patient."
                    )

            else:

                st.warning("No matching patient found.")

        else:

            st.info("No patient records available.")

    # ======================================
    # TAB 2: REQUEST REPORTS
    # ======================================

    with tab2:

        st.subheader("Patient Request Analysis")

        if not requests.empty:

            pending = int(
                (requests["status"] == "Pending").sum()
            )

            in_progress = int(
                (requests["status"] == "In Progress").sum()
            )

            completed = int(
                (requests["status"] == "Completed").sum()
            )

            c1, c2, c3 = st.columns(3)

            c1.metric("Pending", pending)
            c2.metric("In Progress", in_progress)
            c3.metric("Completed", completed)

            st.divider()

            st.markdown("### Request Type Distribution")

            request_counts = (
                requests["request_type"]
                .value_counts()
                .reset_index()
            )

            request_counts.columns = [
                "Request Type",
                "Total Requests"
            ]

            fig = px.bar(
                request_counts,
                x="Request Type",
                y="Total Requests",
                text="Total Requests",
                color="Request Type",
                title="Hospital Service Request Analysis"
            )

            fig.update_layout(
                plot_bgcolor="#FFFFFF",
                paper_bgcolor="#FFFFFF",
                font=dict(
                    color="#17365D",
                    size=13
                ),
                title_font=dict(
                    color="#17365D",
                    size=19
                ),
                xaxis=dict(
                    title="Request Type",
                    showgrid=False,
                    color="#344563"
                ),
                yaxis=dict(
                    title="Number of Requests",
                    showgrid=True,
                    gridcolor="#E8EEF6",
                    color="#344563",
                    rangemode="tozero"
                ),
                showlegend=False,
                margin=dict(
                    l=20,
                    r=20,
                    t=65,
                    b=20
                )
            )

            fig.update_traces(
                textposition="outside"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            st.divider()

            st.markdown("### All Patient Requests")

            st.dataframe(
                requests,
                use_container_width=True,
                hide_index=True
            )

        else:

            st.info("No patient requests available.")

    # ======================================
    # TAB 3: EXPORT CENTER
    # ======================================

    with tab3:

        st.subheader("📥 Individual Patient PDF Export")

        st.write(
            "Search for a patient and download that patient's information and complete medical report details."
        )

        st.divider()

        if not patients.empty:

            search_export = st.text_input(
                "🔍 Search Patient by Name or Patient ID",
                placeholder="Type patient name or ID...",
                key="patient_export_search"
            )

            export_patients = patients.copy()

            if search_export.strip():

                search_value = search_export.strip().lower()

                export_patients = patients[
                    patients["full_name"].astype(str).str.lower().str.contains(
                        search_value,
                        na=False
                    )
                    |
                    patients["patient_id"].astype(str).str.contains(
                        search_value,
                        na=False
                    )
                ]

            if not export_patients.empty:

                export_options = {
                    f'{row["full_name"]} | ID: {row["patient_id"]}':
                    int(row["patient_id"])
                    for _, row in export_patients.iterrows()
                }

                selected_export_label = st.selectbox(
                    "Select Patient for PDF",
                    list(export_options.keys()),
                    key="patient_export_select"
                )

                export_patient_id = export_options[
                    selected_export_label
                ]

                export_patient = patients[
                    patients["patient_id"] == export_patient_id
                ].iloc[0]

                export_medical_reports = load_patient_medical_reports(
                    export_patient_id
                )

                st.success(
                    f"Selected Patient: {export_patient['full_name']}"
                )

                st.write(
                    f"Patient ID: {export_patient_id}"
                )

                st.write(
                    f"Medical Reports Found: {len(export_medical_reports)}"
                )

                patient_info = pd.DataFrame([{
                    "Patient ID": export_patient["patient_id"],
                    "Name": export_patient["full_name"],
                    "Age": export_patient["age"],
                    "Gender": export_patient["gender"],
                    "Room": export_patient["room_number"],
                    "Registration Date": export_patient["created_at"]
                }])

                patient_pdf = generate_pdf(
                    "Individual Patient Report",
                    [
                        ("Patient Information", patient_info),
                        ("Complete Medical Report Details", export_medical_reports)
                    ],
                    landscape_mode=True
                )

                st.download_button(
                    label="⬇️ Download Individual Patient PDF",
                    data=patient_pdf,
                    file_name=f"MediAssist_Patient_{export_patient_id}_Report.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            else:

                st.warning("No matching patient found.")

        else:

            st.info("No patient records available.")

        st.divider()

        # ==================================
        # ALL PATIENT REQUEST REPORT PDF
        # ==================================

        st.subheader("📋 All Patient Request Report")

        st.write(
            "Download the combined service request report for all patients."
        )

        request_pdf_data = requests[
            [
                "request_id",
                "patient_id",
                "full_name",
                "request_type",
                "priority",
                "status",
                "created_at"
            ]
        ].copy()

        request_pdf = generate_pdf(
            "All Patient Request Report",
            [
                ("Hospital Service Requests", request_pdf_data)
            ],
            landscape_mode=True
        )

        st.download_button(
            label="⬇️ Download All Request Reports PDF",
            data=request_pdf,
            file_name="MediAssist_All_Request_Report.pdf",
            mime="application/pdf",
            use_container_width=True
        )


except Exception as e:

    st.error("Unable to generate reports.")

    st.code(str(e))


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.markdown("""
<div style="
    text-align:center;
    color:#526581;
    padding:12px;
    font-weight:600;
">
    Developed by Shihab | Stat 40 Batch
</div>
""", unsafe_allow_html=True)
