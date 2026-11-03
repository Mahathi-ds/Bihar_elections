import pandas as pd
from pathlib import Path

CSV_FOLDER = Path("results/rally_results/NDA/qwen")
CHUNKS_FOLDER = Path("chunks/speeches/NDA")

all_rows = []

for csv_file in sorted(CSV_FOLDER.rglob("*_detailed.csv")):
    video_name = csv_file.stem.removesuffix("_detailed")
    df = pd.read_csv(csv_file, encoding="utf-8-sig")

    for _, row in df.iterrows():

        chunk_name = str(row["Chunk"]).strip()

        # Find corresponding chunk text
        chunk_path = CHUNKS_FOLDER / video_name / chunk_name

        if chunk_path.exists():
            chunk_text = chunk_path.read_text(encoding="utf-8").strip()
        else:
            chunk_text = ""
            print(f"Missing chunk: {chunk_path}")

        all_rows.append({
            "video_name": video_name,
            "chunk_name": chunk_name,
            "chunk_text": chunk_text,
            "qwen_primary": row["Primary_Category"],
            "qwen_secondary": row["Secondary_Category"]
        })

combined = pd.DataFrame(
    all_rows,
    columns=[
        "video_name",
        "chunk_name",
        "chunk_text",
        "qwen_primary",
        "qwen_secondary"
    ]
)

combined.to_excel(
    "nda_qwen_classifications.xlsx",
    index=False
)

print("Total chunks:", len(combined))
print("Saved nda_qwen_classifications.xlsx")
print("Excel saved at:", Path("nda_qwen_classifications.xlsx").resolve())