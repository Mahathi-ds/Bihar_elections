import os
import pandas as pd
from collections import Counter
import time
from pathlib import Path

CATEGORIES = [
    "Agriculture and Farmers",
    "Women’s Development",
    "Education",
    "Women Empowerment",
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

for party in ["Mahagathbandhan"]:
    # detailed_folder = Path("results/rally_results") / party / "gemini"

    detailed_folder=Path("results/manifesto_results/gemini")

    summary_folder = (
        Path("results/rally_results")
        / party
        / "gemini_summary_files"
    )

    summary_folder.mkdir(parents=True, exist_ok=True)

    # Get all already-classified detailed CSV files
    detailed_files = sorted(detailed_folder.glob("*_detailed.csv"))

    print(f"\nFound {len(detailed_files)} detailed CSVs for {party}")

    for detailed_csv in detailed_files:

        # Extract speech name from CSV filename
        speech_name = detailed_csv.stem.removesuffix("_detailed")

        try:
            detailed_df = pd.read_csv(detailed_csv)

        except pd.errors.EmptyDataError:
            print(f"[SKIP] Empty CSV: {detailed_csv.name}")
            continue

        if "Primary_Category" not in detailed_df.columns:
            print(f"[SKIP] Missing Primary_Category: {detailed_csv.name}")
            continue

        # Extract successfully classified primary categories
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

        # Save summary using extracted speech name
        output_path = summary_folder / f"{speech_name}_summary.csv"

        summary_df.to_csv(
            output_path,
            index=False,
            encoding="utf-8-sig"
        )

        print(f"\nCompleted: {speech_name}")
        print(f"Total classified chunks: {total}")
        print(f"Saved: {output_path}")