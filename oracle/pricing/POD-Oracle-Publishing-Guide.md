# POD Open Oracle — Commodity Price Publishing Guide
## Instructions for Junior Developer: Data Pull → On-Chain Publication (Solana / Switchboard)

**Audience:** Junior developer with basic Python and command-line skills  
**Goal:** Pull monthly MENA commodity prices and publish them as a decentralized oracle feed on Solana using Switchboard v2  
**Platform:** Switchboard v2 (Solana-native, Chainlink alternative)  
**Network:** Solana Devnet (testing) → Solana Mainnet (production)

---

## Overview

This guide covers three stages:

1. **Pull** — collect commodity price data from public sources
2. **Package** — format the data into the POD JSON schema
3. **Publish** — push prices on-chain via Switchboard v2 on Solana

The output is a set of on-chain oracle feeds that anyone can read permissionlessly. These feeds are used by the POD protocol to validate commodity valuations and release tranche financing.

---

## Part 1 — Environment Setup

### 1.1 Prerequisites

Install the following before starting:

```bash
# Python 3.11+
python --version   # must be 3.11 or higher

# Node.js 18+ (for Switchboard CLI)
node --version     # must be 18 or higher

# Solana CLI
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
solana --version

# Switchboard CLI
npm install -g @switchboard-xyz/cli
sb --version

# Python packages
pip install requests pandas python-dotenv anchorpy solders solana
```

### 1.2 Wallet Setup

You need a Solana keypair to sign oracle transactions. Use the devnet oracle keypair from the project:

```bash
# Check if oracle keypair already exists
ls ~/.config/solana/oracle-keypair.json

# If not, generate one (devnet only)
solana-keygen new --outfile ~/.config/solana/oracle-keypair.json

# Set CLI to use devnet
solana config set --url https://api.devnet.solana.com
solana config set --keypair ~/.config/solana/oracle-keypair.json

# Airdrop SOL for transaction fees (devnet only)
solana airdrop 2
solana balance   # confirm you have SOL
```

**Important:** Never use the devnet keypair on mainnet. Ask ops@ for the mainnet oracle keypair when ready for production.

### 1.3 Environment File

Copy `.env.template` from `pod-agents/` and fill in the following keys for oracle publishing work:

```
SOLANA_DEVNET_RPC_URL=https://api.devnet.solana.com
ORACLE_KEYPAIR_PATH=~/.config/solana/oracle-keypair.json
SWITCHBOARD_FEED_PUBKEY=     # fill in after creating the feed (Step 3.2)
SWITCHBOARD_QUEUE_PUBKEY=    # fill in after creating the feed (Step 3.2)
```

Leave all other keys blank unless you are also working on satellite oracle or social media tasks.

---

## Part 2 — Pulling Commodity Price Data

### 2.1 Data Sources by Commodity

Use this table to know where to pull each commodity's price:

| Commodity | Source | URL | Cadence |
|---|---|---|---|
| Live sheep / goat (KSA, UAE) | selinawamucii.com | See §2.2 | Weekly |
| Alfalfa hay (KSA CIF) | USDA FAS GAIN | apps.fas.usda.gov | Monthly |
| Alfalfa hay (CEIC series) | CEIC | ceicdata.com | Monthly |
| Corn silage (estimate) | USDA FAS + CME futures | fas.usda.gov | Monthly |
| Sorghum (CIF Jeddah) | USDA FAS | fas.fas.usda.gov | Monthly |
| Live cattle | FAO GIEWS / selinawamucii | fao.org/giews | Monthly |
| Carcass small ruminants | IndexBox (paid) / FAO | indexbox.io | Monthly |

### 2.2 Pulling Live Ruminant Prices from selinawamucii.com

This is the primary confirmed data source for live sheep and goat pricing.

```python
# scripts/pull_selinawamucii.py
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def fetch_sheep_price_ksa():
    """
    Scrape live sheep wholesale price for Saudi Arabia from selinawamucii.com.
    Returns dict with low/high/midpoint in USD/kg live weight.
    """
    url = "https://www.selinawamucii.com/insights/prices/saudi-arabia/sheep/"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    resp = requests.get(url, headers=headers, timeout=15)
    resp.raise_for_status()
    
    soup = BeautifulSoup(resp.text, "html.parser")
    
    # The page displays price ranges in a summary table.
    # Find the element containing "USD" and parse the range.
    # NOTE: If the site structure changes, update the selector below.
    price_text = soup.find("span", class_="price-value")
    
    # Parse "$3.67 - $4.20 per kg"
    # Adapt this parsing if the format changes
    if price_text:
        raw = price_text.get_text(strip=True)
        # Basic parse: extract first and last dollar amounts
        import re
        amounts = re.findall(r"\$?([\d.]+)", raw)
        if len(amounts) >= 2:
            low = float(amounts[0])
            high = float(amounts[-1])
            return {
                "animal": "sheep",
                "market": "Saudi Arabia",
                "port": "Jeddah",
                "unit": "USD/kg live weight",
                "price_low": low,
                "price_high": high,
                "price_midpoint": round((low + high) / 2, 4),
                "source": "selinawamucii.com",
                "date": datetime.now().strftime("%Y-%m"),
                "raw": raw
            }
    
    raise ValueError("Could not parse price from selinawamucii.com — check page structure")


if __name__ == "__main__":
    result = fetch_sheep_price_ksa()
    print(json.dumps(result, indent=2))
```

**If selinawamucii.com blocks automated requests:** Visit the page manually in your browser, read the current price, and enter it directly into the JSON schema. The priority is accuracy, not automation at this stage.

### 2.3 Pulling Alfalfa Hay Prices from USDA FAS

USDA FAS publishes GAIN (Global Agricultural Information Network) reports for Saudi Arabia that include alfalfa import prices.

```python
# scripts/pull_usda_fas.py
import requests
import json

def search_fas_gain_reports(commodity="alfalfa", country="Saudi Arabia"):
    """
    Search USDA FAS GAIN reports for the given commodity and country.
    Returns a list of recent report URLs.
    
    Manual fallback: visit https://apps.fas.usda.gov/psdonline/app/index.html#/app/gainerReports
    Filter by: Country = Saudi Arabia, Commodity = Hay/Alfalfa
    """
    base_url = "https://apps.fas.usda.gov/gainerapi/api/Report/country"
    params = {
        "countryCode": "SA",
        "commodityCode": "1214100000",  # HS code for alfalfa hay
        "pageSize": 5
    }
    
    try:
        resp = requests.get(base_url, params=params, timeout=15)
        resp.raise_for_status()
        reports = resp.json()
        return reports
    except Exception as e:
        print(f"API call failed: {e}")
        print("Use manual fallback: https://apps.fas.usda.gov/psdonline/app/index.html#/app/gainerReports")
        return []


# Manual entry fallback (use when API unavailable)
ALFALFA_MANUAL_ENTRY = {
    "commodity": "Alfalfa Hay",
    "market": "Saudi Arabia",
    "port": "Jeddah",
    "unit": "USD/ton CIF",
    "grade": "Premium",
    "origin": "Australia",
    "price_usd_per_ton": 430,
    "price_range_low": 420,
    "price_range_high": 440,
    "source": "USDA FAS GAIN / CEIC",
    "date": "2026-05",
    "notes": "Enter manually from USDA FAS GAIN Saudi Arabia report"
}
```

**Manual pull steps (recommended for monthly updates):**
1. Go to `apps.fas.usda.gov/psdonline/app/index.html#/app/gainerReports`
2. Filter: Country = Saudi Arabia, Commodity type = Hay
3. Download the most recent report PDF
4. Read the CIF Jeddah price for alfalfa (premium and standard grades)
5. Enter values into `may-2026-commodity-prices.json`

### 2.4 Output Schema

All pulled data must be formatted to match `may-2026-commodity-prices.json` in `pod-analytics/market-intel/commodity-prices/`. The key fields for each oracle feed entry are:

```json
{
  "feed_id": "POD_COMMODITY_SHEEP_KSA_LW",
  "commodity": "Live Sheep",
  "market": "Saudi Arabia",
  "port": "Jeddah",
  "unit": "USD/kg live weight",
  "date": "2026-05",
  "price_midpoint": 3.94,
  "price_low": 3.67,
  "price_high": 4.20,
  "source": "selinawamucii.com",
  "data_quality": "confirmed"
}
```

The `price_midpoint` is what gets published on-chain. Use `(low + high) / 2` rounded to 4 decimal places.

---

## Part 3 — Publishing On-Chain via Switchboard v2 (Solana)

### What is Switchboard?

Switchboard v2 is a decentralized oracle network on Solana. It is the Solana-native equivalent of Chainlink. Unlike Chainlink, Switchboard allows you to create **custom oracle feeds** that pull from any public data source — including commodity price scrapers like the ones above.

Key concepts:
- **Queue**: A set of trusted oracle nodes that validate and publish data
- **Aggregator (Feed)**: An on-chain account that holds the published price value
- **Job**: The data fetch task (URL + parse instructions) that oracle nodes execute

For POD's initial open oracle, we will use a **simpler approach**: a single authorized publisher (the oracle keypair) pushes prices directly to a Switchboard aggregator feed. This is appropriate for Phase 0 before a full decentralized oracle node network is set up.

### 3.1 Install and Configure Switchboard CLI

```bash
# Install
npm install -g @switchboard-xyz/cli

# Confirm installation
sb --version

# Set Switchboard to devnet
sb config set --mainnetBeta false
```

### 3.2 Create an Oracle Queue (one-time setup)

A queue defines which oracle nodes are authorized to publish. For Phase 0, create a **permissioned queue** where your oracle keypair is the only authorized publisher.

```bash
# Create a new oracle queue on devnet
sb queue create \
  --name "POD Commodity Oracle Queue" \
  --keypair ~/.config/solana/oracle-keypair.json \
  --cluster devnet \
  --reward 0 \
  --minStake 0

# SAVE the output. It will print:
#   Queue Pubkey: <QUEUE_PUBKEY>
# Add this to your .env as SWITCHBOARD_QUEUE_PUBKEY
```

### 3.3 Create an Oracle Feed (Aggregator) Per Commodity

Create one feed per commodity price. Run this command once per feed:

```bash
# Example: Live Sheep KSA price feed
sb aggregator create \
  --name "POD Live Sheep KSA USD/kg LW" \
  --keypair ~/.config/solana/oracle-keypair.json \
  --cluster devnet \
  --queueKey $SWITCHBOARD_QUEUE_PUBKEY \
  --batchSize 1 \
  --minRequiredOracleResults 1 \
  --minUpdateDelaySeconds 3600 \
  --varianceThreshold 0.5

# SAVE the output:
#   Aggregator Pubkey: <FEED_PUBKEY>
# Add to .env as SWITCHBOARD_FEED_PUBKEY (use a separate var per feed)
```

Repeat for each feed defined in `oracle_feed_schema` in the JSON data file:
- `POD_COMMODITY_SHEEP_KSA_LW`
- `POD_COMMODITY_GOAT_KSA_LW`
- `POD_COMMODITY_ALFALFA_KSA_PREMIUM`
- `POD_COMMODITY_ALFALFA_KSA_STANDARD`
- `POD_COMMODITY_SORGHUM_KSA`

### 3.4 Add a Job to Each Feed

A Job tells the Switchboard oracle what URL to fetch and how to parse the result. For POD Phase 0, point the job to a hosted JSON endpoint (e.g., a public Arweave or IPFS URL of the monthly data file), or use a static value job to manually push prices.

**Option A — Static value push (simplest for Phase 0):**

```bash
# Push a price directly to the feed without a scraper job
# Useful for monthly manual updates
sb aggregator update $FEED_PUBKEY \
  --keypair ~/.config/solana/oracle-keypair.json \
  --cluster devnet
```

**Option B — JSON endpoint job (recommended for automation):**

```bash
# First, upload your JSON data file to IPFS or Arweave
# Then create a job that fetches the price field from the URL

sb job create \
  --cluster devnet \
  --keypair ~/.config/solana/oracle-keypair.json \
  --name "POD Sheep KSA Price Fetch" \
  --json '{
    "tasks": [
      {
        "httpTask": {
          "url": "https://YOUR_IPFS_OR_ARWEAVE_URL/may-2026-commodity-prices.json"
        }
      },
      {
        "jsonParseTask": {
          "path": "$.live_small_ruminants.markets[0].price_midpoint"
        }
      }
    ]
  }'
```

Then attach the job to the feed:

```bash
sb aggregator add job $FEED_PUBKEY \
  --keypair ~/.config/solana/oracle-keypair.json \
  --cluster devnet \
  --jobKey $JOB_PUBKEY
```

### 3.5 Publish Price Updates (Python Script)

Use the following script to push updated prices on-chain after each monthly data pull:

```python
# scripts/publish_oracle_prices.py
"""
Reads the monthly commodity price JSON and pushes midpoint prices
to Switchboard v2 aggregator feeds on Solana devnet.

Usage:
  python scripts/publish_oracle_prices.py \
    --data pod-analytics/market-intel/commodity-prices/may-2026-commodity-prices.json \
    --network devnet
"""

import argparse
import json
import os
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

FEED_PUBKEYS = {
    "POD_COMMODITY_SHEEP_KSA_LW":        os.getenv("SWITCHBOARD_FEED_SHEEP_KSA"),
    "POD_COMMODITY_GOAT_KSA_LW":         os.getenv("SWITCHBOARD_FEED_GOAT_KSA"),
    "POD_COMMODITY_ALFALFA_KSA_PREMIUM": os.getenv("SWITCHBOARD_FEED_ALFALFA_PREMIUM"),
    "POD_COMMODITY_ALFALFA_KSA_STANDARD":os.getenv("SWITCHBOARD_FEED_ALFALFA_STANDARD"),
    "POD_COMMODITY_SORGHUM_KSA":         os.getenv("SWITCHBOARD_FEED_SORGHUM"),
}

def load_price_data(filepath: str) -> dict:
    with open(filepath) as f:
        return json.load(f)

def get_feed_values(data: dict) -> dict:
    """Extract the on-chain publishable midpoint for each feed."""
    schema = data.get("oracle_feed_schema", {}).get("feeds", [])
    return {
        feed["feed_id"]: feed["value_may_2026"]
        for feed in schema
    }

def push_to_switchboard(feed_pubkey: str, value: float, keypair_path: str, network: str):
    """
    Call the Switchboard CLI to push a value to an aggregator feed.
    Switchboard v2 encodes prices as i128 scaled by 10^precision (default 9).
    """
    cmd = [
        "sb", "aggregator", "update", feed_pubkey,
        "--keypair", keypair_path,
        "--cluster", network
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr.strip()}")
    else:
        print(f"  OK: tx = {result.stdout.strip()}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", required=True, help="Path to monthly price JSON")
    parser.add_argument("--network", default="devnet", choices=["devnet", "mainnet-beta"])
    args = parser.parse_args()

    keypair = os.getenv("ORACLE_KEYPAIR_PATH", "~/.config/solana/oracle-keypair.json")
    
    data = load_price_data(args.data)
    feed_values = get_feed_values(data)

    print(f"\nPublishing {len(feed_values)} feeds to Solana {args.network}...\n")

    for feed_id, value in feed_values.items():
        pubkey = FEED_PUBKEYS.get(feed_id)
        if not pubkey:
            print(f"  SKIP {feed_id}: no pubkey configured in .env")
            continue
        print(f"  {feed_id}: {value} → feed {pubkey[:8]}...")
        push_to_switchboard(pubkey, value, keypair, args.network)

    print("\nDone. Verify on Switchboard Explorer:")
    print("  https://app.switchboard.xyz/solana/devnet")

if __name__ == "__main__":
    main()
```

Run it:

```bash
python scripts/publish_oracle_prices.py \
  --data pod-analytics/market-intel/commodity-prices/may-2026-commodity-prices.json \
  --network devnet
```

### 3.6 Verify On-Chain

After publishing, verify the prices are live:

```bash
# Read a specific feed's current value via CLI
sb aggregator print $SWITCHBOARD_FEED_SHEEP_KSA --cluster devnet

# Or use the Switchboard web explorer
# https://app.switchboard.xyz/solana/devnet
# Paste the feed pubkey to see the latest round result
```

You should see the `latestConfirmedRound.result` matching the midpoint value you published.

---

## Part 4 — Monthly Update Workflow

Run this checklist every month (target: first week of the month, covering the prior month's data):

**Step 1 — Pull prices**
- [ ] Check selinawamucii.com for live sheep/goat prices (KSA and UAE)
- [ ] Check USDA FAS GAIN for latest Saudi Arabia alfalfa report
- [ ] Check FAO GIEWS for any livestock price updates
- [ ] Note any active export bans or disease alerts (RVF, FMD) from OIE

**Step 2 — Update the data file**
- [ ] Open `commodity-prices/may-2026-commodity-prices.json` (or create next month's file with the same schema)
- [ ] Update all `price_midpoint`, `price_low`, `price_high` values
- [ ] Update `data_quality` field: `confirmed` if from primary source, `estimated` if derived
- [ ] Update `period` and `generated` fields in `metadata`
- [ ] Update `oracle_feed_schema.feeds[].value_YYYY_MM` for each feed

**Step 3 — Upload data file to IPFS** (if using Option B jobs)
- [ ] Upload updated JSON to IPFS via web3.storage or Arweave
- [ ] Note the new CID/URL

**Step 4 — Publish on-chain**
- [ ] Run `publish_oracle_prices.py` against devnet first
- [ ] Verify values on Switchboard Explorer (devnet)
- [ ] If values look correct, re-run with `--network mainnet-beta`
- [ ] Verify on Switchboard Explorer (mainnet)

**Step 5 — Record**
- [ ] Save the transaction signatures in a log file under `shared-memory/oracle-results/`
- [ ] Notify ops@proofofdirt.com with a brief summary: which feeds updated, new values, any stubs not updated

---

## Part 5 — Going to Mainnet

Before switching from devnet to mainnet:

1. Confirm with ops@ that the mainnet oracle keypair is ready and funded (needs ~0.1 SOL for fees)
2. Re-create the queue and all feeds on mainnet (`--cluster mainnet-beta`)
3. Save all mainnet feed pubkeys to the production `.env` (never commit this file)
4. Run one dry-run on devnet with the same data, then publish to mainnet
5. Register the feed pubkeys in the POD protocol's Anchor program (ask the Solana dev — Agent 02) so smart contracts can read them

---

## Reference: Key Links

| Resource | URL |
|---|---|
| Switchboard v2 docs | docs.switchboard.xyz |
| Switchboard Explorer (devnet) | app.switchboard.xyz/solana/devnet |
| Switchboard Explorer (mainnet) | app.switchboard.xyz/solana/mainnet |
| Solana Explorer (devnet) | explorer.solana.com?cluster=devnet |
| USDA FAS GAIN Reports | apps.fas.usda.gov/psdonline/app/index.html#/app/gainerReports |
| FAO GIEWS | fao.org/giews/en/ |
| selinawamucii.com | selinawamucii.com/insights/prices/ |
| OIE disease alerts | woah.org/en/disease/rift-valley-fever/ |
| IPFS upload (web3.storage) | web3.storage |

---

## Who to Ask

| Question | Contact |
|---|---|
| Oracle keypair / wallet access | ops@proofofdirt.com |
| Switchboard program integration (Anchor) | dev@proofofdirt.com (Agent 02 — Solana Dev) |
| Price data questions / source validation | analytics@proofofdirt.com |
| On-chain architecture decisions | dev@proofofdirt.com |

---

*POD Open Oracle — Commodity Price Publishing Guide*  
*Last updated: June 2026 | Owner: dev@proofofdirt.com*
