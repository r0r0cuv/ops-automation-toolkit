from __future__ import annotations
import os
from datetime import datetime
import pandas as pd

INPUT_PATH = os.getenv("INPUT_PATH", "data/sample_daily_ops.xlsx")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")

def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load data (Excel or CSV)
    if INPUT_PATH.lower().endswith(".csv"):
        df = pd.read_csv(INPUT_PATH)
    else:
        df = pd.read_excel(INPUT_PATH)

    # --- Example cleaning / standardization ---
    # Expect columns like: Site, Status, Category, Owner, CreatedDate
    expected_cols = {"Site", "Status", "Category"}
    missing = expected_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df["Status"] = df["Status"].astype(str).str.strip().str.title()
    df["Site"] = df["Site"].astype(str).str.strip()

    # --- Example summary KPIs ---
    total = len(df)
    open_count = int((df["Status"] == "Open").sum())
    closed_count = int((df["Status"] == "Closed").sum())

    by_site = df.groupby("Site").size().reset_index(name="TotalItems").sort_values("TotalItems", ascending=False)
    by_status = df.groupby("Status").size().reset_index(name="Count").sort_values("Count", ascending=False)
    by_category = df.groupby("Category").size().reset_index(name="Count").sort_values("Count", ascending=False)

    summary = pd.DataFrame([
        {"Metric": "Total Items", "Value": total},
        {"Metric": "Open Items", "Value": open_count},
        {"Metric": "Closed Items", "Value": closed_count},
        {"Metric": "Report Date", "Value": datetime.now().strftime("%Y-%m-%d %H:%M")},
    ])

    # --- Export ---
    out_xlsx = os.path.join(OUTPUT_DIR, "daily_summary.xlsx")
    out_csv = os.path.join(OUTPUT_DIR, "daily_summary.csv")

    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        summary.to_excel(writer, index=False, sheet_name="Summary")
        by_site.to_excel(writer, index=False, sheet_name="BySite")
        by_status.to_excel(writer, index=False, sheet_name="ByStatus")
        by_category.to_excel(writer, index=False, sheet_name="ByCategory")

    summary.to_csv(out_csv, index=False)

    print(f"✅ Report created: {out_xlsx}")
    print(f"✅ CSV created: {out_csv}")

if __name__ == "__main__":
    main()
