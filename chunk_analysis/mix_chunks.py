
import pandas as pd
import random
import re
import unicodedata
from pathlib import Path

BASE = Path.cwd()

# If running from inside oelp_hindi, don't add oelp_hindi again
if (BASE / "oelp_hindi" / "chunks").exists():
    BASE = BASE / "oelp_hindi"

SPEECH_COUNT= 150
MANIFESTO_COUNT=5
OUTPUT_EXCEL = BASE / "annotation_sheet_mixed_hindi.xlsx"

folders = {
    "MGB_Manifesto": BASE / "chunks/manifestoes/MGB_manifesto_new",
    "NDA_Manifesto": BASE / "chunks/manifestoes/NDA_manifesto_new",
    "MGB_Speech": BASE / "chunks/speeches/Mahagathbandhan",
    "NDA_Speech": BASE / "chunks/speeches/NDA"
}

random.seed(42)


# ============================================================
# NORMALIZE TEXT FOR DUPLICATE CHECKING
# ============================================================

def normalize(text):
    words = text.casefold().split()

    # Remove punctuation but preserve Hindi characters/matras
    words = [
        "".join(
            ch for ch in word
            if not unicodedata.category(ch).startswith(("P", "S"))
        )
        for word in words
    ]

    return [word for word in words if word]


# ============================================================
# CHECK WHETHER 6 CONSECUTIVE WORDS MATCH
# ============================================================

def get_sequences(text):
    words = normalize(text)

    return {
        tuple(words[i:i+6])
        for i in range(len(words) - 5)
    }


# ============================================================
# RANDOM SAMPLING - DUPLICATE CHECK WITHIN SAME FOLDER ONLY
# ============================================================

selected = []

for group, folder in folders.items():

    if "Manifesto" in group:
        chunk_files = list(folder.glob("chunk_*.txt"))
    else:
        chunk_files = list(folder.rglob("chunk_*.txt"))

    random.shuffle(chunk_files)

    count = 0

    # Store sequences separately for each speech/manifesto folder
    seen_by_folder = {}

    for chunk_file in chunk_files:
        if "Manifesto" in group:
            if count == MANIFESTO_COUNT:
                break
        else:
            if count==SPEECH_COUNT:
                break

        text = chunk_file.read_text(encoding="utf-8").strip()

        if not text:
            continue

        # Identify the folder containing this chunk
        folder_key = chunk_file.parent

        if folder_key not in seen_by_folder:
            seen_by_folder[folder_key] = set()

        sequences = get_sequences(text)

        # Compare only against previously selected chunks
        # from the SAME folder
        # Duplicate checking ONLY for speech chunks
        if "Speech" in group:
            if sequences & seen_by_folder[folder_key]:
                print(f"[DUPLICATE] Skipped: {chunk_file}")
                continue

        selected.append({
            "Group": group,
            "Speech_Name": (
                chunk_file.parent.name
                if "Speech" in group else "Manifesto"
            ),
            "Chunk": chunk_file.name,
            "chunk_text": text,
            "Primary_Category": "",
            "Secondary_Category": ""
        })

        if "Speech" in group:
            seen_by_folder[folder_key].update(sequences)
        count += 1

    # print(f"{group}: Selected {count}/{N_PER_GROUP} chunks")


# ============================================================
# MIX AND SAVE TO EXCEL
# ============================================================

random.shuffle(selected)

df = pd.DataFrame(selected)
df.to_excel(OUTPUT_EXCEL, index=False)

print("\nTotal selected chunks:", len(df))
print("Saved to:", OUTPUT_EXCEL)

