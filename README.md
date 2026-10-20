# gads-ai-bridge 🎯

> **Universal Google Ads CLI for AI Coding Assistants**  
> Enables Claude Code, Cursor, Cline, Roo Code, and PPC specialists to query Google Ads performance, mine wasteful search terms, audit keywords, and execute GAQL queries directly from any terminal.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Google Ads API: v18](https://img.shields.io/badge/Google%20Ads%20API-v18-orange.svg)](https://developers.google.com/google-ads/api)

---

## 💡 Why This Exists

Performance marketers and AI assistants in VS Code need immediate access to live ad metrics, search queries, and conversion figures without manually navigating the complex Google Ads web interface.

With `gads-ai-bridge`:
- 🤖 **Autonomous PPC Audits:** AI assistants can find search terms that wasted budget with zero conversions and suggest negative keywords in seconds.
- ⚡ **Lightweight & Fast:** Uses the Google Ads REST searchStream API without heavy C++ protobuf compile dependencies.
- 🔑 **Multi-Account Profiles:** Switch between accounts easily with `--profile work`, `--profile client1`.

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

### 2. Configure Developer Token & Customer ID

Google Ads requires a Developer Token (from your Google Ads Manager Account MCC $\rightarrow$ Tools & Settings $\rightarrow$ API Center):
```powershell
# Set your developer token
gads config --developer-token "YOUR_DEVELOPER_TOKEN"

# (Optional) Set your MCC manager ID and default customer account ID
gads config --mcc-id "123-456-7890" --customer-id "987-654-3210"
```

---

### 3. Authenticate

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
gads campaigns --customer-id <CID>
gads campaigns --customer-id <CID> --days 14
gads campaigns --customer-id <CID> --json
```

### 2. Search Terms Mining (Find Wasted Spend)
Audit search queries that triggered your ads. Filter by minimum spend and zero conversions:
```bash
# Find queries with cost > $25 and 0 conversions over the last 30 days:
gads search-terms --customer-id <CID> --min-spend 25 --zero-conversions --days 30
```

### 3. Keyword Performance
List active keywords with cost, clicks, match type, and conversions:
```bash
gads keywords --customer-id <CID> --days 30
```

### 4. Custom GAQL Queries
Execute any arbitrary Google Ads Query Language query:
```bash
gads query --customer-id <CID> \
  --query "SELECT campaign.name, metrics.cost_micros FROM campaign WHERE segments.date DURING LAST_7_DAYS" \
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

---

## 📄 License

MIT License. Free to use and distribute. See [LICENSE](LICENSE) for details.
