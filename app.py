import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from notion_client import Client
import itertools

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
    print("⚠️ No complete rows found in the Notion database.")
else:
    # --- Clean and process ---
    df["Date"] = pd.to_datetime(df["Date"])
    df.sort_values("Date", inplace=True)
    df["Percentage"] = (df["Marks Obtained"] / df["Max Marks"]) * 100

    print("✅ Data Preview:")
    print(df.head())

    # --- Plot ---
    base_palette = {
        "Chemistry": "dodgerblue",
        "Physics": "crimson",
        "Maths": "mediumseagreen",
        "Mathematics": "mediumseagreen"
    }
    all_subjects = df["Subject"].unique()
    default_colors = itertools.cycle(sns.color_palette("Set2"))
    palette = {subj: base_palette.get(subj, next(default_colors)) for subj in all_subjects}

    # Plotting
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x="Date", y="Percentage", hue="Subject", marker="o", palette=palette)
    plt.title("Your Test Score Trends", fontsize=18)  # Removed the emoji to avoid glyph issue
    plt.ylabel("Percentage")
    plt.xlabel("Date")
    plt.ylim(0, 110)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
