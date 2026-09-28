from dotenv import load_dotenv
import os
import pandas as pd
import time
from pathlib import Path
import google.generativeai as genai

# ============================================================
# LOAD API KEY
# ============================================================

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-3.1-flash-lite")

# ============================================================
# CATEGORIES (14)
# ============================================================

CATEGORIES = [
    "Agriculture and Farmers",
    "Employment and Jobs",
    "Women's Development",
    "Education",
    "Health",
    "Governance",
    "Infrastructure",
    "Religion and Culture",
    "Social justice and Deprived communities",
    "Law and order",
    "Welfare and Funds",
    "Divyang welfare",
    "Content about the Opposition party",
    "Others",
]

# ============================================================
# FOLDERS: one folder per manifesto, chunks directly inside
# Adjust paths below if your layout differs
# ============================================================

BASE_FOLDER = Path("chunks/manifestoes")
MANIFESTOS = {
    "MGB": BASE_FOLDER / "MGB_Manifesto_new",
    "NDA": BASE_FOLDER / "NDA_Manifesto_new",
}


def classify_chunk(text):
    prompt = f"""
You are a political analyst for Bihar 2025 elections.

Choose the **most dominant category** as the Main category and if there is a clear second important category, mention it as the Secondary category.

Categories:
{chr(10).join([f"- {cat}" for cat in CATEGORIES])}

Text:
{text}

Instructions:
- If the text clearly contains a substantial second theme that could be classified into a different category, also give that as the Secondary category.
- Provide a Secondary category only when there is genuine ambiguity or a clearly important second theme.
- Do NOT provide a Secondary category just because another category is mentioned briefly.
- The Main and Secondary categories must be different.
- Both categories MUST be exactly from the list above.
- Do not invent, modify, or combine category names.
- If there is no clear second category, write "Secondary: None".

Format:
Main: Category Name
Secondary: Category Name

Examples:

Main: Agriculture and Farmers
Secondary: Welfare and Funds
"""
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("Error:", e)
        return None


def process_manifesto(party, folder_path):
    print("\n" + "=" * 60)
    print(f"Processing manifesto: {party}")
    print(f"Folder: {folder_path}")
    print("=" * 60)

    if not os.path.exists(folder_path):
        print(f"WARNING: Folder not found: {folder_path}")
        return

    chunk_files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
    chunk_files.sort(key=lambda f: int(f.replace("chunk_", "").replace(".txt", "")))

    print(f"Chunks found: {len(chunk_files)}")

    detailed_results = []

    for i, chunk_file in enumerate(chunk_files, start=1):
        print(f"\nClassifying {chunk_file} ({i}/{len(chunk_files)})...")

        chunk_path = os.path.join(folder_path, chunk_file)
        with open(chunk_path, "r", encoding="utf-8") as f:
            text = f.read()

        response = classify_chunk(text)
        if response is None:
            print(f"Skipping {chunk_file} because classification failed.")
            continue
        print("Response:", response)

        time.sleep(8)

        main_cat, secondary_cat = None, None
        for line in response.splitlines():
            if line.startswith("Main:"):
                main_cat = line.replace("Main:", "").strip()
            elif line.startswith("Secondary:"):
                secondary_cat = line.replace("Secondary:", "").strip()

        if main_cat not in CATEGORIES:
            print(f"WARNING: Invalid category returned: {main_cat}")
            main_cat = "Others"
        if secondary_cat == "None":
            secondary_cat = None
        elif secondary_cat not in CATEGORIES:
            print(f"WARNING: Invalid category returned: {secondary_cat}")

        detailed_results.append({
            "Chunk": chunk_file,
            "Primary_Category": main_cat,
            "Secondary_Category": secondary_cat,
        })

    os.makedirs("results", exist_ok=True)
    output_base = Path("results") / f"Manifesto_{party}"
    detailed_df = pd.DataFrame(detailed_results)
    detailed_df.to_csv(f"{output_base}_detailed.csv", index=False, encoding="utf-8-sig")

    print(f"\nSaved: {output_base}_detailed.csv ({len(detailed_df)} chunks)")


def main():
    for party, folder_path in MANIFESTOS.items():
        process_manifesto(party, folder_path)


if __name__ == "__main__":
    main()