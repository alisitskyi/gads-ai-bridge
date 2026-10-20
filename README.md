# gads-ai-bridge 🎯

> **Universal Google Ads CLI for AI Coding Assistants**  
> Enables Claude Code, Cursor, Cline, Roo Code, and PPC specialists to query Google Ads performance, mine wasteful search terms, audit keywords, and execute GAQL queries directly from any terminal.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Google Ads API: v22](https://img.shields.io/badge/Google%20Ads%20API-v22-orange.svg)](https://developers.google.com/google-ads/api)

---

## 💡 Why This Exists

Performance marketers and AI assistants in VS Code need immediate access to live ad metrics, search queries, and conversion figures without manually navigating the complex Google Ads web interface.

With `gads-ai-bridge`:
- 🤖 **Autonomous PPC Audits:** AI assistants can find search terms that wasted budget with zero conversions and suggest negative keywords in seconds.
- ⚡ **Lightweight & Fast:** Uses the Google Ads REST searchStream API without heavy C++ protobuf compile dependencies.
- 🔑 **Multi-Account Profiles:** Switch between accounts easily with `--profile work`, `--profile client1`.
- 🛠️ **MCC Manager Support:** Manage child accounts seamlessly with `--login-customer-id`.

---

## 🚀 Quickstart

### 1. Installation

**Windows (PowerShell):**
```powershell
git clone https://github.com/alisitskyi/gads-ai-bridge.git
cd gads-ai-bridge
.\install.ps1
```

**macOS / Linux:**
```bash
git clone https://github.com/alisitskyi/gads-ai-bridge.git
cd gads-ai-bridge
chmod +x install.sh
./install.sh
```

---

### 2. Prerequisites & Credentials

1. **Google Cloud Project:**  
   Ensure **Google Ads API** is enabled in your Google Cloud Project:  
   👉 [Enable Google Ads API](https://console.developers.google.com/apis/api/googleads.googleapis.com/overview)
2. **Developer Token:**  
   Obtain your Developer Token from your Google Ads Manager Account (MCC) $\rightarrow$ **Tools & Settings** $\rightarrow$ **API Center**.
3. **Configure Settings:**
   ```powershell
   # Set Developer Token:
   gads config --developer-token "YOUR_DEVELOPER_TOKEN"

   # (Optional) Set your MCC manager ID and default customer account ID:
   gads config --login-customer-id "123-456-7890" --customer-id "987-654-3210"

   # For a separate client profile:
   gads config --profile sellerlogic --customer-id "168-927-0028"
   ```

---

### 3. Authenticate

Authenticate once via standard Google OAuth:
```powershell
gads auth

# Or for a separate account profile:
gads auth --profile work
```

---

## 📖 CLI Usage Reference

### 1. Campaign Overview
List campaigns with spend, clicks, impressions, and conversions:
```bash
# Uses default configured customer-id
gads campaigns

# Specify customer ID explicitly:
gads campaigns --customer-id 168-927-0028
gads campaigns --customer-id 168-927-0028 --days 14
gads campaigns --customer-id 168-927-0028 --days 90 --json
```

### 2. Search Terms Mining (Find Wasted Spend)
Audit search queries that triggered your ads. Filter by minimum spend and zero conversions to rapidly identify negative keyword candidates:
```bash
# Find queries with cost > $25 and 0 conversions over the last 30 days:
gads search-terms --customer-id 168-927-0028 --min-spend 25 --zero-conversions --days 30
```

### 3. Keyword Performance
List active keywords with cost, clicks, match type, and conversions:
```bash
gads keywords --customer-id 168-927-0028 --days 30
```

### 4. Custom GAQL Queries
Execute any arbitrary Google Ads Query Language query:
```bash
gads query --customer-id 168-927-0028 \
  --query "SELECT campaign.name, metrics.cost_micros, metrics.conversions FROM campaign WHERE segments.date DURING LAST_7_DAYS" \
  --json
```

---

## 🤖 Connecting to AI Assistants

Add to `.claude/settings.json` or `.cursorrules`:
```json
{
  "allowedTools": [
    "Bash(gads *)",
    "PowerShell(gads *)"
  ]
}
```

Prompt examples for AI assistants:
- *"Audit search terms for account 168-927-0028 that spent over $20 with zero conversions using `gads search-terms` and propose a negative keyword list."*
- *"Show active Google Ads campaigns and performance for the last 30 days using `gads campaigns`."*
- *"Compare keyword CPCs and conversions with `gads keywords`."*

---

## 📄 License

MIT License. Free to use and distribute. See [LICENSE](LICENSE) for details.
