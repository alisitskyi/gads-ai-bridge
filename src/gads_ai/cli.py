#!/usr/bin/env python3
"""
Global Google Ads CLI Tool (gads)
Enables any AI assistant or developer in VS Code across all projects to:
- Authenticate once globally with multiple account profiles (--profile)
- Query Google Ads using GAQL (Google Ads Query Language)
- Inspect campaigns, spend, CPC, CPA, ROAS
- Pull search terms report to find wasteful queries for negative keywords
- Output in formatted tables, CSV, or JSON for AI processing
"""

import os
import re
import sys
import csv
import json
import argparse
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    'https://www.googleapis.com/auth/adwords'
]

GADS_DIR = Path.home() / '.gads'
GADS_CREDS = GADS_DIR / 'credentials.json'
GADS_TOKEN = GADS_DIR / 'token.json'
GDOC_CREDS = Path.home() / '.gdoc' / 'credentials.json'
API_VERSION = "v24"


def find_credentials_file() -> Path:
    """Find credentials.json in ~/.gads or fallback to ~/.gdoc or local directory."""
    if GADS_CREDS.exists():
        return GADS_CREDS
    if GDOC_CREDS.exists():
        return GDOC_CREDS
    local_creds = Path.cwd() / '.secrets' / 'credentials.json'
    if local_creds.exists():
        return local_creds
    return GADS_CREDS


def find_token_file(profile: str = "default") -> Path:
    """Find token file for specific profile."""
    if profile and profile != "default":
        return GADS_DIR / f"token_{profile}.json"
    return GADS_TOKEN


def find_config_file(profile: str = "default") -> Path:
    """Find config file for specific profile."""
    if profile and profile != "default":
        return GADS_DIR / f"config_{profile}.json"
    return GADS_DIR / "config.json"


def load_config(profile: str = "default") -> Dict[str, Any]:
    """Load configuration (developer token, login customer id, etc.)."""
    cfg_file = find_config_file(profile)
    if cfg_file.exists():
        try:
            with open(cfg_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    # Fallback to default config
    def_cfg = GADS_DIR / "config.json"
    if def_cfg.exists():
        try:
            with open(def_cfg, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_config(data: Dict[str, Any], profile: str = "default"):
    """Save configuration."""
    GADS_DIR.mkdir(parents=True, exist_ok=True)
    cfg_file = find_config_file(profile)
    with open(cfg_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def clean_customer_id(cid: str) -> str:
    """Strip hyphens and spaces from customer ID."""
    if not cid:
        return ""
    return re.sub(r'[^0-9]', '', str(cid).strip())


def get_credentials(profile: str = "default") -> Credentials:
    """Authenticate via OAuth Desktop App."""
    GADS_DIR.mkdir(parents=True, exist_ok=True)
    creds_file = find_credentials_file()
    token_file = find_token_file(profile)

    if not creds_file.exists():
        print(f"\n[ERROR] Credentials file not found!", file=sys.stderr)
        print(f"Please save your downloaded Google Cloud OAuth JSON as:\n  {GADS_CREDS}", file=sys.stderr)
        sys.exit(1)

    creds = None
    if token_file.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print(f"[*] Refreshing expired token (profile: {profile})...", file=sys.stderr)
            try:
                creds.refresh(Request())
            except Exception:
                creds = None

        if not creds:
            print(f"[*] Launching browser for Google Ads OAuth login (profile: {profile})...", file=sys.stderr)
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_file, 'w', encoding='utf-8') as f:
            f.write(creds.to_json())
        print(f"[+] Google Ads token for profile '{profile}' saved to {token_file}", file=sys.stderr)

    return creds


def execute_gaql(customer_id: str, query: str, profile: str = "default", login_customer_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """Execute a GAQL query via Google Ads REST API searchStream."""
    creds = get_credentials(profile)
    if not creds.valid:
        creds.refresh(Request())

    config = load_config(profile)
    dev_token = config.get("developer_token") or os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN")
    if not dev_token:
        print("[ERROR] Developer Token is required for Google Ads API.", file=sys.stderr)
        print("Run 'gads config --developer-token <YOUR_TOKEN>' to save it.", file=sys.stderr)
        sys.exit(1)

    cid = clean_customer_id(customer_id)
    if not cid:
        cid = clean_customer_id(config.get("customer_id", ""))
    if not cid:
        print("[ERROR] Customer ID is required (--customer-id 123-456-7890).", file=sys.stderr)
        sys.exit(1)

    url = f"https://googleads.googleapis.com/{API_VERSION}/customers/{cid}/googleAds:searchStream"
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "developer-token": dev_token,
        "Content-Type": "application/json"
    }

    raw_login_cid = login_customer_id or config.get("login_customer_id", "")
    login_cid = clean_customer_id(raw_login_cid)
    if login_cid:
        headers["login-customer-id"] = login_cid

    resp = requests.post(url, headers=headers, json={"query": query})
    if resp.status_code != 200:
        print(f"[!] Google Ads API Error ({resp.status_code}):", file=sys.stderr)
        try:
            err_json = resp.json()
            print(json.dumps(err_json, indent=2, ensure_ascii=False), file=sys.stderr)
        except Exception:
            print(resp.text, file=sys.stderr)
        sys.exit(1)

    stream_batches = resp.json()
    all_rows = []
    for batch in stream_batches:
        results = batch.get("results", [])
        all_rows.extend(results)

    return all_rows


def print_table(headers: List[str], rows: List[List[str]], out_json: bool = False, out_csv: bool = False):
    """Format and print tabular data to stdout."""
    if out_json:
        result = [dict(zip(headers, row)) for row in rows]
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    if out_csv:
        writer = csv.writer(sys.stdout)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)
        return

    if not rows:
        print("[!] No data returned for this query.", file=sys.stderr)
        return

    widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            widths[idx] = max(widths[idx], len(str(val)))

    header_line = " | ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    separator = "-+-".join("-" * widths[i] for i in range(len(headers)))
    print(header_line)
    print(separator)
    for row in rows:
        print(" | ".join(str(val).ljust(widths[i]) for i, val in enumerate(row)))


# ==================== GADS COMMANDS ====================

def cmd_config(args):
    prof = getattr(args, 'profile', 'default')
    cfg = load_config(prof)
    updated = False

    if args.developer_token:
        cfg["developer_token"] = args.developer_token.strip()
        updated = True
    if args.mcc_id:
        cfg["login_customer_id"] = clean_customer_id(args.mcc_id)
        updated = True
    if args.customer_id:
        cfg["customer_id"] = clean_customer_id(args.customer_id)
        updated = True

    if updated:
        save_config(cfg, prof)
        print(f"[+] Configuration updated for profile '{prof}'!")

    print(f"=== Google Ads Config (Profile: '{prof}') ===")
    print(f"Developer Token:    {cfg.get('developer_token', '<NOT SET>')}")
    print(f"Login Customer ID:  {cfg.get('login_customer_id', '<NOT SET>')}")
    print(f"Default Customer ID:{cfg.get('customer_id', '<NOT SET>')}")


def cmd_status(args):
    prof = getattr(args, 'profile', 'default')
    creds_file = find_credentials_file()
    token_file = find_token_file(prof)
    cfg = load_config(prof)

    print(f"=== Google Ads Status (Profile: '{prof}') ===")
    print(f"Credentials location: {creds_file} (Exists: {creds_file.exists()})")
    print(f"Token location:       {token_file} (Exists: {token_file.exists()})")
    print(f"Developer Token:      {'CONFIGURED' if cfg.get('developer_token') else 'MISSING'}")

    if not creds_file.exists():
        print("[-] Status: Missing credentials.json. Please put it in ~/.gads/credentials.json")
    elif not token_file.exists():
        print(f"[!] Status: credentials.json present! Run 'gads auth --profile {prof}' to authorize.")
    elif not cfg.get('developer_token'):
        print("[!] Status: Authorized, but missing developer token. Run 'gads config --developer-token <TOKEN>'")
    else:
        print(f"[+] Status: Google Ads CLI is READY for profile '{prof}'!")


def cmd_campaigns(args):
    prof = getattr(args, 'profile', 'default')
    cid = clean_customer_id(args.customer_id)
    days = args.days or 30

    query = f"""
    SELECT
      campaign.id,
      campaign.name,
      campaign.status,
      campaign.advertising_channel_type,
      metrics.cost_micros,
      metrics.clicks,
      metrics.impressions,
      metrics.conversions,
      metrics.conversions_value
    FROM campaign
    WHERE segments.date DURING LAST_{days}_DAYS
      AND campaign.status != 'REMOVED'
    ORDER BY metrics.cost_micros DESC
    """

    results = execute_gaql(cid, query, prof, getattr(args, 'mcc_id', None))
    headers = ["Campaign", "Status", "Type", "Cost", "Clicks", "Impressions", "Conversions", "Conv. Value"]
    rows = []

    for r in results:
        c = r.get("campaign", {})
        m = r.get("metrics", {})
        cost = round(int(m.get("costMicros", 0)) / 1_000_000, 2)
        convs = round(float(m.get("conversions", 0)), 1)
        val = round(float(m.get("conversionsValue", 0)), 2)

        rows.append([
            c.get("name", "Unknown"),
            c.get("status", ""),
            c.get("advertisingChannelType", ""),
            f"${cost}",
            str(m.get("clicks", 0)),
            str(m.get("impressions", 0)),
            str(convs),
            f"${val}"
        ])

    print_table(headers, rows, args.json, args.csv)


def cmd_search_terms(args):
    prof = getattr(args, 'profile', 'default')
    cid = clean_customer_id(args.customer_id)
    days = args.days or 30
    min_spend = args.min_spend or 0.0

    query = f"""
    SELECT
      search_term_view.search_term,
      campaign.name,
      metrics.cost_micros,
      metrics.clicks,
      metrics.conversions
    FROM search_term_view
    WHERE segments.date DURING LAST_{days}_DAYS
    ORDER BY metrics.cost_micros DESC
    LIMIT {args.limit or 100}
    """

    results = execute_gaql(cid, query, prof, getattr(args, 'mcc_id', None))
    headers = ["Search Term", "Campaign", "Cost", "Clicks", "Conversions"]
    rows = []

    for r in results:
        term = r.get("searchTermView", {}).get("searchTerm", "")
        cname = r.get("campaign", {}).get("name", "")
        m = r.get("metrics", {})
        cost = round(int(m.get("costMicros", 0)) / 1_000_000, 2)
        convs = round(float(m.get("conversions", 0)), 1)

        if cost < min_spend:
            continue
        if args.zero_conversions and convs > 0:
            continue

        rows.append([
            term,
            cname,
            f"${cost}",
            str(m.get("clicks", 0)),
            str(convs)
        ])

    print_table(headers, rows, args.json, args.csv)


def cmd_keywords(args):
    prof = getattr(args, 'profile', 'default')
    cid = clean_customer_id(args.customer_id)
    days = args.days or 30

    query = f"""
    SELECT
      ad_group_criterion.keyword.text,
      ad_group_criterion.keyword.match_type,
      campaign.name,
      metrics.cost_micros,
      metrics.clicks,
      metrics.conversions
    FROM keyword_view
    WHERE segments.date DURING LAST_{days}_DAYS
      AND ad_group_criterion.status != 'REMOVED'
    ORDER BY metrics.cost_micros DESC
    LIMIT {args.limit or 100}
    """

    results = execute_gaql(cid, query, prof, getattr(args, 'mcc_id', None))
    headers = ["Keyword", "Match Type", "Campaign", "Cost", "Clicks", "Conversions"]
    rows = []

    for r in results:
        kw = r.get("adGroupCriterion", {}).get("keyword", {})
        cname = r.get("campaign", {}).get("name", "")
        m = r.get("metrics", {})
        cost = round(int(m.get("costMicros", 0)) / 1_000_000, 2)
        convs = round(float(m.get("conversions", 0)), 1)

        rows.append([
            kw.get("text", ""),
            kw.get("matchType", ""),
            cname,
            f"${cost}",
            str(m.get("clicks", 0)),
            str(convs)
        ])

    print_table(headers, rows, args.json, args.csv)


def cmd_query(args):
    prof = getattr(args, 'profile', 'default')
    cid = clean_customer_id(args.customer_id)
    results = execute_gaql(cid, args.query, prof, getattr(args, 'mcc_id', None))

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        # Flatten json and print
        print(f"Returned {len(results)} row(s):")
        for r in results:
            print(json.dumps(r, ensure_ascii=False))


def main():
    common_parser = argparse.ArgumentParser(add_help=False)
    common_parser.add_argument("--profile", default="default", help="Google Ads account profile name (e.g. 'work', 'client')")
    common_parser.add_argument("--login-customer-id", "--mcc-id", dest="mcc_id", help="Override Login MCC Customer ID")

    parser = argparse.ArgumentParser(
        prog="gads",
        description="Global Google Ads CLI for AI assistants and PPC specialists.",
        parents=[common_parser]
    )
    sub = parser.add_subparsers(dest="subcommand", help="Command to run")

    # Common
    sub.add_parser("auth", help="Authenticate with Google Ads OAuth", parents=[common_parser])
    sub.add_parser("status", help="Check Google Ads credentials & configuration status", parents=[common_parser])

    # Config
    p_cfg = sub.add_parser("config", help="Set or view Google Ads configuration", parents=[common_parser])
    p_cfg.add_argument("--developer-token", help="Set Developer Token")
    p_cfg.add_argument("--customer-id", help="Set default target Customer ID")

    # Campaigns
    p_camp = sub.add_parser("campaigns", help="List campaigns with spend, clicks, conversions", parents=[common_parser])
    p_camp.add_argument("--customer-id", help="Google Ads Customer ID (xxx-xxx-xxxx)")
    p_camp.add_argument("--days", type=int, default=30, help="Days back (default: 30)")
    p_camp.add_argument("--json", action="store_true", help="Output JSON")
    p_camp.add_argument("--csv", action="store_true", help="Output CSV")

    # Search Terms
    p_st = sub.add_parser("search-terms", help="Audit search terms report (find wasteful queries)", parents=[common_parser])
    p_st.add_argument("--customer-id", help="Google Ads Customer ID")
    p_st.add_argument("--days", type=int, default=30, help="Days back (default: 30)")
    p_st.add_argument("--min-spend", type=float, default=0.0, help="Filter minimum spend")
    p_st.add_argument("--zero-conversions", action="store_true", help="Only show queries with 0 conversions")
    p_st.add_argument("--limit", type=int, default=100, help="Max rows")
    p_st.add_argument("--json", action="store_true", help="Output JSON")
    p_st.add_argument("--csv", action="store_true", help="Output CSV")

    # Keywords
    p_kw = sub.add_parser("keywords", help="List keywords and performance", parents=[common_parser])
    p_kw.add_argument("--customer-id", help="Google Ads Customer ID")
    p_kw.add_argument("--days", type=int, default=30, help="Days back (default: 30)")
    p_kw.add_argument("--limit", type=int, default=100, help="Max rows")
    p_kw.add_argument("--json", action="store_true", help="Output JSON")
    p_kw.add_argument("--csv", action="store_true", help="Output CSV")

    # Query
    p_q = sub.add_parser("query", help="Execute arbitrary GAQL query", parents=[common_parser])
    p_q.add_argument("--customer-id", help="Google Ads Customer ID")
    p_q.add_argument("--query", required=True, help="GAQL query string")
    p_q.add_argument("--json", action="store_true", help="Output JSON")
    p_q.add_argument("--csv", action="store_true", help="Output CSV")

    args = parser.parse_args()

    if not args.subcommand:
        parser.print_help()
        sys.exit(0)

    try:
        prof = getattr(args, 'profile', 'default')
        if args.subcommand == "auth":
            get_credentials(prof)
            print(f"[+] Google Ads authentication successful for profile '{prof}'!")
        elif args.subcommand == "status":
            cmd_status(args)
        elif args.subcommand == "config":
            cmd_config(args)
        elif args.subcommand == "campaigns":
            cmd_campaigns(args)
        elif args.subcommand == "search-terms":
            cmd_search_terms(args)
        elif args.subcommand == "keywords":
            cmd_keywords(args)
        elif args.subcommand == "query":
            cmd_query(args)
    except Exception as e:
        print(f"[!] Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
