import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# CATEGORIES = [
#        "Agriculture and Farmers",
#        "Employement and jobs",
#        "Education",
#        "Women Development",
#        "Health",
#        "Governance",
#        "Infrastructure",
#        "Religion and Culture",
#        "Social justice and Deprived communities",
#        "Law and Order",
#        "Welfare and Funds",
#        "Divyang Welfare",
#        "Already executed promises",
#        "Content about the Opposition party",
#        "Others"
# ]

# # Existing individual speech summaries
# summary_folder = Path(
#     "results/rally_results/mahagathbandhan/gemini_summary_files"
# )

# summary_files = list(summary_folder.glob("*_summary.csv"))

# pooled_counts = {cat: 0 for cat in CATEGORIES}

# for file in summary_files:
#     df = pd.read_csv(file)

#     for _, row in df.iterrows():
#         if row["Category"] in pooled_counts:
#             pooled_counts[row["Category"]] += int(row["Count"])

# total = sum(pooled_counts.values())

# pooled_df = pd.DataFrame({
#     "Category": CATEGORIES,
#     "Count": [pooled_counts[cat] for cat in CATEGORIES]
# })

# pooled_df["Percentage (%)"] = (
#     pooled_df["Count"] / total * 100
# ).round(2) if total > 0 else 0

# # Save pooled summary outside the individual summary folder
# pooled_path = Path(
#     "results/rally_results/mahagathbandhan/MGB_pooled_rally_summary.csv"
# )

# pooled_df.to_csv(pooled_path, index=False, encoding="utf-8-sig")

# print(f"Speeches pooled: {len(summary_files)}")
# print(f"Total classified rally chunks: {total}")
# print(pooled_df)




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
       "Content about the Opposition party",
       "Others"
]

# Existing individual speech summaries
summary_folder = Path(
    "results/manifesto_results/gemini/MGB_detailed.csv"
)

# 
pooled_counts = {cat: 0 for cat in CATEGORIES}


df = pd.read_csv(summary_folder)

for _, row in df.iterrows():
    if row["Category"] in pooled_counts:
        pooled_counts[row["Category"]] += int(row["Count"])

total = sum(pooled_counts.values())

pooled_df = pd.DataFrame({
    "Category": CATEGORIES,
    "Count": [pooled_counts[cat] for cat in CATEGORIES]
})

pooled_df["Percentage (%)"] = (
    pooled_df["Count"] / total * 100
).round(2) if total > 0 else 0

# Save pooled summary outside the individual summary folder
pooled_path = Path(
    "results/manifesto_results/gemini/MGB_summary.csv"
)

pooled_df.to_csv(pooled_path, index=False, encoding="utf-8-sig")

