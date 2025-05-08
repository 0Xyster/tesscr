import pandas as pd
import plotly.express as px
from notion_client import Client
import streamlit as st

# --- Notion Config ---
NOTION_TOKEN = "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"
DATABASE_ID = "1ecd1e330efa80e7a93afe010dabaf0d"
notion = Client(auth=NOTION_TOKEN)

# --- Fetch from Notion ---
results = notion.databases.query(database_id=DATABASE_ID)["results"]
data = []

for row in results:
    props = row.get("properties", {})
    title_list = props.get("Test Name", {}).get("title") or []
    date_obj = props.get("Date Taken", {}).get("date") or {}
    subject_obj = props.get("Subject", {}).get("select") or {}
    marks_obt = props.get("Marks Obtained", {}).get("number")
    max_marks = props.get("Max Marks", {}).get("number")

    if not (title_list and date_obj.get("start") and subject_obj.get("name") and
            marks_obt is not None and max_marks is not None):
        continue

    data.append({
        "Test Name": title_list[0].get("plain_text", ""),
        "Date": date_obj.get("start"),
        "Subject": subject_obj.get("name"),
        "Marks Obtained": marks_obt,
        "Max Marks": max_marks
    })

df = pd.DataFrame(data)

if df.empty:
    st.warning("⚠️ No complete rows found in the Notion database.")
else:
    # --- Clean and process ---
    df["Date"] = pd.to_datetime(df["Date"])
    df.sort_values("Date", inplace=True)
    df["Percentage"] = (df["Marks Obtained"] / df["Max Marks"]) * 100

    # Add origin (0%) for each subject at earliest date
    earliest_date = df["Date"].min()
    subjects = df["Subject"].unique()

    origin_rows = pd.DataFrame({
        "Date": [earliest_date] * len(subjects),
        "Subject": subjects,
        "Percentage": [0] * len(subjects),
        "Test Name": ["Origin"] * len(subjects),
        "Marks Obtained": [0] * len(subjects),
        "Max Marks": [1] * len(subjects),  # To avoid division by zero
    })

    df_full = pd.concat([origin_rows, df], ignore_index=True)
    df_full.sort_values("Date", inplace=True)

    # --- Plot only the graph ---
    fig = px.line(df_full, x="Date", y="Percentage", color="Subject", markers=True,
                  title="Your Test Score Trends 📈",
                  labels={"Percentage": "Percentage", "Date": "Date"},
                  template="plotly_dark")

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Percentage",
        plot_bgcolor="black",
        paper_bgcolor="#2E2E2E",
        font=dict(color="white"),
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='gray'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='gray'),
        showlegend=True,
        legend=dict(title="Subject", title_font=dict(family="Arial", size=14))
    )

    st.plotly_chart(fig)
