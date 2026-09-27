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

# load_dotenv()

# genai.configure(api_key=os.getenv("gemini_api_key"))

# model = genai.GenerativeModel("gemini-3.1-flash-lite")


# # ============================================================
# # CATEGORIES
# # ============================================================

# CATEGORIES = [
#     "Agriculture and Farmers",
#     "Women’s Development",
#     "Education",
#     "Women Empowerment",
#     "Health",
#     "Governance",
#     "Infrastructure",
#     "Religion and Culture",
#     "Social justice and Deprived communities",
#     "Law and Order",
#     "Welfare and Funds",
#     "Divyang Welfare",
#     "Content about the Opposition party",
#     "Others"
# ]


# #  ============================================================

# # EXCEL_FILE = (
# #     "/Users/ctrl2/OneDrive/Documents/Annotation sheet.xlsx"
# # )

# # df=pd.read_excel(EXCEL_FILE)

# def classify_chunk(text):
#     prompt = f"""
# You are a political analyst for Tamil Nadu 2026 elections.

# Choose the **most dominant category** as the Main category and if there is a clear second important category, mention it as the econdary category.

# Categories:
# {chr(10).join([f"- {cat}" for cat in CATEGORIES])}

# Text:
# {text}

# Instructions:
# - If the text clearly contains a substantial second theme that could  be classified into a different category, also give that as the Secondary category.
# - Provide a Secondary category only when there is genuine ambiguity or a clearly important second theme.
# - Do NOT provide a Secondary category just because another category is mentioned briefly.
# - The Main and Secondary categories must be different.
# - Both categories MUST be exactly from the list above.
# - Do not invent, modify, or combine category names.
# - If there is no clear second category, write "Secondary: None".

# Format:
# Main: Category Name
# Secondary: Category Name

# Examples:

# Main: Agriculture and Farmers
# Secondary: Welfare and Funds
# """



#     try:
#         response = model.generate_content(prompt)

#         return response.text.strip()

#     except Exception as e:
#         print("Error:", e)
#         return "Main: None\nSecondary: None"


# def process_speech(party,speech_name, folder_path):

#     print("\n" + "=" * 60)
#     print(f"Processing: {speech_name}")
#     print(f"Folder: {folder_path}")
#     print("=" * 60)

#     # --------------------------------------------------------
#     # Get all chunk files
#     # --------------------------------------------------------

#     chunk_files = [
#         f for f in os.listdir(folder_path)
#         if f.endswith(".txt")
#     ]

#     chunk_files.sort(
#         key=lambda f: int(
#             f.replace("chunk_", "").replace(".txt", "")
#         )
#     )

#     print("\n" + "=" * 60)
    
#     print(f"Speech: {speech_name}")
#     print(f"Chunks: {len(chunk_files)}")
#     print("=" * 60)

     
#     detailed_results=[]
#     for i, chunk_file in enumerate(chunk_files, start=1):

#         print(
#             f"\nClassifying {chunk_file} "
#             f"({i}/{len(chunk_files)})..."
#         )

#         chunk_path = os.path.join(folder_path, chunk_file)

#         with open(chunk_path, "r", encoding="utf-8") as f:
#             text = f.read()

#         response = classify_chunk(text)
#         if response==None:
#             print(f"Skipping {chunk_file} because classification failed.")
#             continue
#         print("Response:", response)



#         # Wait between requests
#         time.sleep(8)

#         # ----------------------------------------------------
#         # Extract categories
#         # ----------------------------------------------------
        
#         main_cat = None
#         secondary_cat = None

#         for line in response.splitlines():
#             if line.startswith("Main:"):
#                 main_cat = line.replace("Main:", "").strip()

#             elif line.startswith("Secondary:"):
#                 secondary_cat = line.replace("Secondary:", "").strip()     

#         # Make sure returned category is valid
#         if main_cat not in CATEGORIES:
#             print(f"WARNING: Invalid category returned: {main_cat}")
#             main_cat = "Others"
#         if secondary_cat == "None":
#                 secondary_cat = None
#         elif secondary_cat not in CATEGORIES:
#             print( f"WARNING: Invalid category returned: {secondary_cat}"
#                         )
            

#         detailed_results.append({
#             # "Party": party,
#             # "Speech": speech_name,
#             "Chunk": chunk_file,
#             "Primary_Category": main_cat,
#             "Secondary_Category": secondary_cat
#         })

        

#         time.sleep(8)

#     os.makedirs("results", exist_ok=True)
        
#     output_base = Path("results") / speech_name

#     output_base.parent.mkdir(parents=True, exist_ok=True)

#     detailed_df = pd.DataFrame(detailed_results)
#     detailed_df.to_csv(f"{output_base}_detailed.csv", index=False, encoding="utf-8-sig")

# #SAVE RESULTS


# BASE_FOLDER = "/Users/ctrl2/Desktop/election_manifest_OELP/chunks/speeches"
   
# for party in ["TVK"]:

#     party_folder = os.path.join(BASE_FOLDER, party)

#     if not os.path.exists(party_folder):

#         print(
#             f"\nWARNING: Folder not found: "
#             f"{party_folder}"
#         )

#         continue


    

#     speech_folders = [folder for folder in os.listdir(party_folder)
#         if os.path.isdir( os.path.join(party_folder,folder))]

#     print(
#             f"\nFound {len(speech_folders)} speeches "
#             f"for {party}"
#         )

#     for speech_name in sorted(speech_folders):

#         speech_folder = os.path.join(
#             party_folder,
#             speech_name
#         )



#         process_speech(
#             party=party,
#             speech_name=speech_name,
#             folder_path=speech_folder
        # )    

import pandas as pd
from pathlib import Path

BASE_FOLDER = Path("/Users/ctrl2/Desktop/election_manifest_OELP/chunks/speeches")
RESULTS_FOLDER = Path("results")
EXCEL_FILE = "/Users/ctrl2/OneDrive/Documents/Annotation sheet.xlsx"

COLUMNS = [
    "id",
    "party",
    "speaker",
    "speech",
    "chunk",

    "annotator_1_primary",
    "annotator_1_secondary",
    "annotator_2_primary",
    "annotator_2_secondary",
    "annotator_3_primary",
    "annotator_3_secondary",

    "annotators_primary_agreement",
    "annotators_secondary_agreement",

    "GPT model",
    "GPT_primary",
    "GPT_secondary",

    "GEMINI model",
    "GEMINI_primary",
    "GEMINI_secondary",

    "LLAMA model",
    "LLAMA_primary",
    "LLAMA_secondary"
]

all_rows = []

for party in ["AIADMK", "DMK","TVK"]:

    party_folder = BASE_FOLDER / party

    print("\n" + "=" * 70)
    print(f"RECOVERING {party}")
    print("=" * 70)

    if not party_folder.exists():
        print(f"WARNING: {party_folder} does not exist")
        continue

    speech_folders = sorted(
        [folder for folder in party_folder.iterdir() if folder.is_dir()]
    )

    print(f"Found {len(speech_folders)} speech folders")

    for speech_folder in speech_folders:

        speech_name = speech_folder.name

        csv_file = RESULTS_FOLDER / f"{speech_name}_detailed.csv"

        if not csv_file.exists():
            print(f"NO CSV: {speech_name}")
            continue

        print(f"Recovering: {party} -> {speech_name}")

        detailed_df = pd.read_csv(csv_file)

        for _, row in detailed_df.iterrows():

            chunk_file = str(row["Chunk"])
            chunk_path = speech_folder / chunk_file

            if not chunk_path.exists():
                print(f"  WARNING: Missing {chunk_path}")
                continue

            # Read actual chunk text
            with open(chunk_path, "r", encoding="utf-8") as f:
                chunk_text = f.read().strip()

            all_rows.append({
                "id": "",
                "party": party,
                "speaker": "",
                "speech": speech_name,
                "chunk": chunk_text,

                "annotator_1_primary": "",
                "annotator_1_secondary": "",
                "annotator_2_primary": "",
                "annotator_2_secondary": "",
                "annotator_3_primary": "",
                "annotator_3_secondary": "",

                "annotators_primary_agreement": "",
                "annotators_secondary_agreement": "",

                "GPT model": "",
                "GPT_primary": "",
                "GPT_secondary": "",

                "GEMINI model": "gemini-3.1-flash-lite",
                "GEMINI_primary": row["Primary_Category"],
                "GEMINI_secondary": row["Secondary_Category"],

                "LLAMA model": "",
                "LLAMA_primary": "",
                "LLAMA_secondary": ""
            })


# Create dataframe
new_df = pd.DataFrame(all_rows, columns=COLUMNS)

# Give every row a unique ID
new_df["id"] = range(1, len(new_df) + 1)

# Save Excel
new_df.to_excel(EXCEL_FILE, index=False)

print("\n" + "=" * 70)
print("RECOVERY COMPLETE")
print("=" * 70)

print(f"Total rows: {len(new_df)}")
print("\nRows by party:")
print(new_df["party"].value_counts())

print("\nExcel saved to:")
print(EXCEL_FILE)
        


    # count = Counter(main_categories)

    # total = len(main_categories)

    # summary_data = []

    # for category in CATEGORIES:

    #     num = count.get(category, 0)

    #     if total > 0:
    #         percentage = round(
    #             (num / total) * 100,
    #             2
    #         )
    #     else:
    #         percentage = 0

    #     summary_data.append([
    #         category,
    #         num,
    #         percentage
    #     ])

    # summary_df = pd.DataFrame(
    #     summary_data,
    #     columns=[
    #         "Category",
    #         "Main_Count",
    #         "Secondary_Count"
    #         "Percentage (%)"
    #     ]
    # )

    # summary_df.to_csv(
    #     f"{output_base}_summary.csv",
    #     index=False,
    #     encoding="utf-8-sig"
    # )
    # print("\n" + "=" * 60)
    # print(f"Completed: {speech_name}")
    # print(f"Total chunks: {total}")
    # print("=" * 60)

    # print(summary_df)





