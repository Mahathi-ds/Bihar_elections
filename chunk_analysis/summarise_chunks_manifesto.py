
import pandas as pd
from collections import Counter
from pathlib import Path

CATEGORIES = [
    "Agriculture and Farmers",
    "Employement and jobs",
    "Education",
    "Women Development",
    "Health",
    "Governance",
    "Infrastructure",
    "Religion and Culture",
    "Social justice and Deprived communities",
    "Law and Order",
    "Welfare and Funds",
    "Divyang Welfare",
    "Already executed promises",
    "Content about the Opposition party",
    "Others"
]

# ============================================================
# MANIFESTO SUMMARY
# ============================================================

detailed_csv = Path("results/manifesto_results/gemini/NDA_detailed.csv")

summary_path = Path("results/manifesto_results/gemini/NDA_summary.csv")

# Read already classified chunks
detailed_df = pd.read_csv(detailed_csv)

# Extract primary categories
main_categories = [
    cat for cat in detailed_df["Primary_Category"].dropna()
    if cat in CATEGORIES
]

count = Counter(main_categories)
total = len(main_categories)

summary_data = []

for cat in CATEGORIES:
    num = count.get(cat, 0)
    percent = round((num / total) * 100, 2) if total > 0 else 0

    summary_data.append([cat, num, percent])

summary_df = pd.DataFrame(
    summary_data,
    columns=["Category", "Count", "Percentage (%)"]
)

# Save summary
summary_df.to_csv(
    summary_path,
    index=False,
    encoding="utf-8-sig"
)

print(f"\nMGB Manifesto Summary")
print(f"Total successfully classified chunks: {total}")
print(summary_df)
print(f"\nSaved to: {summary_path}")
