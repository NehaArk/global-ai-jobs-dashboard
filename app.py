import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Global AI Jobs Dashboard 2026", layout="wide")

# ---- Load data ----
@st.cache_data
def load_data():
    df = pd.read_csv("global_ai_jobs_2026.csv")
    return df

df = load_data()

st.title("🌍 Global AI Jobs Dashboard (2026)")
st.write("Explore salaries, roles, and trends across the AI job market worldwide.")

# ---- Sidebar filters ----
st.sidebar.header("Filters")

countries = st.sidebar.multiselect(
    "Country", options=sorted(df["Country"].unique()), default=None
)
industries = st.sidebar.multiselect(
    "Industry", options=sorted(df["Industry"].unique()), default=None
)
experience_levels = st.sidebar.multiselect(
    "Experience Level", options=sorted(df["Experience_Level"].unique()), default=None
)
salary_range = st.sidebar.slider(
    "Salary Range (USD)",
    min_value=int(df["Salary_USD"].min()),
    max_value=int(df["Salary_USD"].max()),
    value=(int(df["Salary_USD"].min()), int(df["Salary_USD"].max())),
)

# ---- Apply filters ----
filtered = df.copy()
if countries:
    filtered = filtered[filtered["Country"].isin(countries)]
if industries:
    filtered = filtered[filtered["Industry"].isin(industries)]
if experience_levels:
    filtered = filtered[filtered["Experience_Level"].isin(experience_levels)]
filtered = filtered[
    (filtered["Salary_USD"] >= salary_range[0]) & (filtered["Salary_USD"] <= salary_range[1])
]

st.sidebar.markdown(f"**{len(filtered):,} jobs match your filters**")

# ---- Key metrics ----
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Jobs", f"{len(filtered):,}")
col2.metric("Avg Salary (USD)", f"${filtered['Salary_USD'].mean():,.0f}" if len(filtered) else "N/A")
col3.metric("Avg Automation Risk", f"{filtered['Automation_Risk_%'].mean():.1f}%" if len(filtered) else "N/A")
col4.metric("Avg Job Satisfaction", f"{filtered['Job_Satisfaction_1_10'].mean():.1f}/10" if len(filtered) else "N/A")

st.divider()

if len(filtered) == 0:
    st.warning("No jobs match your current filters. Try widening your selection.")
else:
    # ---- Salary distribution ----
    st.subheader("Salary Distribution")
    fig_salary = px.histogram(
        filtered, x="Salary_USD", nbins=40,
        title="Distribution of Salaries (USD)",
        labels={"Salary_USD": "Salary (USD)"}
    )
    st.plotly_chart(fig_salary, use_container_width=True)

    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Avg Salary by Experience Level")
        exp_salary = filtered.groupby("Experience_Level")["Salary_USD"].mean().sort_values(ascending=False)
        fig_exp = px.bar(exp_salary, labels={"value": "Avg Salary (USD)", "Experience_Level": "Experience Level"})
        st.plotly_chart(fig_exp, use_container_width=True)

    with col_b:
        st.subheader("Job Count by Industry")
        industry_counts = filtered["Industry"].value_counts().head(10)
        fig_ind = px.bar(industry_counts, labels={"value": "Number of Jobs", "index": "Industry"})
        st.plotly_chart(fig_ind, use_container_width=True)

    col_c, col_d = st.columns(2)

    with col_c:
        st.subheader("Remote Work % vs Job Satisfaction")
        fig_scatter = px.scatter(
            filtered, x="Remote_Work_%", y="Job_Satisfaction_1_10",
            color="Experience_Level", size="Salary_USD",
            hover_data=["Job_Title", "Company"],
            title="Remote Work vs Satisfaction"
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_d:
        st.subheader("Automation Risk by AI Specialization")
        risk_by_spec = filtered.groupby("AI_Specialization")["Automation_Risk_%"].mean().sort_values(ascending=False)
        fig_risk = px.bar(risk_by_spec, labels={"value": "Avg Automation Risk (%)", "AI_Specialization": "Specialization"})
        st.plotly_chart(fig_risk, use_container_width=True)

    # ---- Data table ----
    st.subheader("Browse the Data")
    st.dataframe(
        filtered[[
            "Job_Title", "Company", "Country", "Industry", "Experience_Level",
            "Salary_USD", "Remote_Work_%", "Job_Satisfaction_1_10", "Automation_Risk_%"
        ]],
        use_container_width=True
    )

    # ---- Download filtered data ----
    csv_out = filtered.to_csv(index=False).encode("utf-8")
    st.download_button("Download filtered data as CSV", csv_out, "filtered_ai_jobs.csv", "text/csv")
