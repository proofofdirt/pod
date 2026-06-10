"""
POD Oracle — SAR Plow Detection Runner
POD-ORACLE-01 entry point for automated agent execution.

Accepts a JSON job file from the Orchestrator, runs GEE plow detection,
writes the result to shared-memory/oracle-results/ for downstream agents.

Job file format (see pod-agents/shared-memory/oracle-jobs/):
{
  "job_id":       "JOB-20260410-ETH001",
  "plot_id":      "ETH-001",
  "claimed_date": "2026-04-10",
  "model":        "SAR_PLOW_T1",
  "requested_by": "POD-ORCH-01"
}

Usage (agent):
    python run_oracle.py --job path/to/job.json

Usage (manual fallback):
    python run_oracle.py --plot ETH-001 --date 2026-04-10
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────

REPO_ROOT      = Path(__file__).parent.parent.parent          # ProofOfDirt/
ENV_FILE       = REPO_ROOT / "pod-agents" / ".env.devnet"
RESULTS_DIR    = REPO_ROOT / "pod-agents" / "shared-memory" / "oracle-results"
JOBS_DIR       = REPO_ROOT / "pod-agents" / "shared-memory" / "oracle-jobs"

# ── Auth helper ───────────────────────────────────────────────────────────────

def init_gee() -> None:
    """Authenticate GEE via service account from .env.devnet."""
    try:
        from dotenv import load_dotenv
        load_dotenv(ENV_FILE, override=False)
    except ImportError:
        pass  # fall back to already-set env vars

    import ee

    sa       = os.environ.get("GEE_SERVICE_ACCOUNT")
    key_file = os.environ.get("GEE_KEY_FILE")
    project  = os.environ.get("GEE_PROJECT")

    if sa and key_file and Path(key_file).exists():
        creds = ee.ServiceAccountCredentials(sa, key_file)
        ee.Initialize(credentials=creds, project=project)
        print(f"[oracle] GEE authenticated — {sa}")
    elif project:
        import ee
        ee.Initialize(project=project)
        print(f"[oracle] GEE authenticated — app default (project: {project})")
    else:
        import ee
        ee.Initialize()
        print("[oracle] GEE authenticated — app default credentials")


# ── Run model ─────────────────────────────────────────────────────────────────

def run_sar_plow(plot_id: str, claimed_date: str, job_id: str = "") -> dict:
    """Import and call the GEE SAR plow detection model."""
    sys.path.insert(0, str(Path(__file__).parent))
    from gee_sar_plow import predict_plowing
    result = predict_plowing(plot_id, claimed_date)
    if job_id:
        result["job_id"] = job_id
    return result


# ── Write result ──────────────────────────────────────────────────────────────

def write_result(result: dict, job_id: str) -> Path:
    """Save oracle result JSON to shared-memory/oracle-results/."""
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts       = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{job_id or result.get('plot_id', 'unknown')}_{ts}.json"
    out_path = RESULTS_DIR / filename
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    return out_path


# ── Pass/fail evaluation ──────────────────────────────────────────────────────

THRESHOLDS = {
    "SAR_PLOW_T1": {"confidence": 0.72},   # from 01-oracle-ai.md
}

def evaluate(result: dict, model: str) -> dict:
    """Append pass/fail verdict against tranche threshold."""
    threshold = THRESHOLDS.get(model, {}).get("confidence", 0.72)
    passed    = result.get("confidence", 0) >= threshold and result.get("status") == "CONFIRMED"
    result["tranche_model"]     = model
    result["threshold"]         = threshold
    result["tranche_pass"]      = passed
    result["tranche_verdict"]   = "PASS" if passed else "FAIL"
    return result


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="POD Oracle runner — SAR plow detection")
    group  = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--job",   help="Path to job JSON file from Orchestrator")
    group.add_argument("--plot",  help="Plot ID for manual run e.g. ETH-001")
    parser.add_argument("--date", help="Claimed date YYYY-MM-DD (required with --plot)")
    args = parser.parse_args()

    # ── Load job ──
    if args.job:
        with open(args.job) as f:
            job = json.load(f)
        plot_id      = job["plot_id"]
        claimed_date = job["claimed_date"]
        model        = job.get("model", "SAR_PLOW_T1")
        job_id       = job.get("job_id", "")
    else:
        if not args.date:
            parser.error("--date required with --plot")
        plot_id      = args.plot
        claimed_date = args.date
        model        = "SAR_PLOW_T1"
        job_id       = f"MANUAL-{plot_id}-{claimed_date}"

    print(f"\n[oracle] Job: {job_id or 'manual'} | {plot_id} | {claimed_date} | {model}")

    # ── Authenticate ──
    init_gee()

    # ── Run model ──
    print("[oracle] Running SAR plow detection...")
    try:
        result = run_sar_plow(plot_id, claimed_date, job_id)
    except Exception as e:
        error_result = {
            "job_id":        job_id,
            "plot_id":       plot_id,
            "claimed_date":  claimed_date,
            "status":        "ERROR",
            "error":         str(e),
            "timestamp":     datetime.utcnow().isoformat()
        }
        out = write_result(error_result, job_id)
        print(f"[oracle] ✗ Error: {e}")
        print(f"[oracle] Error result written → {out}")
        sys.exit(1)

    # ── Evaluate ──
    result = evaluate(result, model)

    # ── Output ──
    print("\n── Oracle Result ─────────────────────────────────")
    print(json.dumps(result, indent=2))

    out_path = write_result(result, job_id)
    print(f"\n[oracle] ✓ Result written → {out_path}")
    print(f"[oracle] Verdict: {result['tranche_verdict']} "
          f"(confidence {result['confidence']} vs threshold {result['threshold']})")


if __name__ == "__main__":
    main()
