
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# PATHS
# ============================================================

BASE = Path.cwd()

# metadata = pd.read_excel("C:/Users/ctrl2/OneDrive/Documents/zonal_metadata_copy.xlsx")

# CHART_FOLDER = Path("results_charts/zonal_analysis")
# CHART_FOLDER.mkdir(parents=True, exist_ok=True)

# ============================================================
# READ SUMMARY FILES
# ============================================================

# all_data = []

# for _, row in metadata.iterrows():

#     zone = row["Zone"]
#     party = row["Party"].strip().upper()

#     summary_path = Path(str(row["Summary_file"]).strip())

#     if not summary_path.is_absolute():
#         summary_path = BASE / summary_path

#     df = pd.read_csv(summary_path)

#     df["Zone"] = zone
#     df["Party"] = party

#     all_data.append(df)

# data = pd.concat(all_data, ignore_index=True)

# zones = metadata["Zone"].unique()
# categories = data["Category"].unique()

# ============================================================
# 1. HEATMAP FOR EACH PARTY
# ============================================================

# for party in ["MGB"]:

#     party_data = data[data["Party"] == party]

#     heatmap = party_data.pivot(
#         index="Zone",
#         columns="Category",
#         values="Percentage (%)"
#     )

#     heatmap = heatmap.reindex(
#         index=zones,
#         columns=categories
#     )

#     plt.figure(figsize=(20, 7))

#     plt.imshow(
#         heatmap,
#         cmap="YlOrRd",
#         aspect="auto",
#         vmin=0,
#         vmax=40
#     )

#     plt.colorbar(label="Percentage (%)")

#     plt.xticks(
#         range(len(categories)),
#         categories,
#         rotation=65,
#         ha="right"
#     )

#     plt.yticks(range(len(zones)), zones)

#     # Display percentage inside each cell
#     for i in range(len(zones)):
#         for j in range(len(categories)):

#             value = heatmap.iloc[i, j]

#             if pd.notna(value):
#                 plt.text(
#                     j, i,
#                     f"{value:.1f}",
#                     ha="center",
#                     va="center",
#                     fontsize=9,
#                     color="white" if value > 25 else "black"
#                 )

#     plt.title(f"{party}: Category Distribution Across Zones")

#     plt.tight_layout()

#     plt.savefig(
#         CHART_FOLDER / f"{party}_heatmap.png",
#         dpi=300,
#         bbox_inches="tight"
#     )

#     plt.show()


# ============================================================
# 2. GROUPED BAR CHART FOR EACH ZONE
# ============================================================

# for zone in zones:

#     zone_data = data[data["Zone"] == zone]

#     mgb = (
#         zone_data[zone_data["Party"] == "MGB"]
#         .set_index("Category")
#         .reindex(categories)["Percentage (%)"]
#         .fillna(0)
#     )

#     # nda = (
#     #     zone_data[zone_data["Party"] == "NDA"]
#     #     .set_index("Category")
#     #     .reindex(categories)["Percentage (%)"]
#     #     .fillna(0)
#     # )

#     x = np.arange(len(categories))
#     width = 0.35

#     plt.figure(figsize=(16, 7))

#     plt.bar(x - width/2, mgb, width, label="MGB")
#     plt.bar(x + width/2, nda, width, label="NDA")

#     plt.xticks(x, categories, rotation=65, ha="right")
#     plt.ylabel("Percentage (%)")
#     plt.title(f"MGB vs NDA: {zone}")
#     plt.legend()

#     plt.tight_layout()

#     plt.savefig(
#         CHART_FOLDER / f"{zone}_bar_chart.png",
#         dpi=300,
#         bbox_inches="tight"
#     )

#     plt.show()


    
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# PATHS
# ============================================================

metadata=pd.read_excel("C:/Users/ctrl2/OneDrive/Documents/zonal_metadata_copy.xlsx")

CHART_FOLDER = Path("results_charts/zonal_election_analysis")
CHART_FOLDER.mkdir(parents=True, exist_ok=True)

OUTPUT_FOLDER = Path("results/zonal_analysis")
OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

# ============================================================
# READ SUMMARY FILES AND ATTACH WINNING STATUS
# ============================================================

all_data = []

for _, row in metadata.iterrows():

    party = row["party"].strip().upper()

    summary_path = Path(str(row["summary_file"]).strip())

    df = pd.read_csv(summary_path)

    df["Zone"] = row["zone"]
    df["Party"] = party

    # Select the corresponding party's winning status
    if party == "MGB":
        df["Win_Status"] = int(row["MGB_status"])

    else:
        df["Win_Status"] = int(row["NDA_status"])

    all_data.append(df)

data = pd.concat(all_data, ignore_index=True)

data.to_csv(
    OUTPUT_FOLDER / "zonal_topics_with_win_status.csv",
    index=False
)

categories = data["Category"].unique()

# ============================================================
# 1. WINNING VS LOSING ZONES: BAR CHART
# ============================================================

for party in ["MGB", "NDA"]:

    party_data = data[data["Party"] == party]

    # Average percentage in zones where party won
    winning = (
        party_data[party_data["Win_Status"] == 1]
        .groupby("Category")["Percentage (%)"]
        .mean()
        .reindex(categories)
    )

    # Average percentage in zones where party lost
    losing = (
        party_data[party_data["Win_Status"] == 0]
        .groupby("Category")["Percentage (%)"]
        .mean()
        .reindex(categories)
    )

    if winning.isna().all() or losing.isna().all():
        print(f"{party}: Need both winning and losing zones for comparison.")
        continue

    x = np.arange(len(categories))
    width = 0.35

    plt.figure(figsize=(16, 7))

    plt.bar(
        x - width/2,
        winning,
        width,
        label="Winning Zones"
    )

    plt.bar(
        x + width/2,
        losing,
        width,
        label="Losing Zones"
    )

    plt.xticks(x, categories, rotation=65, ha="right")
    plt.ylabel("Average Category Percentage (%)")
    plt.title(f"{party}: Topic Emphasis in Winning vs Losing Zones")

    plt.legend()
    plt.tight_layout()

    plt.savefig(
        CHART_FOLDER / f"{party}_winning_vs_losing.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()


# ============================================================
# 2. CORRELATION WITH WINNING STATUS
# ============================================================

correlation_results = []

for party in ["MGB", "NDA"]:

    party_data = data[data["Party"] == party]

    # One row per zone, one column per category
    pivot_df = party_data.pivot(
        index="Zone",
        columns="Category",
        values="Percentage (%)"
    )

    # Attach winning status for each zone
    status = (
        party_data.groupby("Zone")["Win_Status"]
        .first()
    )

    pivot_df["Win_Status"] = status

    for cat in categories:

        # Correlation is undefined when either variable is constant
        if (
            pivot_df[cat].nunique() < 2
            or pivot_df["Win_Status"].nunique() < 2
        ):
            corr = np.nan
        else:
            corr = pivot_df[cat].corr(pivot_df["Win_Status"])

        correlation_results.append({
            "Party": party,
            "Category": cat,
            "Correlation": corr
        })


corr_df = pd.DataFrame(correlation_results)

corr_df.to_csv(
    OUTPUT_FOLDER / "topic_win_correlations.csv",
    index=False
)

# ============================================================
# CORRELATION HEATMAP
# ============================================================

heatmap = corr_df.pivot(
    index="Party",
    columns="Category",
    values="Correlation"
)

heatmap = heatmap.reindex(
    index=["MGB", "NDA"],
    columns=categories
)

plt.figure(figsize=(17, 4))

plt.imshow(
    heatmap,
    cmap="coolwarm",
    vmin=-1,
    vmax=1,
    aspect="auto"
)

plt.colorbar(label="Correlation with Winning Status")

plt.xticks(
    range(len(categories)),
    categories,
    rotation=65,
    ha="right"
)

plt.yticks([0, 1], ["MGB", "NDA"])

plt.title("Correlation Between Topic Emphasis and Electoral Victory")

plt.tight_layout()

plt.savefig(
    CHART_FOLDER / "topic_win_correlation_heatmap.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print(corr_df)

