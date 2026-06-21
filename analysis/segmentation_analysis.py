"""
ApexPlanet — Task 3: Deep-Dive Analysis (Customer Segmentation)
==================================================================
Performs RFM (Recency, Frequency, Monetary) based customer segmentation
on the cleaned order dataset and exports:
  1. data/customer_segments.csv   -> one row per customer, with RFM scores + segment label
  2. dashboard/data/data.js       -> aggregated JSON consumed by the interactive dashboard

Run:
    python analysis/segmentation_analysis.py
"""

import pandas as pd
import json

INPUT_FILE = "data/ApexPlanet_Cleaned_Dataset.xlsx"
SEGMENTS_OUT = "data/customer_segments.csv"
DASHBOARD_JS_OUT = "dashboard/data/data.js"


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_excel(path)
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    return df


def build_customer_segments(df: pd.DataFrame) -> pd.DataFrame:
    """RFM scoring + rule-based segment assignment, one row per customer."""
    snapshot_date = df["Order_Date"].max() + pd.Timedelta(days=1)

    cust = (
        df.groupby("Customer_ID")
        .agg(
            Customer_Name=("Customer_Name", "first"),
            City=("City", "first"),
            Age=("Age", "first"),
            Gender=("Gender", "first"),
            Last_Purchase=("Order_Date", "max"),
            Frequency=("Order_ID", "count"),
            Monetary=("Total_Sales", "sum"),
            Avg_Order_Value=("Total_Sales", "mean"),
            Fav_Category=("Category", lambda x: x.mode()[0]),
        )
        .reset_index()
    )

    cust["Recency_Days"] = (snapshot_date - cust["Last_Purchase"]).dt.days

    # Quartile scoring: 4 = best. Recency is inverted (fewer days = better = 4).
    cust["R_Score"] = pd.qcut(cust["Recency_Days"], 4, labels=[4, 3, 2, 1]).astype(int)
    cust["F_Score"] = pd.qcut(cust["Frequency"].rank(method="first"), 4, labels=[1, 2, 3, 4]).astype(int)
    cust["M_Score"] = pd.qcut(cust["Monetary"], 4, labels=[1, 2, 3, 4]).astype(int)
    cust["RFM_Score"] = cust["R_Score"] + cust["F_Score"] + cust["M_Score"]

    def assign_segment(row) -> str:
        r, f, m = row["R_Score"], row["F_Score"], row["M_Score"]
        if r >= 3 and f >= 3 and m >= 3:
            return "Champions"
        if r >= 3 and m >= 3:
            return "Loyal High-Value"
        if r >= 3 and f <= 2:
            return "Recent Low-Engagement"
        if r <= 2 and f >= 3 and m >= 3:
            return "At-Risk High-Value"
        if r <= 2 and m <= 2:
            return "Lost / Churned"
        return "Needs Attention"

    cust["Segment"] = cust.apply(assign_segment, axis=1)
    return cust


def build_dashboard_payload(df: pd.DataFrame, cust: pd.DataFrame) -> dict:
    total_revenue = df["Total_Sales"].sum()
    total_orders = df["Order_ID"].nunique()
    total_customers = df["Customer_ID"].nunique()
    repeat_customers = int((df["Customer_ID"].value_counts() > 1).sum())

    df["YearMonth"] = df["Order_Date"].dt.to_period("M").astype(str)
    monthly = (
        df.groupby("YearMonth")
        .agg(Revenue=("Total_Sales", "sum"), Orders=("Order_ID", "count"))
        .reset_index()
    )

    category = (
        df.groupby("Category")
        .agg(Revenue=("Total_Sales", "sum"), Orders=("Order_ID", "count"), Avg_Order=("Total_Sales", "mean"))
        .reset_index()
        .sort_values("Revenue", ascending=False)
    )

    city = (
        df.groupby("City")
        .agg(Revenue=("Total_Sales", "sum"), Orders=("Order_ID", "count"), Customers=("Customer_ID", "nunique"))
        .reset_index()
        .sort_values("Revenue", ascending=False)
    )

    product = (
        df.groupby(["Category", "Product"])
        .agg(Revenue=("Total_Sales", "sum"), Units=("Quantity", "sum"), Orders=("Order_ID", "count"))
        .reset_index()
        .sort_values("Revenue", ascending=False)
    )

    age_order = ["18-25", "26-35", "36-45", "46-55", "56-65"]
    age_group = df.groupby("Age_Group").agg(Revenue=("Total_Sales", "sum"), Orders=("Order_ID", "count"), AOV=("Total_Sales", "mean")).reset_index()
    age_group["Age_Group"] = pd.Categorical(age_group["Age_Group"], categories=age_order, ordered=True)
    age_group = age_group.sort_values("Age_Group")

    gender = df.groupby("Gender").agg(Revenue=("Total_Sales", "sum"), Orders=("Order_ID", "count"), AOV=("Total_Sales", "mean")).reset_index()

    dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    dow = df.groupby("Day_of_Week").agg(Revenue=("Total_Sales", "sum"), Orders=("Order_ID", "count")).reset_index()
    dow["Day_of_Week"] = pd.Categorical(dow["Day_of_Week"], categories=dow_order, ordered=True)
    dow = dow.sort_values("Day_of_Week")

    segments = (
        cust.groupby("Segment")
        .agg(
            Customers=("Customer_ID", "count"),
            Total_Revenue=("Monetary", "sum"),
            Avg_Revenue=("Monetary", "mean"),
            Avg_Frequency=("Frequency", "mean"),
            Avg_Recency=("Recency_Days", "mean"),
        )
        .reset_index()
        .sort_values("Total_Revenue", ascending=False)
    )

    top_customers = cust.sort_values("Monetary", ascending=False).head(10)[
        ["Customer_Name", "City", "Segment", "Frequency", "Monetary", "Recency_Days"]
    ]

    orders_raw = df[
        ["Order_ID", "Order_Date", "Customer_ID", "City", "Product", "Category",
         "Quantity", "Unit_Price", "Total_Sales", "Age_Group", "Gender", "Day_of_Week", "Month_Name"]
    ].assign(Order_Date=lambda d: d["Order_Date"].dt.strftime("%Y-%m-%d"))

    return {
        "kpis": {
            "total_revenue": round(float(total_revenue), 2),
            "total_orders": int(total_orders),
            "total_customers": int(total_customers),
            "aov": round(float(df["Total_Sales"].mean()), 2),
            "repeat_rate": round(repeat_customers / total_customers * 100, 2),
            "repeat_customers": repeat_customers,
        },
        "monthly": monthly.to_dict(orient="records"),
        "category": category.to_dict(orient="records"),
        "city": city.to_dict(orient="records"),
        "product": product.to_dict(orient="records"),
        "age_group": age_group.to_dict(orient="records"),
        "gender": gender.to_dict(orient="records"),
        "day_of_week": dow.to_dict(orient="records"),
        "segments": segments.to_dict(orient="records"),
        "top_customers": top_customers.to_dict(orient="records"),
        "orders_raw": orders_raw.to_dict(orient="records"),
    }


def main():
    df = load_data(INPUT_FILE)
    cust = build_customer_segments(df)
    cust.to_csv(SEGMENTS_OUT, index=False)
    print(f"Wrote {SEGMENTS_OUT} ({len(cust)} customers)")

    payload = build_dashboard_payload(df, cust)
    with open(DASHBOARD_JS_OUT, "w") as f:
        f.write("const DASHBOARD_DATA = " + json.dumps(payload, default=str) + ";")
    print(f"Wrote {DASHBOARD_JS_OUT}")

    print("\nSegment distribution:")
    print(cust["Segment"].value_counts())


if __name__ == "__main__":
    main()
