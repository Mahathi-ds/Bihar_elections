import pandas as pd
from pathlib import Path

BASE_FOLDER = Path("chunks/manifestoes")
RESULTS_FOLDER = Path("results")
EXCEL_FILE = "Bihar_Manifesto_Annotation_Sheet.xlsx"

MANIFESTOS = {
    "MGB": BASE_FOLDER / "MGB_Manifesto_new",
    "NDA": BASE_FOLDER / "NDA_Manifesto_new",
}

COLUMNS = [
    "id",
    "party",
    "chunk",

    "annotator_1_primary",
    "annotator_1_secondary",
    "annotator_2_primary",
    "annotator_2_secondary",
    "annotator_3_primary",
    "annotator_3_secondary",

    "annotators_primary_agreement",
    "annotators_secondary_agreement",

    "GEMINI model",
    "GEMINI_primary",
    "GEMINI_secondary",
]

all_rows = []

for party, folder_path in MANIFESTOS.items():

    print("\n" + "=" * 70)
    print(f"BUILDING ROWS FOR {party}")
    print("=" * 70)

    csv_file = RESULTS_FOLDER / f"Manifesto_{party}_detailed.csv"

    if not csv_file.exists():
        print(f"NO CSV: {csv_file} -- run classify_manifesto_gemini_bihar.py first")
        continue

    detailed_df = pd.read_csv(csv_file)

    for _, row in detailed_df.iterrows():

        chunk_file = str(row["Chunk"])
        chunk_path = folder_path / chunk_file

        if not chunk_path.exists():
            print(f"  WARNING: Missing {chunk_path}")
            continue

        with open(chunk_path, "r", encoding="utf-8") as f:
            chunk_text = f.read().strip()

        all_rows.append({
            "id": "",
            "party": party,
            "chunk": chunk_text,

            "annotator_1_primary": "",
            "annotator_1_secondary": "",
            "annotator_2_primary": "",
            "annotator_2_secondary": "",
            "annotator_3_primary": "",
            "annotator_3_secondary": "",

            "annotators_primary_agreement": "",
            "annotators_secondary_agreement": "",

            "GEMINI model": "gemini-3.1-flash-lite",
            "GEMINI_primary": row["Primary_Category"],
            "GEMINI_secondary": row["Secondary_Category"],
        })

new_df = pd.DataFrame(all_rows, columns=COLUMNS)
new_df["id"] = range(1, len(new_df) + 1)

new_df.to_excel(EXCEL_FILE, index=False)

print("\n" + "=" * 70)
print("EXCEL BUILD COMPLETE")
print("=" * 70)
print(f"Total rows: {len(new_df)}")
print("\nRows by party:")
print(new_df["party"].value_counts())
print(f"\nSaved to: {EXCEL_FILE}")