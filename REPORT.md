# Deep-Dive Analysis Report — ApexPlanet Retail

**Task 3: Deep-Dive Analysis & Interactive Dashboarding**
Dataset: `ApexPlanet_Cleaned_Dataset.xlsx` · 1,000 orders · 947 customers · Jan 2025 – Jan 2026 · 8 cities · 5 categories

**Live dashboard:** see [`dashboard/index.html`](dashboard/index.html) (or the GitHub Pages link in the main README)

---

## 1. Objective

To move beyond surface-level reporting and answer a harder business question: **which customers should ApexPlanet spend its retention budget on, and why?** This requires defining core KPIs, picking one business area for a real deep-dive, and surfacing both in a dashboard a non-technical stakeholder can explore.

---

## 2. Core KPIs

| KPI | Formula | Business Rationale |
|---|---|---|
| **Total Revenue** | `SUM(Total_Sales)` | Top-line scale of the business; every other KPI explains movement in this number. |
| **Average Order Value (AOV)** | `SUM(Total_Sales) / COUNT(Order_ID)` | Distinguishes "more orders" growth from "bigger basket" growth — different levers, different costs. |
| **Repeat Customer Rate** | `Customers with 2+ orders / Total customers` | Measures retention health independent of revenue size. |
| **Customer Recency (Days)** | `Snapshot Date − Last Order Date` | Early-warning signal for churn risk, computed per customer. |
| **Customer Lifetime Value (Monetary)** | `SUM(Total_Sales)` per `Customer_ID` | Identifies which customers are actually worth retaining. |

**Headline numbers from this dataset:**
- Total Revenue: **₹13.94 Cr** across 1,000 orders
- AOV: **₹1,39,399**
- Repeat Customer Rate: **5.5%** (52 of 947 customers ordered more than once)

---

## 3. Why Customer Segmentation Was Chosen as the Deep-Dive

The task brief offered three deep-dive options: cohort/retention analysis, funnel analysis, or segmentation analysis. **Cohort analysis was checked first and ruled out**: with only 52 of 947 customers (5.5%) placing a second order within the 12-month window, monthly cohort retention curves would be built on too few repeat events per cohort to be statistically meaningful or actionable.

**Customer Segmentation (RFM)** was selected instead, because it works well precisely in a business that is acquisition-heavy and retention-light — it answers "who are our best customers, and who is slipping away?" using the data that *is* dense (every customer has a recency, frequency, and monetary value, even with just one order).

---

## 4. Methodology — RFM Segmentation

Each customer was scored on three dimensions, independently bucketed into quartiles (1 = worst, 4 = best):

- **Recency (R):** Days since last order (inverted — fewer days = higher score)
- **Frequency (F):** Number of orders placed
- **Monetary (M):** Total historical spend

Customers were then assigned to one of six business-rule segments based on their R/F/M scores:

| Segment | Rule | Count | % of Base | Total Revenue | Avg. Spend/Customer |
|---|---|---:|---:|---:|---:|
| **Champions** | High R, F, and M | 129 | 13.6% | ₹3.34 Cr | ₹2,59,216 |
| **Needs Attention** | Mixed scores | 224 | 23.7% | ₹3.10 Cr | ₹1,38,530 |
| **At-Risk High-Value** | Low R, but high F & M | 121 | 12.8% | ₹3.01 Cr | ₹2,48,635 |
| **Loyal High-Value** | High R & M | 113 | 11.9% | ₹2.57 Cr | ₹2,27,791 |
| **Lost / Churned** | Low R and low M | 239 | 25.2% | ₹1.23 Cr | ₹51,543 |
| **Recent Low-Engagement** | High R, but low F | 121 | 12.8% | ₹0.68 Cr | ₹56,081 |

*(Full per-customer output: [`data/customer_segments.csv`](data/customer_segments.csv); reproducible via [`analysis/segmentation_analysis.py`](analysis/segmentation_analysis.py))*

---

## 5. Key Findings

1. **A small high-value core carries the business.** Champions + Loyal High-Value + At-Risk High-Value together are only 38.3% of customers but generate **₹8.92 Cr — 64% of total revenue.** Retention strategy should concentrate here first.

2. **"At-Risk High-Value" is the single highest-priority segment to act on.** These 121 customers have historically spent as much as Champions (₹2,48,635 avg.) but haven't ordered in ~275 days on average. They are not yet lost, but trending that way — a targeted win-back campaign (personalized offer, reorder reminder) has the highest expected ROI of any action available in this dataset.

3. **"Lost / Churned" is the largest segment by count (25.2%) but the smallest by revenue contribution (8.8%).** This validates that broad-based reactivation campaigns aimed at this group will have a low ceiling — better to qualify which of them resemble past Champions before spending budget here.

4. **Repeat purchase is rare overall (5.5%).** This is the most important structural finding: ApexPlanet currently behaves like a single-purchase / transactional retailer rather than a habitual one. Any roadmap aimed at improving LTV should treat "convert a first-time buyer into a second-time buyer" as its own funnel to instrument and optimize, separate from acquisition.

5. **Electronics is the largest category by revenue (₹5.08 Cr, 36.4% of total),** followed by Education (₹2.50 Cr). Mobile and Laptop alone account for the bulk of Electronics revenue — useful context when deciding which category to bundle into win-back offers for At-Risk High-Value customers.

---

## 6. Recommendations

| Priority | Action | Target Segment |
|---|---|---|
| 1 | Win-back campaign with personalized discount on previously purchased category | At-Risk High-Value (121 customers, ₹3.0 Cr at stake) |
| 2 | Loyalty/early-access program to convert single-purchase Champions into repeat buyers | Champions, Loyal High-Value |
| 3 | Post-purchase email sequence nudging a second order within 30–60 days | Recent Low-Engagement |
| 4 | Low-cost, automated reactivation only (no discount budget) | Lost / Churned |
| 5 | Instrument and track "first-to-second purchase" conversion as a new core KPI going forward | All segments |

---

## 7. Dashboard

The interactive dashboard (`dashboard/index.html`) has four views:
- **Overview** — top-line KPIs with live City/Category/Year filters, revenue trend, category mix, city and age-group breakdowns
- **Core KPIs** — the 5 KPIs above with formulas and rationale, plus day-of-week and product performance
- **Customer Segmentation** — the full RFM deep-dive: segment sizing, revenue concentration, a recency-vs-spend bubble chart, and a top-10 customer leaderboard
- **Data Explorer** — filterable raw order-level table

No build step is required — it's a static HTML/JS file (Chart.js, bundled locally) that can be opened directly or hosted via GitHub Pages.
