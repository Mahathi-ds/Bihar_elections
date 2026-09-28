import os
import re
import json
import time
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from groq import Groq


# ============================================================
# 1. CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results" / "qwen_manifesto_results"

RESULTS_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "qwen/qwen3.8-27b")

if not API_KEY:
    raise ValueError(
        "GROQ_API_KEY was not found.\n"
        f"Create a .env file at: {BASE_DIR}"
    )

client = Groq(api_key=API_KEY)


# ============================================================
# 2. INPUT FOLDERS -- one folder per manifesto, chunk_N.txt inside
# ============================================================

CHUNK_FOLDERS = {
    "MGB": BASE_DIR / "chunks" / "manifestoes" / "MGB_Manifesto_new",
    "NDA": BASE_DIR / "chunks" / "manifestoes" / "NDA_Manifesto_new",
}


# ============================================================
# 3. BIHAR CATEGORIES (14)
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

UNCLASSIFIED = "Unclassified / Error"
MAX_ATTEMPTS = 3


# ============================================================
# 4. CATEGORY VALIDATION
# ============================================================

def normalize_label(value):
    """Normalize a category label for matching."""
    value = str(value or "").strip().lower()
    value = re.sub(r"^\s*\d+\s*[\.\):\-]?\s*", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


CATEGORY_LOOKUP = {
    normalize_label(category): category
    for category in CATEGORIES
}


def validate_category(value, allow_empty=False):
    """Return the exact official category label or None."""
    if value is None or not str(value).strip():
        return "" if allow_empty else None
    return CATEGORY_LOOKUP.get(normalize_label(value))


# ============================================================
# 5. READ CHUNK FILES
# ============================================================

def load_chunks():
    all_chunks = []

    for party, folder_path in CHUNK_FOLDERS.items():
        if not folder_path.exists():
            raise FileNotFoundError(f"Missing folder: {folder_path}")

        chunk_files = [f for f in os.listdir(folder_path) if f.endswith(".txt")]
        chunk_files.sort(key=lambda f: int(f.replace("chunk_", "").replace(".txt", "")))

        for chunk_file in chunk_files:
            chunk_path = folder_path / chunk_file
            with open(chunk_path, "r", encoding="utf-8") as f:
                text = f.read().strip()

            if text:
                all_chunks.append({
                    "party": party,
                    "chunk_id": chunk_file,
                    "text": text,
                })
            else:
                print(f"WARNING: Empty chunk skipped: {party} / {chunk_file}")

    return all_chunks


# ============================================================
# 6. PARSE THE MODEL RESPONSE
# ============================================================

def parse_json_response(content):
    """Extract JSON even if the model surrounds it with text."""
    content = content.strip()
    content = re.sub(r"^\s*```(?:json)?\s*", "", content, flags=re.IGNORECASE)
    content = re.sub(r"\s*```\s*$", "", content)

    start = content.find("{")
    end = content.rfind("}")

    if start == -1 or end == -1 or end < start:
        raise ValueError(f"No JSON object found in response: {content[:300]}")

    return json.loads(content[start:end + 1])


# ============================================================
# 7. CLASSIFY ONE CHUNK
# ============================================================

def classify_chunk(chunk):
    text = chunk["text"]

    prompt = f"""
You are analysing a political party's election manifesto
for the Bihar 2025 elections, for an academic text-classification project.

Classify the following manifesto text into ONE dominant
category from the exact list below.

CATEGORIES:
{json.dumps(CATEGORIES, ensure_ascii=False)}

RULES:
1. Choose exactly one main_category from the list.
2. Return the category label exactly as written in the list.
3. Use "Others" only when the text genuinely does not
   fit any of the other thirteen categories.
4. Do not use "Others" just because the text is difficult
   to understand.
5. If the text is genuinely too corrupted or incomplete
   to classify, set main_category to null and explain why.
6. A mention of an opposition party is not automatically
   "Content about the Opposition party". Use that category only when
   the content is specifically about the opposition party.
7. Classify based on the text provided, not your opinion
   about any party.
8. Do not invent promises or facts.
9. Return valid JSON only. Do not include Markdown fences.

JSON format:
{{
  "main_category": "exact category label or null",
  "secondary_category": "exact category label or null",
  "reason": "brief explanation in English"
}}

MANIFESTO TEXT:
{text}
"""

    last_error = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a careful academic text "
                            "classifier. Follow the category "
                            "definitions exactly. Return JSON only."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.1,
                max_tokens=400,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("The model returned an empty response.")

            data = parse_json_response(content)

            main_category = validate_category(data.get("main_category"))
            if main_category is None:
                raise ValueError(
                    f"Missing or invalid main_category: {data.get('main_category')!r}"
                )

            secondary_category = validate_category(
                data.get("secondary_category"), allow_empty=True
            )
            if secondary_category == main_category:
                secondary_category = ""

            return {
                "main_category": main_category,
                "secondary_category": secondary_category or "",
                "reason": str(data.get("reason", "")).strip(),
                "classification_status": "success",
                "error_message": "",
            }

        except Exception as exc:
            last_error = exc
            print(f"  Attempt {attempt}/{MAX_ATTEMPTS} failed: {type(exc).__name__}: {exc}")
            if attempt < MAX_ATTEMPTS:
                time.sleep(2 * attempt)

    return {
        "main_category": "",
        "secondary_category": "",
        "reason": "",
        "classification_status": "error",
        "error_message": str(last_error)[:1000],
    }


# ============================================================
# 8. CHECKPOINT AND RESUME
# ============================================================

DETAIL_PATH = RESULTS_DIR / "qwen_classified_chunks.csv"


def save_checkpoint(results_by_key):
    if not results_by_key:
        return
    df = pd.DataFrame(list(results_by_key.values()))
    df.to_csv(DETAIL_PATH, index=False, encoding="utf-8-sig")


def load_previous_successes():
    previous = {}
    if not DETAIL_PATH.exists():
        return previous

    try:
        df = pd.read_csv(DETAIL_PATH, encoding="utf-8-sig", keep_default_na=False)
        required = {"party", "chunk_id", "main_category", "classification_status"}

        if not required.issubset(df.columns):
            print("Old checkpoint has an unexpected format; starting fresh.")
            return {}

        for _, row in df.iterrows():
            if row["classification_status"] != "success":
                continue
            category = validate_category(row["main_category"])
            if category is None:
                continue
            key = (str(row["party"]), str(row["chunk_id"]))
            previous[key] = row.to_dict()

    except Exception as exc:
        print(f"Could not read previous checkpoint: {exc}")
        return {}

    return previous


# ============================================================
# 9. CLASSIFY ALL CHUNKS
# ============================================================

def run_classification():
    chunks = load_chunks()

    print("=" * 60)
    print("QWEN BIHAR MANIFESTO CLASSIFICATION")
    print("=" * 60)
    print(f"Model: {MODEL}")
    print(f"Chunks loaded: {len(chunks)}")

    results_by_key = load_previous_successes()
    print(f"Successful chunks loaded from checkpoint: {len(results_by_key)}")

    for index, chunk in enumerate(chunks, start=1):
        key = (chunk["party"], chunk["chunk_id"])
        if key in results_by_key:
            continue

        print(f"[{index}/{len(chunks)}] {chunk['party']} - {chunk['chunk_id']}")

        classification = classify_chunk(chunk)
        result = {**chunk, **classification}
        results_by_key[key] = result
        save_checkpoint(results_by_key)

        if classification["classification_status"] == "success":
            print(f"  Category: {classification['main_category']}")
        else:
            print("  Classification failed; saved for retry.")

    ordered_results = [
        results_by_key[(chunk["party"], chunk["chunk_id"])]
        for chunk in chunks
        if (chunk["party"], chunk["chunk_id"]) in results_by_key
    ]

    results_df = pd.DataFrame(ordered_results)
    results_df.to_csv(DETAIL_PATH, index=False, encoding="utf-8-sig")

    create_summaries(results_df)

    print("\n" + "=" * 60)
    print("CLASSIFICATION FINISHED")
    print("=" * 60)
    print(f"Input chunks: {len(chunks)}")
    print(f"Result rows: {len(results_df)}")
    print(f"Successful: {(results_df['classification_status'] == 'success').sum()}")
    print(f"Errors: {(results_df['classification_status'] != 'success').sum()}")
    print(f"Detailed results: {DETAIL_PATH}")
    print(f"Summary workbook: {RESULTS_DIR / 'qwen_summary.xlsx'}")


# ============================================================
# 10. CREATE SUMMARY TABLES
# ============================================================

def create_summaries(results_df):
    summary_rows = []
    overview_rows = []

    for party in CHUNK_FOLDERS:
        party_df = results_df[results_df["party"] == party]
        total_chunks = len(party_df)
        successful_df = party_df[party_df["classification_status"] == "success"]
        successful_chunks = len(successful_df)
        error_count = int((party_df["classification_status"] != "success").sum())

        overview_rows.append({
            "party": party,
            "total_chunks": total_chunks,
            "successful_chunks": successful_chunks,
            "unclassified_count": error_count,
            "success_percentage": (
                round(successful_chunks / total_chunks * 100, 2) if total_chunks else 0
            ),
        })

        category_counts = successful_df["main_category"].value_counts().to_dict()

        for category in CATEGORIES:
            count = int(category_counts.get(category, 0))
            summary_rows.append({
                "party": party,
                "category": category,
                "chunk_count": count,
                "percentage": round(count / total_chunks * 100, 2) if total_chunks else 0,
            })

        summary_rows.append({
            "party": party,
            "category": UNCLASSIFIED,
            "chunk_count": error_count,
            "percentage": round(error_count / total_chunks * 100, 2) if total_chunks else 0,
        })

    category_summary = pd.DataFrame(summary_rows)
    party_overview = pd.DataFrame(overview_rows)

    category_summary.to_csv(RESULTS_DIR / "qwen_category_summary.csv", index=False, encoding="utf-8-sig")
    party_overview.to_csv(RESULTS_DIR / "qwen_party_overview.csv", index=False, encoding="utf-8-sig")

    workbook_path = RESULTS_DIR / "qwen_summary.xlsx"
    with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
        category_summary.to_excel(writer, sheet_name="Category Summary", index=False)
        party_overview.to_excel(writer, sheet_name="Party Overview", index=False)
        results_df.to_excel(writer, sheet_name="Detailed Results", index=False)

    print("\nParty overview:")
    print(party_overview.to_string(index=False))


# ============================================================
# 11. MAIN
# ============================================================

if __name__ == "__main__":
    run_classification()