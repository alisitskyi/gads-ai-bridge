# gads-ai-bridge 🎯

> **Universal Google Ads CLI for AI Coding Assistants**  
> Enables Claude Code, Cursor, Cline, Roo Code, and PPC specialists to query Google Ads performance, mine wasteful search terms, audit keywords, and execute GAQL queries directly from any terminal.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Google Ads API: v24](https://img.shields.io/badge/Google%20Ads%20API-v24-orange.svg)](https://developers.google.com/google-ads/api)

---

## 💡 Why This Exists

Performance marketers and AI assistants in VS Code need immediate access to live ad metrics, search queries, and conversion figures without manually navigating the complex Google Ads web interface.

With `gads-ai-bridge`:
- 🤖 **Autonomous PPC Audits:** AI assistants can find search terms that wasted budget with zero conversions and suggest negative keywords in seconds.
- ⚡ **Lightweight & Fast:** Uses the Google Ads REST searchStream API without heavy C++ protobuf compile dependencies.
- 🔑 **Multi-Account Profiles:** Switch between accounts easily with `--profile work`, `--profile helpcrunch`.
- 🛠️ **MCC Manager Support:** Manage child accounts seamlessly with `--login-customer-id` (MCC ID).
- 🚀 **Zero-Delay Setup:** Uses Google Cloud **Explorer Access** to query live production accounts with automated instant approval.

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

1. **Google Cloud Project & Explorer Access:**  
   - Enable **Google Ads API** in your Google Cloud Project: [Enable Google Ads API](https://console.developers.google.com/apis/api/googleads.googleapis.com/overview)
   - On the Google Ads API Overview page, upgrade your access level from **Test** to **Explorer Access**. Explorer Access grants automated, instant approval to query live production accounts (up to 2,880 operations/day).
2. **Developer Token:**  
   Obtain your Developer Token from your Google Ads Manager Account (MCC) $\rightarrow$ **Tools & Settings** $\rightarrow$ **API Center**.
3. **Configure Settings:**
   ```powershell
   # Set Developer Token:
   gads config --developer-token "YOUR_DEVELOPER_TOKEN"

   # (Optional) Set your MCC manager ID and default customer account ID:
   gads config --login-customer-id "123-456-7890" --customer-id "987-654-3210"
   ```

---

### 3. Multi-Account Authentication

You can authenticate multiple Google accounts in parallel. Each profile maintains isolated OAuth tokens and settings in `~/.gads/`:

```powershell
# Account 1 (Default / SellerLogic):
gads auth
gads config --customer-id "168-927-0028" --login-customer-id "324-029-4849"

# Account 2 (HelpCrunch Profile):
gads auth --profile helpcrunch
gads config --profile helpcrunch --customer-id "994-801-3362" --login-customer-id "756-356-5497"
```

---

## 📖 CLI Usage Reference

### 1. Campaign Overview
List campaigns with spend, clicks, impressions, and conversions:
```bash
# Uses default profile (SellerLogic):
gads campaigns

# Query another profile (HelpCrunch):
gads campaigns --profile helpcrunch
gads campaigns --profile helpcrunch --days 14
gads campaigns --profile helpcrunch --days 90 --json

# Target any customer account and MCC on the fly:
gads campaigns --customer-id 168-927-0028 --login-customer-id 324-029-4849
```

### 2. Search Terms Mining (Find Wasted Spend)
Audit search queries that triggered your ads. Filter by minimum spend and zero conversions to rapidly identify negative keyword candidates:
```bash
# Find queries with cost > $20 and 0 conversions over the last 30 days:
gads search-terms --profile helpcrunch --min-spend 20 --zero-conversions --days 30
```

### 3. Keyword Performance
List active keywords with cost, clicks, match type, and conversions:
```bash
gads keywords --profile helpcrunch --days 30
```

### 4. Custom GAQL Queries
Execute any arbitrary Google Ads Query Language query:
```bash
gads query --profile helpcrunch \
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
- *"Audit search terms for HelpCrunch that spent over $20 with zero conversions using `gads search-terms --profile helpcrunch` and propose a negative keyword list."*
- *"Show active Google Ads campaigns and performance for SellerLogic using `gads campaigns`."*
- *"Compare keyword CPCs and conversions for HelpCrunch with `gads keywords --profile helpcrunch`."*

---

## 📄 License

MIT License. Free to use and distribute. See [LICENSE](LICENSE) for details.
