# Claude Code Guide for Google Ads (gads)

You have access to a global command-line utility `gads` to query Google Ads performance, campaigns, search queries, and keywords.

## Quick Reference
- **List campaigns with spend, clicks, conversions, ROAS:**
  ```bash
  gads campaigns --customer-id <CID> [--days 30] [--profile work]
  ```
- **Audit search terms (find wasteful queries for negative keywords):**
  ```bash
  # Find queries with spend > $20 and 0 conversions:
  gads search-terms --customer-id <CID> --min-spend 20 --zero-conversions --days 30
  ```
- **List keyword performance:**
  ```bash
  gads keywords --customer-id <CID> --days 30
  ```
- **Run arbitrary GAQL query:**
  ```bash
  gads query --customer-id <CID> --query "SELECT campaign.name, metrics.cost_micros FROM campaign WHERE segments.date DURING LAST_7_DAYS" --json
  ```
