
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# ============================================================
# PATHS
# ============================================================

BASE = Path.cwd()

CHART_FOLDER = BASE / "results_charts/zonal_analysis"
RESULT_FOLDER = BASE / "results/zonal_analysis"

CHART_FOLDER.mkdir(parents=True, exist_ok=True)
RESULT_FOLDER.mkdir(parents=True, exist_ok=True)

metadata = pd.read_csv("zonal_videos.csv")

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
# 1. COMBINE VIDEO SUMMARIES BY ZONE AND PARTY
# ============================================================

all_data = []

metadata["Party"] = metadata["Party"].str.strip().str.upper()
metadata["Zone"] = metadata["Zone"].str.strip()

# Check that each zone has 2 videos from each party
video_counts = metadata.groupby(["Zone", "Party"]).size()

if len(metadata) != 20 or len(video_counts) != 10 or not (video_counts == 2).all():
    raise ValueError(
        "Expected exactly 2 MGB and 2 NDA videos in each of 5 zones."
    )

for _, row in metadata.iterrows():

    file = BASE / str(row["Summary_File"]).strip()

    df = pd.read_csv(file, encoding="utf-8-sig")

    if not {"Category", "Count"}.issubset(df.columns):
        raise ValueError(f"Missing Category/Count columns in {file}")

    if df["Category"].duplicated().any():
        raise ValueError(f"Duplicate categories in {file}")

    unknown = set(df["Category"].dropna()) - set(CATEGORIES)
    if unknown:
        raise ValueError(f"Unknown categories in {file}: {unknown}")

    for _, r in df.iterrows():

        all_data.append({
            "Zone": row["Zone"],
            "Party": row["Party"],
            "Category": r["Category"],
            "Count": int(r["Count"])
        })

combined = pd.DataFrame(all_data)

# Sum counts of both videos
pooled = combined.groupby(
    ["Zone", "Party", "Category"],
    as_index=False
)["Count"].sum()

# Fill absent categories with zero
zones = metadata["Zone"].drop_duplicates().tolist()

complete_index = pd.MultiIndex.from_product(
    [zones, ["MGB", "NDA"], CATEGORIES],
    names=["Zone", "Party", "Category"]
)

pooled = (
    pooled.set_index(["Zone", "Party", "Category"])
    .reindex(complete_index, fill_value=0)
    .reset_index()
)

# Calculate percentage for each party within each zone
pooled["Total"] = pooled.groupby(
    ["Zone", "Party"]
)["Count"].transform("sum")

if (pooled["Total"] == 0).any():
    raise ValueError("At least one party-zone has zero classified chunks.")

pooled["Percentage"] = (
    pooled["Count"] / pooled["Total"] * 100
).round(2)

pooled.to_csv(
    RESULT_FOLDER / "zonal_pooled_summary.csv",
    index=False,
    encoding="utf-8-sig"
)

print(pooled)


# ============================================================
# 2. HEATMAP - ONE FOR EACH PARTY
# ============================================================

# Same colour scale for both heatmaps
max_percent = pooled["Percentage"].max()

for party in ["MGB", "NDA"]:

    df = pooled[pooled["Party"] == party]

    matrix = df.pivot(
        index="Zone",
        columns="Category",
        values="Percentage"
    ).reindex(index=zones, columns=CATEGORIES)

    plt.figure(figsize=(17, 6))

    plt.imshow(
        matrix,
        cmap="YlOrRd",
        aspect="auto",
        vmin=0,
        vmax=max_percent
    )

    plt.colorbar(label="Percentage (%)")

    plt.xticks(
        range(len(CATEGORIES)),
        CATEGORIES,
        rotation=65,
        ha="right"
    )

    plt.yticks(range(len(zones)), zones)

    plt.title(f"{party}: Category Distribution Across Zones")

    plt.tight_layout()

    plt.savefig(
        CHART_FOLDER / f"{party}_heatmap.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()


# ============================================================
# 3. GROUPED BAR CHART - ONE FOR EACH ZONE
# ============================================================

for zone in zones:

    zone_df = pooled[pooled["Zone"] == zone]

    mgb = zone_df[
        zone_df["Party"] == "MGB"
    ].set_index("Category").reindex(CATEGORIES)

    nda = zone_df[
        zone_df["Party"] == "NDA"
    ].set_index("Category").reindex(CATEGORIES)

    x = np.arange(len(CATEGORIES))
    width = 0.35

    plt.figure(figsize=(16, 7))

    plt.bar(
        x - width/2,
        mgb["Percentage"],
        width,
        label="MGB"
    )

    plt.bar(
        x + width/2,
        nda["Percentage"],
        width,
        label="NDA"
    )

    plt.xticks(x, CATEGORIES, rotation=65, ha="right")

    plt.xlabel("Categories")
    plt.ylabel("Percentage (%)")
    plt.title(f"{zone}: MGB vs NDA Topic Distribution")
    plt.legend()

    plt.tight_layout()

    plt.savefig(
        CHART_FOLDER / f"{zone}_comparison.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.show()
