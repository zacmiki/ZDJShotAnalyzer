# ============================================================
# FILE: app.py
# ============================================================

import streamlit as st
from analysis_engine import ShotData, ShotAnalysis

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Golf Shot Analyzer",
    layout="wide"
)

# ============================================================
# TITLE
# ============================================================

st.title("🏌️ Golf Shot Analyzer")

# ============================================================
# INPUT SECTION
# ============================================================

st.markdown("## 📥 Shot Data Input")

col1, col2, col3 = st.columns(3)

# ============================================================
# COLUMN 1
# ============================================================

with col1:

    club = st.selectbox(
        "Club",
        [
            "Driver",
            "3W",
            "5I",
            "6I",
            "7I",
            "8I",
            "9I",
            "PW"
        ]
    )

    ball_speed = st.number_input(
        "Ball Speed (mph)",
        value=100.0,
        step=0.1,
        format="%.1f"

    )

    launch_angle = st.number_input(
        "Vertical Launch Angle (°)",
        value=18.0,
        step=0.1,
        format="%.1f"
    )

# ============================================================
# COLUMN 2
# ============================================================

with col2:

    spin = st.number_input(
        "Spin (rpm)",
        value=6000
    )

    spin_axis = st.number_input(
        "Spin Axis (°)",
        value=0.0,
        step=0.1,
        format="%.1f"
    )

    horizontal_angle = st.number_input(
        "Horizontal Launch Angle (°)",
        value=0.0,
        step=0.1,
        format="%.1f"
    )

# ============================================================
# COLUMN 3
# ============================================================

with col3:

    peak_height = st.number_input(
        "Peak Height (yd)",
        value=25.0,
        step=0.1,
        format="%.1f"
    )

    descent_angle = st.number_input(
        "Descent Angle (°)",
        value=45.0,
        step=0.1,
        format="%.1f"
    )

    carry = st.number_input(
        "Carry Distance (yd)",
        value=140.0,
        step=0.1,
        format="%.1f"
    )

# ============================================================
# ANALYZE BUTTON
# ============================================================

analyze = st.button("🚀 Analyze Shot")

# ============================================================
# ANALYSIS
# ============================================================

if analyze:

    # ========================================================
    # CREATE SHOT OBJECT
    # ========================================================

    shot = ShotData(
        club=club,
        launch_angle=launch_angle,
        peak_height=peak_height,
        descent_angle=descent_angle,
        spin=spin,
        spin_axis=spin_axis,
        ball_speed=ball_speed,
        horizontal_angle=horizontal_angle,
        carry=carry
    )

    # ========================================================
    # RUN ANALYSIS
    # ========================================================

    analysis = ShotAnalysis(shot)

    analysis.compute_all()

    r = analysis.results

    # ========================================================
    # RESULTS HEADER
    # ========================================================

    st.markdown("---")
    st.markdown("# 📊 Analysis Results")

    # ========================================================
    # METRICS CARDS
    # ========================================================

    c1, c2, c3 = st.columns(3)

    # ========================================================
    # COLUMN 1
    # ========================================================

    with c1:

        st.metric(
            "Estimated Club Speed",
            f"{r['club_speed']} mph"
        )

        st.metric(
            "Dynamic Loft",
            f"{r['dynamic_loft']['estimate']}°"
        )

        st.metric(
            "Attack Angle",
            f"{r['attack_angle']['estimate']}°"
        )

    # ========================================================
    # COLUMN 2
    # ========================================================

    with c2:

        st.metric(
            "Face Angle",
            f"{r['face_angle']['estimate']}°"
        )

        st.metric(
            "Club Path",
            f"{r['club_path']['estimate']}°"
        )

        st.metric(
            "Face-to-Path",
            f"{r['face_to_path']['estimate']}°"
        )

    # ========================================================
    # COLUMN 3
    # ========================================================

    with c3:

        st.metric(
            "Smash Factor",
            f"{r['smash_factor']['estimate']}"
        )

        st.metric(
            "Carry Efficiency",
            f"{r['carry_efficiency']['value']}"
        )

        st.metric(
            "Efficiency Rating",
            r['carry_efficiency']['rating']
        )

    # ========================================================
    # BALL FLIGHT / TRAJECTORY / FLAGS
    # ========================================================

    st.markdown("---")

    t1, t2, t3 = st.columns(3)

    # ========================================================
    # BALL FLIGHT
    # ========================================================

    with t1:

        st.markdown("## 🏌️ Ball Flight")

        st.info(
            f"""
            ### Start Direction

            {analysis.start_direction}
            """
        )

        st.info(
            f"""
            ### Curvature

            {analysis.severity} {analysis.curvature}
            """
        )

        st.info(
            f"""
            ### Shot Shape

            {analysis.shot_shape}
            """
        )

    # ========================================================
    # TRAJECTORY
    # ========================================================

    with t2:

        st.markdown("## ✈️ Trajectory")

        st.success(
            f"""
            ### Flight Window

            {analysis.flight_window}

            ### Miss Pattern

            {analysis.miss_pattern}
            """
        )

    # ========================================================
    # FLAGS + CONFIDENCE
    # ========================================================

    with t3:

        st.markdown("## 🎯 Conf. Levels")

        for k, v in analysis.confidence.items():

            st.markdown(
                f"""
                <div style="
                    background-color:#5e548e;
                        padding:12px;
                        border-radius:12px;
                        margin-bottom:12px;
                        color:white;
                ">

                <b>{k}</b><br>
                {v}

                </div>
                """,
                unsafe_allow_html=True
            )


    st.markdown("## 🚨 Coaching Flags")

    if len(analysis.flags) == 0:

        st.success("No major coaching flags detected.")

    else:

        for flag in analysis.flags:

            st.warning(flag)

st.markdown("---")

st.markdown("""
Program to analyze the shot parameters from ZDJ setup to interpret
the numbers.

### Extracted Values:
- Dynamic Loft
- Attack Angle
- Face Angle
- Club Path
- Face-to-Path
- Shot Shape
- Coaching Tendencies

Zac™️

HAPPY GOLFING !
""")
