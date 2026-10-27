import numpy as np
from scipy.special import rel_entr

# Align categories in both datasets
manifesto_df = manifesto_df.set_index("Category").reindex(CATEGORIES)
pooled_df = rally_pooled_df.set_index("Category").reindex(CATEGORIES)

# Get probability distributions using counts
P = manifesto_df["Count"].fillna(0).to_numpy(dtype=float)
Q = rally_pooled_df["Count"].fillna(0).to_numpy(dtype=float)

# Small smoothing value to avoid log(0)
epsilon = 1e-10

P = P + epsilon
Q = Q + epsilon

# Normalize so each distribution sums to 1
P = P / P.sum()
Q = Q / Q.sum()

# Calculate KL divergence
kl_manifesto_rally = np.sum(rel_entr(P, Q))
kl_rally_manifesto = np.sum(rel_entr(Q, P))

print("KL Divergence Results")
print("-------------------------")
print(f"Manifesto → Rallies: {kl_manifesto_rally:.4f}")
print(f"Rallies → Manifesto: {kl_rally_manifesto:.4f}")