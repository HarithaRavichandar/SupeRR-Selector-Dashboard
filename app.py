import streamlit as st
import pandas as pd
import plotly.express as px
import pathlib

# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------

def load_excel_data(excel_path: pathlib.Path):
    """Load the three required sheets from the strict ranking workbook.
    Returns a dict with keys ``batters``, ``bowlers`` and ``methodology``.
    Any failure is reported to the user and stops the app.
    """
    required_sheets = ["Top 10 Batters", "Top 10 Bowlers", "Methodology"]
    try:
        xl = pd.ExcelFile(excel_path, engine="openpyxl")
    except FileNotFoundError:
        st.error(f"❌ Excel file not found at **{excel_path}**.")
        st.stop()
    except Exception as e:
        st.error(f"❌ Unable to read Excel file: {e}")
        st.stop()

    missing = [s for s in required_sheets if s not in xl.sheet_names]
    if missing:
        st.error(
            f"❌ Required sheets missing from workbook: **{', '.join(missing)}**"
        )
        st.stop()

    data = {
        "batters": xl.parse("Top 10 Batters"),
        "bowlers": xl.parse("Top 10 Bowlers"),
        "methodology": xl.parse("Methodology"),
    }
    return data

def format_number(val):
    if pd.isna(val):
        return "-"
    if isinstance(val, (int, float)):
        # Keep three decimal places for scores, two for other floats
        if isinstance(val, float) and not val.is_integer():
            return f"{val:,.3f}"
        return f"{val:,}"
    return str(val)

# ---------------------------------------------------------------------------
# Styling helpers – deep navy with teal accents
# ---------------------------------------------------------------------------

def set_global_style():
    st.markdown(
        """
        <style>
            html, body, .stApp {height: 100vh; margin:0; padding:0; overflow:hidden; background: linear-gradient(135deg, #0a0e2c, #02040a);}
            .stMetric {background-color: #1a2238; border-radius: 6px; padding: 8px; margin:0;}
            .card {background-color: #1a2238; border: 1px solid #2a3b5c; border-radius: 8px; padding: 8px; margin-bottom: 8px;}
            .section-header {color: #00b3b3; font-weight: bold; margin:0;}
            .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {margin:0;}
            #overview {
                display: grid;
                height: 100vh;
                max-height: 100vh;
                overflow: hidden;
                box-sizing: border-box;
                grid-template-rows: 7% 12% 49% 25% 4%;
                gap: 0.5vh;
                padding: 8px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Page renderers
# ---------------------------------------------------------------------------

def render_overview(data):
    st.title("SupeRR Selector")
    st.subheader("IPL & T20I Pressure Performance Analytics (2022 onwards)")

    # KPI cards – exact values from specification
    matches = 853
    balls = 193_988
    eligible_batters = 89
    eligible_bowlers = 102
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Matches Analysed", format_number(matches))
    col2.metric("Ball Records", format_number(balls))
    col3.metric("Eligible Batters", format_number(eligible_batters))
    col4.metric("Eligible Bowlers", format_number(eligible_bowlers))

    # Featured player cards – use explicit column names
    batters = data["batters"].copy()
    bowlers = data["bowlers"].copy()
    top_bat_name = batters.iloc[0]["striker_name"]
    top_bowl_name = bowlers.iloc[0]["bowler_name"]
    top_bat_score = format_number(batters.iloc[0]["score"])
    top_bowl_score = format_number(bowlers.iloc[0]["score"])
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(
            f"""
            <div class='card'>
                <h4>Top Batter</h4>
                <p><strong>{top_bat_name}</strong></p>
                <p>Composite Score: {top_bat_score}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class='card'>
                <h4>Top Bowler</h4>
                <p><strong>{top_bowl_name}</strong></p>
                <p>Composite Score: {top_bowl_score}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Ranking visualisations – horizontal bar charts of the composite score
    fig_bat = px.bar(
        batters,
        x="score",
        y="striker_name",
        orientation="h",
        title="Top 10 Batters – Composite Score",
        labels={"score": "Score", "striker_name": "Batter"},
        color_discrete_sequence=["#00b3b3"],
    )
    fig_bat.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig_bat, use_container_width=True)

    fig_bowl = px.bar(
        bowlers,
        x="score",
        y="bowler_name",
        orientation="h",
        title="Top 10 Bowlers – Composite Score",
        labels={"score": "Score", "bowler_name": "Bowler"},
        color_discrete_sequence=["#00b3b3"],
    )
    fig_bowl.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig_bowl, use_container_width=True)

    # Compact leaderboard preview – first five rows of each sheet
    st.subheader("Leaderboard Preview")
    col_a, col_b = st.columns(2)
    with col_a:
        st.caption("Batters")
        st.dataframe(
            batters.head(5).style.hide(axis="index").format({c: format_number for c in batters.columns})
        )
    with col_b:
        st.caption("Bowlers")
        st.dataframe(
            bowlers.head(5).style.hide(axis="index").format({c: format_number for c in bowlers.columns})
        )

    # Success messages for verification
    st.success(f"🏏 **Top Batter:** {top_bat_name} – {top_bat_score} composite")
    st.success(f"🏏 **Top Bowler:** {top_bowl_name} – {top_bowl_score} composite")

def render_batters(data):
    st.header("Top 10 Batters")
    df = data["batters"].copy()
    # Show full table – hide the index and format numbers
    st.dataframe(df.style.hide(axis="index").format({c: format_number for c in df.columns}))

    # 1️⃣ Horizontal bar – score (already shown in overview, but keep for completeness)
    fig_score = px.bar(
        df,
        x="score",
        y="striker_name",
        orientation="h",
        title="Batter Composite Scores",
        labels={"score": "Score", "striker_name": "Batter"},
        color_discrete_sequence=["#00b3b3"],
    )
    fig_score.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig_score, use_container_width=True)

    # 2️⃣ Grouped bar – pressure SR vs baseline SR
    fig_sr = px.bar(
        df.melt(id_vars=["striker_name"], value_vars=["pressure_sr", "baseline_sr"], var_name="Metric", value_name="Strike Rate"),
        x="Strike Rate",
        y="striker_name",
        color="Metric",
        orientation="h",
        title="Pressure vs Baseline Strike Rate",
        color_discrete_map={"pressure_sr": "#00b3b3", "baseline_sr": "#009999"},
    )
    fig_sr.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig_sr, use_container_width=True)

    # 3️⃣ Scatter – pressure runs vs pressure SR
    fig_scatter = px.scatter(
        df,
        x="pressure_runs",
        y="pressure_sr",
        hover_name="striker_name",
        title="Pressure Runs vs Pressure Strike Rate",
        labels={"pressure_runs": "Pressure Runs", "pressure_sr": "Pressure SR"},
        color_discrete_sequence=["#00b3b3"],
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Player selector for detailed metrics
    player_names = df["striker_name"].tolist()
    selected = st.selectbox("Select a batter for details", player_names)
    if selected:
        row = df[df["striker_name"] == selected].iloc[0]
        st.subheader(f"Details for {selected}")
        for col, val in row.items():
            st.metric(col, format_number(val))

def render_bowlers(data):
    st.header("Top 10 Bowlers")
    df = data["bowlers"].copy()
    st.dataframe(df.style.hide(axis="index").format({c: format_number for c in df.columns}))

    # 1️⃣ Horizontal bar – score
    fig_score = px.bar(
        df,
        x="score",
        y="bowler_name",
        orientation="h",
        title="Bowler Composite Scores",
        labels={"score": "Score", "bowler_name": "Bowler"},
        color_discrete_sequence=["#00b3b3"],
    )
    fig_score.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig_score, use_container_width=True)

    # 2️⃣ Grouped bar – pressure economy vs baseline economy
    fig_econ = px.bar(
        df.melt(id_vars=["bowler_name"], value_vars=["pressure_economy", "baseline_economy"], var_name="Metric", value_name="Economy"),
        x="Economy",
        y="bowler_name",
        color="Metric",
        orientation="h",
        title="Pressure vs Baseline Economy",
        color_discrete_map={"pressure_economy": "#00b3b3", "baseline_economy": "#009999"},
    )
    fig_econ.update_layout(yaxis=dict(categoryorder="total ascending"))
    st.plotly_chart(fig_econ, use_container_width=True)

    # 3️⃣ Scatter – pressure wickets vs pressure economy
    fig_scatter = px.scatter(
        df,
        x="pressure_wickets",
        y="pressure_economy",
        hover_name="bowler_name",
        title="Pressure Wickets vs Pressure Economy",
        labels={"pressure_wickets": "Pressure Wickets", "pressure_economy": "Pressure Economy"},
        color_discrete_sequence=["#00b3b3"],
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Player selector
    player_names = df["bowler_name"].tolist()
    selected = st.selectbox("Select a bowler for details", player_names, key="bowler_selector")
    if selected:
        row = df[df["bowler_name"] == selected].iloc[0]
        st.subheader(f"Details for {selected}")
        for col, val in row.items():
            st.metric(col, format_number(val))

def render_methodology(data):
    st.header("Methodology")
    df = data["methodology"].copy()
    # Present as a clean card with formatted table
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("Pressure‑over definition (Overs 16‑20)")
    st.write("Pressure overs are the final five overs of an innings (overs 16‑20).")
    st.subheader("Baseline‑over definition (Overs 1‑15)")
    st.write("Baseline overs cover the first fifteen overs of an innings (overs 1‑15).")
    st.subheader("Eligibility thresholds")
    st.write(
        "Players are included only if they meet a strict sensitivity threshold (e.g., minimum number of balls/runs)."
    )
    st.subheader("Scoring weights & data‑quality notes")
    st.dataframe(df.style.hide(axis="index"))
    st.caption(
        "The table above shows the exact scoring weights, eligibility thresholds, and data‑quality caveats used in the analysis."
    )
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------

def main():
    st.set_page_config(page_title="SupeRR Selector Dashboard", layout="wide")
    set_global_style()
    excel_path = pathlib.Path(__file__).parent / "data" / "SupeRR_Selector_Final_Rankings.xlsx"
    data = load_excel_data(excel_path)

    # Top navigation (compact)
    view = st.selectbox("", ["Overview", "Batters", "Bowlers", "Methodology"], index=0, key="nav")
    if view == "Overview":
        render_overview(data)
    elif view == "Batters":
        render_batters(data)
    elif view == "Bowlers":
        render_bowlers(data)
    else:
        render_methodology(data)


if __name__ == "__main__":
    main()
