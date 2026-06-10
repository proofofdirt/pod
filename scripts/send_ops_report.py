"""
POD-ORCH-01 — Send oracle pipeline status report to ops@proofofdirt.com
Run once after each agent session to notify ops supervisor.

Usage: python send_ops_report.py
"""

import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / "pod-agents" / ".env.devnet", override=False)
except ImportError:
    pass

SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.mail.yahoo.com")
SMTP_PORT   = int(os.environ.get("SMTP_PORT", 465))
FROM_EMAIL  = os.environ.get("OPS_EMAIL", "ops@proofofdirt.com")
FROM_PASS   = os.environ.get("OPS_IMAP_APP_PASSWORD")
TO_EMAIL    = "ops@proofofdirt.com"

SUBJECT = "[ORACLE-AI] SAR Pipeline Ready — 8 Jobs Queued, Awaiting Manual GEE Run"

BODY = """
POD-ORACLE-01 · Session Report
================================
Date: 2026-05-31
Agent: POD-ORACLE-01 (Oracle / AI Agent)
Reported to: ops@proofofdirt.com

COMPLETED
---------
✅ Oracle schema enrichment — all 8 Desafarm plots updated
   File: pod-agents/shared-memory/plots/desafarm-all-plots.geojson
   Plots: ETH-001 through ETH-008
   Schema: plot_id, producer_id, crop_type, country_code, season_year,
           planting_window_start/end, t1_claimed_plow_date, oracle_status

✅ Oracle job queue — 8 SAR plow detection jobs created
   Location: pod-agents/shared-memory/oracle-jobs/
   Model: SAR_PLOW_T1 (Sentinel-1, confidence threshold ≥ 0.72)
   Claimed plow date: 2026-04-10
   Jobs: JOB-20260410-ETH001 through JOB-20260410-ETH008

✅ GEE scripts ready (service account auth wired to .env.devnet)
   - pod-oracle/sar/gee_sar_plow.js  (GEE Code Editor)
   - pod-oracle/sar/gee_sar_plow.py  (Python API, primary)
   - pod-oracle/sar/run_oracle.py    (agent runner entry point)

✅ NDVI scripts ready (T2, queued for post-planting July 2026)
   - pod-oracle/ndvi/gee_ndvi_desafarm.js
   - pod-oracle/ndvi/gee_ndvi_pipeline.py

BLOCKED — ACTION REQUIRED
--------------------------
⚠ GEE oracle run needs to execute on your machine (sandbox unavailable).

Run from cmd/terminal:

  cd ProofOfDirt\\pod-oracle\\sar
  pip install -r requirements.txt
  python run_oracle.py --job ..\\..\\pod-agents\\shared-memory\\oracle-jobs\\JOB-20260410-ETH001.json

  # Or run all 8 at once (bash):
  for job in ../../pod-agents/shared-memory/oracle-jobs/JOB-20260410-*.json; do
    python run_oracle.py --job "$job"
  done

Results will write to: pod-agents/shared-memory/oracle-results/

⚠ Confirm GEE service account key exists at:
  C:\\Users\\bekam\\.config\\pod-agents\\gee-service-account.json

NEXT SESSION
------------
Once results are in oracle-results/:
1. POD-ORACLE-01 evaluates PASS/FAIL per plot
2. PASS → POD-CAP-01 triggers T1 tranche release
3. FAIL/UNCERTAIN → POD-COMM-01 flags for SME review
4. T2 NDVI run queued for July 2026 (post-planting)

—
POD-ORCH-01 · Proof of Dirt Orchestrator
ops@proofofdirt.com
"""


def send():
    if not FROM_PASS:
        print("ERROR: OPS_IMAP_APP_PASSWORD not set in .env.devnet")
        return

    msg = MIMEMultipart("alternative")
    msg["Subject"] = SUBJECT
    msg["From"]    = FROM_EMAIL
    msg["To"]      = TO_EMAIL
    msg.attach(MIMEText(BODY, "plain"))

    ctx = ssl.create_default_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=ctx) as server:
        server.login(FROM_EMAIL, FROM_PASS)
        server.sendmail(FROM_EMAIL, TO_EMAIL, msg.as_string())
    print(f"✅ Report sent → {TO_EMAIL}")


if __name__ == "__main__":
    send()
