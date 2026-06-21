# ApexPlanet — Deep-Dive Analysis & Interactive Dashboard

**Internship Task 3** · Deep-Dive Analysis & Interactive Dashboarding · Timeline: 12 Days

An end-to-end analysis of 1,000 ApexPlanet retail orders: core KPI definitions, an RFM-based
customer segmentation deep-dive, and a fully interactive dashboard.

**[Live Dashboard](dashboard/index.html)** — open directly, or via GitHub Pages once enabled (see below).

---

## What's in this repo

```
├── REPORT.md                       # Full deep-dive write-up: KPIs, methodology, findings, recommendations
├── data/
│   ├── ApexPlanet_Cleaned_Dataset.xlsx   # Source dataset (1,000 orders)
│   └── customer_segments.csv             # Output: 1 row per customer with RFM scores + segment
├── analysis/
│   └── segmentation_analysis.py    # Reproducible Python script that generates the segmentation + dashboard data
└── dashboard/
    ├── index.html                  # The interactive dashboard (open this file, or deploy via Pages)
    ├── data/data.js                # Pre-computed aggregates consumed by the dashboard
    └── assets/chart.umd.js         # Chart.js, bundled locally (no external dependencies / CDN)
```

## Quick start

**View the dashboard:** just open `dashboard/index.html` in any browser. No install, no server, no build step.

**Re-run the analysis:**
```bash
pip install pandas openpyxl
python analysis/segmentation_analysis.py
```
This regenerates both `data/customer_segments.csv` and `dashboard/data/data.js` from the source Excel file.

## Deploying the live link (GitHub Pages)

1. Push this repo to GitHub
2. Go to **Settings → Pages**
3. Set source to the `main` branch, root folder
4. Your dashboard will be live at:
   `https://<your-username>.github.io/<repo-name>/dashboard/index.html`

## Summary of findings

- **₹13.94 Cr** total revenue across 1,000 orders, 947 unique customers
- Only **5.5%** of customers have placed more than one order — this is a primarily acquisition-driven, not retention-driven, business today
- A focused **38% of customers (Champions / Loyal High-Value / At-Risk High-Value) generate 64% of revenue**
- The highest-leverage opportunity: **121 "At-Risk High-Value" customers** who spend like top customers but haven't ordered in ~9 months — a prime win-back target

Full methodology and recommendations in **[REPORT.md](REPORT.md)**.

## Dashboard features

- **Overview** — KPI cards, monthly revenue trend, category/city/age-group breakdowns, with live filters (City, Category, Year)
- **Core KPIs** — the 5 defined KPIs with formulas + rationale, day-of-week and product performance
- **Customer Segmentation** — the deep-dive: segment sizing, revenue concentration, recency-vs-spend bubble chart, top-10 customer leaderboard
- **Data Explorer** — filterable raw order table

Built with vanilla HTML/CSS/JS + Chart.js. No frameworks, no build tooling — easy to read, easy to extend.
