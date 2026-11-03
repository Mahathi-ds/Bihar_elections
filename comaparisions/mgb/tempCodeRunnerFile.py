manifesto_df = manifesto_df.set_index("Category").reindex(CATEGORIES)
rally_pooled_df = rally_pooled_df.set_index("Category").reindex(CATEGORIES)

categories = CATEGORIES

manifesto = manifesto_df["Percentage (%)"].fillna(0)
rallies = rally_pooled_df["Percentage (%)"].fillna(0)

x = np.arange(len(categories))
width = 0.35

plt.figure(figsize=(16, 7))

plt.bar(x - width/2, manifesto, width, label="Manifesto")
plt.bar(x + width/2, rallies, width, label="Rallies")

plt.xticks(x, categories, rotation=60, ha="right")
plt.ylabel("Percentage (%)")
plt.title("MGB Manifesto vs Rally Speeches")
plt.legend()


Path("results_charts").mkdir(parents=True, exist_ok=True)

plt.tight_layout()
plt.savefig("results_charts/MGB_manifesto_vs_rallies.png", dpi=150, bbox_inches="tight")
plt.show()