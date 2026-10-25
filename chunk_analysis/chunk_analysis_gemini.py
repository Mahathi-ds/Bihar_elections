from dotenv import load_dotenv
import os
import pandas as pd
from collections import Counter
import time
from pathlib import Path
import google.generativeai as genai


# # ============================================================
# # LOAD API KEY
# # ============================================================

load_dotenv()

genai.configure(api_key=os.getenv("gemini_key_1424"))

model = genai.GenerativeModel("gemini-3.1-flash-lite")


# ============================================================
# CATEGORIES
# ============================================================

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


#  ============================================================

# EXCEL_FILE = (
#     "/Users/ctrl2/OneDrive/Documents/Annotation sheet.xlsx"
# )

# df=pd.read_excel(EXCEL_FILE)

def classify_chunk(text):
    prompt = f"""
    You are a political analyst for Bihar 2025 elections.

    Choose the *most dominant category* as the Main category and if there is a clear second important category, mention it as the Secondary category.
    
    
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
    
    

    About the category "Already executed promises":
    - Use it ONLY when the speaker claims that a specific promise, scheme, project or commitment made by their party or government has actually been delivered or completed (for example: "we promised free bus travel for women and we have implemented it", "the hospital we announced has been built and opened").
    - When a chunk does describe such a delivered promise, choose "Already executed promises" as the Main category and None as the secondary category
    - Past tense alone does NOT make a chunk "Already executed promises". Classify by its topic instead in these cases:
    - recounting history, past events, or past leaders' lives without claiming a delivered promise
    - criticising the opposition's past actions or failures (use "Content about the Opposition party")
    - personal stories, anecdotes, or descriptions of past rallies or meetings
    - a past promise that the speaker says was NOT fulfilled or was broken
    - vague boasts with no identifiable promise, scheme, or work (e.g. "we did a lot of good work")
    - future promises or plans, even if worded with "will have done"

    Format:
    Main: Category Name
    Secondary: Category Name


    Examples:

    Main: Agriculture and Farmers
    Secondary: Welfare and Funds

    Main: Already executed promises
    Secondary: None

    """


    try:
        response = model.generate_content(prompt)

        return response.text.strip()

    except Exception as e:
        print("Error:", e)
        return "Main: None\nSecondary: None"


def process_speech(party,speech_name, folder_path):

    

    print("\n" + "=" * 60)
    print(f"Processing: {speech_name}")
    print(f"Folder: {folder_path}")
    print("=" * 60)

    # --------------------------------------------------------
    # Get all chunk files
    # --------------------------------------------------------

    chunk_files = [
        f for f in os.listdir(folder_path)
        if f.endswith(".txt")
    ]

    chunk_files.sort(
        key=lambda f: int(
            f.replace("chunk_", "").replace(".txt", "")
        )
    )

    print("\n" + "=" * 60)
    
    print(f"Speech: {speech_name}")
    print(f"Chunks: {len(chunk_files)}")
    print("=" * 60)

     
    detailed_results=[]
    for i, chunk_file in enumerate(chunk_files, start=1):

        print(
            f"\nClassifying {chunk_file} "
            f"({i}/{len(chunk_files)})..."
        )

        chunk_path = os.path.join(folder_path, chunk_file)

        with open(chunk_path, "r", encoding="utf-8") as f:
            text = f.read()

        response = classify_chunk(text)
        if response==None:
            print(f"Skipping {chunk_file} because classification failed.")
            continue
        print("Response:", response)



        # Wait between requests
        time.sleep(8)

        # ----------------------------------------------------
        # Extract categories
        # ----------------------------------------------------
        
        # ----------------------------------------------------
# Extract categories and reasons
# ----------------------------------------------------

        main_cat = None
        secondary_cat = None

        for line in response.splitlines():
            line = line.strip()

            if line.startswith("Main:"):
                main_cat = line.replace("Main:", "", 1).strip()

            # elif line.startswith("Main reason:"):
            #     main_reason = line.replace("Main reason:", "", 1).strip()

            elif line.startswith("Secondary:"):
                secondary_cat = line.replace("Secondary:", "", 1).strip()

            # elif line.startswith("Secondary reason:"):
            #     secondary_reason = line.replace("Secondary reason:", "", 1).strip()


            # Validate categories
            if main_cat not in CATEGORIES:
                print(f"WARNING: Invalid category returned: {main_cat}")
                main_cat = "Others"

            if secondary_cat == "None":
                secondary_cat = None

          
                                
                    

            detailed_results.append({
            "Chunk": chunk_file,
            "Primary_Category": main_cat,
            # "Primary_Reason": main_reason,
            "Secondary_Category": secondary_cat,
            # "Secondary_Reason": secondary_reason
        })

            

            time.sleep(8)

    os.makedirs("results", exist_ok=True)
        
    output_base = Path("results/rally_results/mahagathbandhan/gemini") / speech_name

    output_base.parent.mkdir(parents=True, exist_ok=True)

    detailed_df = pd.DataFrame(detailed_results)
    detailed_df.to_csv(f"{output_base}_detailed.csv", index=False, encoding="utf-8-sig")
    return detailed_results

#SAVE RESULTS



# SAVE RESULTS

BASE_FOLDER = "/Users/ctrl2/Desktop/oelp_hindi/chunks/speeches"

for party in ["Mahagathbandhan"]:

    party_folder = os.path.join(BASE_FOLDER, party)

    if not os.path.exists(party_folder):
        print(f"\nWARNING: Folder not found: {party_folder}")
        continue

    speech_folders = [
        folder for folder in os.listdir(party_folder)
        if os.path.isdir(os.path.join(party_folder, folder))
    ]

    print(f"\nFound {len(speech_folders)} speeches for {party}")

    for speech_name in sorted(speech_folders):
        detailed_csv = (
        Path("results") / "rally_results" /"mahagathbandhan"/"gemini"/
        f"{speech_name}_detailed.csv"
        )

        # Skip speech if it has already been classified
        if detailed_csv.exists():
            print(f"[SKIP] Already classified: {speech_name}")
            continue 

        speech_folder = os.path.join(party_folder, speech_name)

        detailed_results = process_speech(
            party=party,
            speech_name=speech_name,
            folder_path=speech_folder
        )

       
# ============================================================


    


    



   





