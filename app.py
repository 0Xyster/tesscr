import pandas as pd
import plotly.express as px
from notion_client import Client
import itertools
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

    st.success("✅ Data Preview:")
    st.write(df.head())

    # --- Plot with Plotly for better UX ---
    fig = px.line(df, x="Date", y="Percentage", color="Subject",
                  title="Your Test Score Trends",
                  labels={"Percentage": "Test Percentage", "Date": "Date"},
                  template="plotly_dark")

    # Customizing the layout for better UX
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Percentage",
        title="Your Test Score Trends 📈",
        plot_bgcolor="black",
        paper_bgcolor="#2E2E2E",  # Dark background
        font=dict(color="white"),  # White text
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='gray'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='gray'),
        showlegend=True,
        legend=dict(title="Subject", title_font=dict(family="Arial", size=14))
    )

    # Ensure the plot is shown properly
    st.plotly_chart(fig)
