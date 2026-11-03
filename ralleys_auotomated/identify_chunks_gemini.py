
import pandas as pd
from pathlib import Path

BASE = Path.cwd()

# ==========================================
# STEP 1: COMBINE MGB AND NDA CLASSIFICATIONS
# ==========================================

mgb = pd.read_excel(BASE / "mgb_qwen_classifications.xlsx")
nda = pd.read_excel(BASE / "nda_qwen_classifications.xlsx")

# Combine rows
qwen = pd.concat(
    [mgb, nda],
    ignore_index=True
)

# Save combined classifications
qwen.to_excel(
    BASE / "qwen_classifications.xlsx",
    index=False
)

print("MGB and NDA classifications combined!")
print("Total classification rows:", len(qwen))


# ==========================================
# STEP 2: MERGE INTO HINDI_5CHUNKS
# ==========================================

hindi = pd.read_excel(BASE / "hindi_5chunks.xlsx")

# Remove accidental spaces from column names
qwen.columns = qwen.columns.str.strip()
hindi.columns = hindi.columns.str.strip()

# Matching columns
keys = ["video_name", "chunk_name"]

# Classification columns from qwen
classification_cols = [
    col for col in qwen.columns
    if col not in keys + ["chunk_text"]
]

# Keep only required columns from qwen
qwen_subset = qwen[keys + classification_cols]

# Merge classifications into hindi_5chunks
combined = hindi.merge(
    qwen_subset,
    on=keys,
    how="left",
    validate="many_to_one"
)

# Save the updated Hindi file
combined.to_excel(
    BASE / "hindi_5chunks.xlsx",
    index=False
)

print("Qwen classifications added to hindi_5chunks!")

# Check unmatched chunks
unmatched = combined[classification_cols].isna().all(axis=1)

print("Unmatched chunks:", unmatched.sum())
print("Total Hindi chunks:", len(combined))
print("Final columns:", combined.columns.tolist())
