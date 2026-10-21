import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
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

manifesto_path = Path(
    "results/manifesto_results/gemini/MGB_summary.csv"
)

rally_pooled_path=Path("results/rally_results/mahagathbandhan/MGB_pooled_rally_summary.csv")

manifesto_df = pd.read_csv(manifesto_path)
rally_pooled_df = pd.read_csv(rally_pooled_path)
# Ensure both have categories in the same order
# manifesto_df = manifesto_df.set_index("Category").reindex(CATEGORIES)
# rally_pooled_df = rally_pooled_df.set_index("Category").reindex(CATEGORIES)

# categories = CATEGORIES

# manifesto = manifesto_df["Percentage (%)"].fillna(0)
# rallies = rally_pooled_df["Percentage (%)"].fillna(0)

# x = np.arange(len(categories))
# width = 0.35

# plt.figure(figsize=(16, 7))

# plt.bar(x - width/2, manifesto, width, label="Manifesto")
# plt.bar(x + width/2, rallies, width, label="Rallies")

# plt.xticks(x, categories, rotation=60, ha="right")
# plt.ylabel("Percentage (%)")
# plt.title("MGB Manifesto vs Rally Speeches")
# plt.legend()


# Path("results_charts").mkdir(parents=True, exist_ok=True)

# plt.tight_layout()
# plt.savefig("results_charts/MGB_manifesto_vs_rallies.png", dpi=300, bbox_inches="tight")
# plt.show()


###########################    probability distribution   ############################



# Ensure categories are in the same order
# manifesto_df = manifesto_df.set_index("Category").reindex(CATEGORIES)
# pooled_df = rally_pooled_df.set_index("Category").reindex(CATEGORIES)

# # Convert percentages into probabilities
# manifesto_prob = manifesto_df["Percentage (%)"].fillna(0) / 100
# rally_prob = rally_pooled_df["Percentage (%)"].fillna(0) / 100

# x = np.arange(len(CATEGORIES))

# plt.figure(figsize=(16, 7))

# plt.plot(x, manifesto_prob, marker="o", label="MGB Manifesto")
# plt.plot(x, rally_prob, marker="o", label="MGB Rally Speeches")

# plt.xticks(x, CATEGORIES, rotation=60, ha="right")
# plt.xlabel("Categories")
# plt.ylabel("Probability")
# plt.title("Probability Distribution of Categories: MGB Manifesto vs Rallies")

# plt.legend()
# plt.grid(alpha=0.3)
# plt.tight_layout()

# # Save graph
# Path("results_charts").mkdir(exist_ok=True)

# plt.savefig(
#     "results_charts/MGB_probability_distribution.png",
#     dpi=300,
#     bbox_inches="tight"
# )

# plt.show()


##########################   KL divergence   ####################

# import numpy as np
# from scipy.special import rel_entr

# # Align categories in both datasets
# manifesto_df = manifesto_df.set_index("Category").reindex(CATEGORIES)
# pooled_df = rally_pooled_df.set_index("Category").reindex(CATEGORIES)

# # Get probability distributions using counts
# P = manifesto_df["Count"].fillna(0).to_numpy(dtype=float)
# Q = rally_pooled_df["Count"].fillna(0).to_numpy(dtype=float)

# # Small smoothing value to avoid log(0)
# epsilon = 1e-10

# P = P + epsilon
# Q = Q + epsilon

# # Normalize so each distribution sums to 1
# P = P / P.sum()
# Q = Q / Q.sum()

# # Calculate KL divergence
# kl_manifesto_rally = np.sum(rel_entr(P, Q))
# kl_rally_manifesto = np.sum(rel_entr(Q, P))

# print("KL Divergence Results")
# print("-------------------------")
# print(f"Manifesto → Rallies: {kl_manifesto_rally:.4f}")
# print(f"Rallies → Manifesto: {kl_rally_manifesto:.4f}")