
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path
from scipy.stats import pointbiserialr

BASE = Path.cwd()

# ==========================================
# METADATA FILES FOR BOTH PARTIES
# ==========================================

METADATA_FILES = {
    "NDA": "C:/Users/ctrl2/OneDrive/Documents/nda_win_metadata.xlsx",
    "MGB": "C:/Users/ctrl2/OneDrive/Documents/mgb_win_metadata.xlsx"
}

# ==========================================
# PROCESS EACH PARTY SEPARATELY
# ==========================================

for party, metadata_file in METADATA_FILES.items():

    print(f"\nProcessing {party}...")

    CHART_FOLDER = Path(f"All_about_zones/results_charts/{party.lower()}_win_analysis")
    CHART_FOLDER.mkdir(parents=True, exist_ok=True)

    # ==========================================
    # 1. READ METADATA AND SUMMARY FILES
    # ==========================================

    metadata = pd.read_excel(metadata_file)

    # Standardise column names
    metadata.columns = metadata.columns.str.strip()

    metadata["Winning_status"] = pd.to_numeric(
        metadata["Winning_status"], errors="raise"
    ).astype(int)

    all_data = []

    for _, row in metadata.iterrows():

        path = Path(
            str(row["Summary_file"]).strip().strip('"').strip("'")
        )

        if not path.is_absolute():
            path = BASE / path

        df = pd.read_csv(path)

        percentages = dict(
            zip(df["Category"], df["Percentage (%)"])
        )

        percentages["Zone"] = str(row["Zone"]).strip()
        percentages["Winning_status"] = row["Winning_status"]

        all_data.append(percentages)

    data = pd.DataFrame(all_data)

    categories = [
        col for col in data.columns
        if col not in ["Zone", "Winning_status"]
    ]

    data[categories] = data[categories].apply(
        pd.to_numeric, errors="coerce"
    ).fillna(0)

    print("Total videos:", len(data))
    print("Winning videos:", sum(data["Winning_status"] == 1))
    print("Losing videos:", sum(data["Winning_status"] == 0))

    # ==========================================
    # 2. ZONE-WISE PERCENTAGE HEATMAP
    # ==========================================

    heatmap_data = data.set_index("Zone")[categories]

    heatmap_data.index = [
        f"{row['Zone']} ({'Won' if row['Winning_status'] == 1 else 'Lost'})"
        for _, row in data.iterrows()
    ]

    plt.figure(figsize=(20, 8))

    sns.heatmap(
        heatmap_data,
        annot=True,
        fmt=".1f",
        cmap="YlOrRd",
        linewidths=0.5,
        vmin=0,
        vmax=heatmap_data.max().max(),
        cbar_kws={"label": "Percentage (%)"},
        annot_kws={"size": 8}
    )

    plt.title(f"{party}: Category Percentages Across All Zones")
    plt.xlabel("Categories")
    plt.ylabel("Zones (Election Result)")

    plt.xticks(rotation=65, ha="right")
    plt.yticks(rotation=0)

    plt.tight_layout()

    plt.savefig(
        CHART_FOLDER / "1_zone_percentage_heatmap.png",
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    # ==========================================
    # 3. CORRELATION WITH WINNING STATUS
    # ==========================================

    correlations = {}
    p_values = {}

    for category in categories:

        if data[category].nunique() < 2:
            correlations[category] = np.nan
            p_values[category] = np.nan

        else:
            corr, p_value = pointbiserialr(
                data["Winning_status"],
                data[category]
            )

            correlations[category] = corr
            p_values[category] = p_value

    corr_series = pd.Series(correlations).sort_values()

    plt.figure(figsize=(12, 8))

    colors = [
        "seagreen" if value > 0 else "indianred"
        for value in corr_series
    ]

    bars = plt.barh(
        corr_series.index,
        corr_series.values,
        color=colors
    )

    for bar, value in zip(bars, corr_series.values):

        if pd.notna(value):

            plt.text(
                value + (0.02 if value >= 0 else -0.02),
                bar.get_y() + bar.get_height()/2,
                f"{value:.2f}",
                va="center",
                ha="left" if value >= 0 else "right",
                fontsize=9
            )

    plt.axvline(0, color="black", linewidth=1)
    plt.xlim(-1.1, 1.1)

    plt.xlabel("Correlation with Winning Status")
    plt.title(f"{party}: Topic Percentage vs Winning Status")

    plt.tight_layout()

    plt.savefig(
        CHART_FOLDER / "2_category_correlation.png",
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    # Save correlation and p-value results
    correlation_results = pd.DataFrame({
        "Category": categories,
        "Correlation": [correlations[c] for c in categories],
        "P_Value": [p_values[c] for c in categories]
    })

    correlation_results.to_csv(
        CHART_FOLDER / "correlation_results.csv",
        index=False
    )

    # ==========================================
    # 4. WINNING VS LOSING CATEGORY COMPARISON
    # ==========================================

    winning = data[
        data["Winning_status"] == 1
    ][categories].mean()

    losing = data[
        data["Winning_status"] == 0
    ][categories].mean()

    x = np.arange(len(categories))
    width = 0.35

    plt.figure(figsize=(18, 7))

    plt.bar(
        x - width/2,
        winning,
        width,
        label="Winning Zones",
        color="seagreen"
    )

    plt.bar(
        x + width/2,
        losing,
        width,
        label="Losing Zones",
        color="indianred"
    )

    plt.xticks(x, categories, rotation=65, ha="right")

    plt.ylabel("Average Category Percentage (%)")
    plt.title(f"{party}: Topics Spoken in Winning vs Losing Zones")

    plt.legend()
    plt.tight_layout()

    plt.savefig(
        CHART_FOLDER / "3_winning_vs_losing.png",
        dpi=150,
        bbox_inches="tight"
    )

    plt.close()

    print(f"Visualisations saved in: {CHART_FOLDER}")

print("\nAll visualisations generated successfully!")
