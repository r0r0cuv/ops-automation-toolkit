from __future__ import annotations
import os
import pandas as pd

ASSETS_PATH = os.getenv("ASSETS_PATH", "data/assets.csv")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
LOW_STOCK_THRESHOLD = int(os.getenv("LOW_STOCK_THRESHOLD", "5"))

def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df = pd.read_csv(ASSETS_PATH)

    # duplicates by asset_id
    dupes = df[df.duplicated(subset=["asset_id"], keep=False)].sort_values("asset_id")

    # low stock
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
    low = df[df["quantity"] < LOW_STOCK_THRESHOLD].sort_values("quantity")

    out_xlsx = os.path.join(OUTPUT_DIR, "inventory_audit.xlsx")
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Inventory")
        low.to_excel(writer, index=False, sheet_name="LowStock")
        dupes.to_excel(writer, index=False, sheet_name="Duplicates")

    print(f"✅ Inventory audit created: {out_xlsx}")
    print(f"Low stock items (<{LOW_STOCK_THRESHOLD}): {len(low)}")
    print(f"Duplicate asset IDs: {len(dupes)}")

if __name__ == "__main__":
    main()
