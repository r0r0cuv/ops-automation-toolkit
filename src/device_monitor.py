from __future__ import annotations
import os
import platform
import subprocess
from datetime import datetime
import pandas as pd

DEVICES_PATH = os.getenv("DEVICES_PATH", "data/devices.csv")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")

def ping(ip: str) -> bool:
    # Windows uses -n, Linux/Mac uses -c
    count_flag = "-n" if platform.system().lower().startswith("win") else "-c"
    cmd = ["ping", count_flag, "1", ip]
    result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0

def main() -> None:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    devices = pd.read_csv(DEVICES_PATH)

    rows = []
    for _, row in devices.iterrows():
        name = str(row["name"])
        ip = str(row["ip"])
        ok = ping(ip)
        rows.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "name": name,
            "ip": ip,
            "status": "UP" if ok else "DOWN"
        })

    log_path = os.path.join(OUTPUT_DIR, "status_log.csv")
    df = pd.DataFrame(rows)

    # Append if exists, else create
    if os.path.exists(log_path):
        df.to_csv(log_path, mode="a", index=False, header=False)
    else:
        df.to_csv(log_path, index=False)

    # Print summary
    down = df[df["status"] == "DOWN"]
    if len(down) > 0:
        print("⚠️ Devices DOWN:")
        print(down[["name", "ip"]].to_string(index=False))
    else:
        print("✅ All devices UP")

if __name__ == "__main__":
    main()
