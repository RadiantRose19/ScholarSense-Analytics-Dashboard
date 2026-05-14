# ScholarSense - simple student analytics dashboard
# Built with Streamlit + pandas + plotly (course project style)

from datetime import datetime

import joblib
import pandas as pd
import plotly.express as px
import streamlit as st

# --- page setup ---
st.set_page_config(page_title="ScholarSense", layout="wide", page_icon="🎓")

# small style tweak so it looks a bit nicer (optional)
st.markdown(
    """
    <style>
    div[data-testid="stMetricValue"] { font-size: 1.35rem; }
    .block-container { padding-top: 1.2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


# load csv once (cache helps when file is big)
@st.cache_data
def load_data():
    df = pd.read_csv("processed_students.csv")
    # make sure numbers are real numbers not text
    number_cols = [
        "math_score",
        "science_score",
        "english_score",
        "overall_score",
        "attendance_percentage",
        "study_hours",
        "risk_score",
        "age",
    ]
    for col in number_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


@st.cache_resource
def load_model():
    return joblib.load("performance_model.pkl")


students = load_data()
model = load_model()

st.title("ScholarSense Analytics Platform")
st.markdown("Student marks, attendance, study hours, and risk — change sliders on the left to update everything.")

# ============ SIDEBAR ============
st.sidebar.title("Controls")
school_list = ["All"]
for s in sorted(students["school_type"].dropna().unique()):
    school_list.append(s)
school_choice = st.sidebar.selectbox("School type", school_list)

high_score = st.sidebar.slider("High score (top list)", 0, 100, 85, 5)
low_score = st.sidebar.slider("Low score (weak list)", 0, 100, 50, 5)
risk_cut = st.sidebar.slider("Risk level (at-risk list)", 0, 100, 65, 5)

st.sidebar.markdown("---")
st.sidebar.write("Tip: risk can be negative in the file for very safe students.")

# ============ FILTER TABLE ============
df = students.copy()
if school_choice != "All":
    df = df[df["school_type"] == school_choice]

n_students = len(df)

# lists used in tabs
top_df = df[df["overall_score"] >= high_score].sort_values("overall_score", ascending=False)
weak_df = df[df["overall_score"] <= low_score].sort_values("overall_score", ascending=True)
risk_df = df[df["risk_score"] >= risk_cut].sort_values("risk_score", ascending=False)

# who needs help: bad score OR high risk
help_df = df[(df["overall_score"] <= low_score) | (df["risk_score"] >= risk_cut)].copy()
help_df["priority"] = help_df["risk_score"] + (100 - help_df["overall_score"])
help_df = help_df.sort_values("priority", ascending=False)
help_df = help_df.drop(columns=["priority"])

# ============ TOP NUMBERS ============
st.subheader("Summary")
c1, c2, c3 = st.columns(3)
c4, c5, c6 = st.columns(3)
c1.metric("Students shown", str(n_students))
c2.metric("Average overall score", round(df["overall_score"].mean(), 1))
c3.metric("Top performers", len(top_df))
c4.metric("Weak (by score)", len(weak_df))
c5.metric("At-risk (by risk)", len(risk_df))
c6.metric("Needs attention", len(help_df))

st.divider()

# ============ CHARTS ============
st.subheader("Charts")

# chart 1: average score per school type
left, right = st.columns(2)

with left:
    school_table = df.groupby("school_type")["overall_score"].mean()
    school_table = school_table.reset_index()
    school_table = school_table.sort_values("overall_score", ascending=False)
    school_table.columns = ["school_type", "avg_score"]

    fig1 = px.bar(
        school_table,
        x="school_type",
        y="avg_score",
        title="Average overall score by school",
        labels={"avg_score": "Average score", "school_type": "School"},
    )
    fig1.update_traces(marker_color="#2563eb")
    fig1.update_layout(yaxis=dict(range=[0, 100]), showlegend=False)
    st.plotly_chart(fig1, use_container_width=True)

with right:
    # count how many in each score band (simple logic, easy to read)
    band_names = ["0-19", "20-39", "40-59", "60-79", "80-100"]
    band_counts = [0, 0, 0, 0, 0]
    for score in df["overall_score"]:
        if pd.isna(score):
            continue
        if score < 20:
            band_counts[0] = band_counts[0] + 1
        elif score < 40:
            band_counts[1] = band_counts[1] + 1
        elif score < 60:
            band_counts[2] = band_counts[2] + 1
        elif score < 80:
            band_counts[3] = band_counts[3] + 1
        else:
            band_counts[4] = band_counts[4] + 1

    total_for_pct = n_students
    if total_for_pct == 0:
        total_for_pct = 1

    bar_labels = []
    for i in range(len(band_names)):
        cnt = band_counts[i]
        pct = round(100.0 * cnt / total_for_pct, 1)
        bar_labels.append(str(cnt) + " (" + str(pct) + "%)")

    dist = pd.DataFrame({"band": band_names, "count": band_counts, "text": bar_labels})

    fig2 = px.bar(
        dist,
        x="band",
        y="count",
        title="How many students in each score range",
        labels={"count": "Number of students", "band": "Overall score"},
        text="text",
    )
    fig2.update_traces(marker_color="#0f766e", textposition="outside")
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, use_container_width=True)

bottom_left, bottom_right = st.columns(2)

with bottom_left:
    # pie: one label per student, using same numbers as the sliders
    sc = df["overall_score"]
    rk = df["risk_score"]
    is_weak = sc <= low_score
    is_top = sc >= high_score
    is_high_risk = rk >= risk_cut

    # start everyone as mid range, then overwrite smaller groups
    group = pd.Series("Mid-range scores", index=df.index, dtype=object)
    group.loc[is_weak & is_high_risk] = "Low score + high risk"
    group.loc[is_weak & ~is_high_risk] = "Low score, lower risk"
    group.loc[~is_weak & is_top & is_high_risk] = "High score + high risk"
    group.loc[~is_weak & is_top & ~is_high_risk] = "High score, lower risk"

    pie_table = group.value_counts().reset_index()
    pie_table.columns = ["group", "how_many"]
    pie_table = pie_table.sort_values("how_many", ascending=False)

    if pie_table["how_many"].sum() == 0:
        st.info("No data to draw pie chart.")
    else:
        fig3 = px.pie(
            pie_table,
            names="group",
            values="how_many",
            title="Risk vs score (same sliders as sidebar)",
            hole=0.35,
        )
        fig3.update_traces(textinfo="percent+label")
        st.plotly_chart(fig3, use_container_width=True)

with bottom_right:
    # scatter can be heavy with 25000 dots, so we only plot a sample
    if n_students == 0:
        st.info("No rows to plot.")
    else:
        if n_students > 3000:
            small = df.sample(n=3000, random_state=1)
        else:
            small = df

        fig4 = px.scatter(
            small,
            x="study_hours",
            y="overall_score",
            color="attendance_percentage",
            title="Study hours vs overall score (sample if big)",
            labels={"study_hours": "Study hours per day", "overall_score": "Overall score"},
            color_continuous_scale="Blues",
        )
        fig4.update_layout(yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ============ TABLES ============
st.subheader("Student lists")

# columns we want to show (skip if missing)
wanted_cols = [
    "student_id",
    "gender",
    "school_type",
    "math_score",
    "science_score",
    "english_score",
    "overall_score",
    "attendance_percentage",
    "study_hours",
    "risk_score",
    "final_grade",
]
show_cols = []
for col in wanted_cols:
    if col in df.columns:
        show_cols.append(col)


def round_table(t):
    # copy so we do not break the original data
    out = t[show_cols].copy()
    for col in out.columns:
        # "f" means float columns in pandas
        if out[col].dtype.kind == "f":
            out[col] = out[col].round(2)
    return out


t1, t2, t3, t4, t5 = st.tabs(
    ["Top performers", "Weak by score", "At-risk by risk", "Needs attention", "Predict score"]
)

with t1:
    st.write("Students with overall score **greater or equal** to " + str(high_score) + ". Total: **" + str(len(top_df)) + "**")
    if len(top_df) == 0:
        st.warning("Nobody matches.")
    else:
        st.dataframe(round_table(top_df), use_container_width=True, hide_index=True, height=400)
        csv_bytes = round_table(top_df).to_csv(index=False).encode("utf-8")
        st.download_button("Download as CSV", csv_bytes, file_name="top.csv", mime="text/csv")

with t2:
    st.write("Students with overall score **less or equal** to " + str(low_score) + ". Total: **" + str(len(weak_df)) + "**")
    if len(weak_df) == 0:
        st.warning("Nobody matches.")
    else:
        st.dataframe(round_table(weak_df), use_container_width=True, hide_index=True, height=400)
        csv_bytes = round_table(weak_df).to_csv(index=False).encode("utf-8")
        st.download_button("Download as CSV", csv_bytes, file_name="weak.csv", mime="text/csv")

with t3:
    st.write("Students with risk score **greater or equal** to " + str(risk_cut) + ". Total: **" + str(len(risk_df)) + "**")
    if len(risk_df) == 0:
        st.warning("Nobody matches.")
    else:
        st.dataframe(round_table(risk_df), use_container_width=True, hide_index=True, height=400)
        csv_bytes = round_table(risk_df).to_csv(index=False).encode("utf-8")
        st.download_button("Download as CSV", csv_bytes, file_name="risk.csv", mime="text/csv")

with t4:
    st.write("Low score **or** high risk. Sorted so urgent cases appear first. Total: **" + str(len(help_df)) + "**")
    if len(help_df) == 0:
        st.warning("Nobody matches.")
    else:
        st.dataframe(round_table(help_df), use_container_width=True, hide_index=True, height=400)
        csv_bytes = round_table(help_df).to_csv(index=False).encode("utf-8")
        st.download_button("Download as CSV", csv_bytes, file_name="help.csv", mime="text/csv")

with t5:
    st.write("Predict overall score using the saved model (5 inputs).")
    a, b = st.columns(2)
    with a:
        m1 = st.number_input("Math", 0.0, 100.0, 75.0, 0.5)
        m2 = st.number_input("Science", 0.0, 100.0, 70.0, 0.5)
        m3 = st.number_input("English", 0.0, 100.0, 75.0, 0.5)
    with b:
        m4 = st.number_input("Study hours per day", 0.0, 12.0, 4.5, 0.1)
        m5 = st.number_input("Attendance %", 0.0, 100.0, 75.0, 0.5)

    if st.button("Run prediction"):
        answer = model.predict([[m1, m2, m3, m4, m5]])[0]
        st.success("Predicted overall score: **" + str(round(float(answer), 2)) + "**")

st.divider()
st.caption("Rows in file: " + str(len(students)) + " | Last refresh time: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
