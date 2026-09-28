from dotenv import load_dotenv
import os
import pandas as pd
from collections import Counter
import time
from pathlib import Path
# import google.generativeai as genai
from openai import OpenAI



# # ============================================================
# # LOAD API KEY
# # ============================================================

load_dotenv()

client = OpenAI(
    api_key=os.getenv('GROQ_API_KEY'),
    base_url="https://api.groq.com/openai/v1"
    # base_url = "https://integrate.api.nvidia.com/v1",
)


# # ============================================================
# # CATEGORIES
# # ============================================================

CATEGORIES = [
    "Agriculture and Farmers",
    "Women’s Development",
    "Education",
    "Women Empowerment",
    "Health",
    "Governance",
    "Infrastructure",
    "Religion and Culture",
    "Social justice and Deprived communities",
    "Law and Order",
    "Welfare and Funds",
    "Divyang Welfare",
    "Content about the Opposition party",
    "Others"
]


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
#         response=client.chat.completions.create(
#             model="openai/gpt-oss-20b",
#             messages=[
#                     {
#                         "role": "user",
#                         "content": prompt
#                     }
#                     ]
#             )
#         return response.choices[0].message.content

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
        
#     output_base = Path("results") / "gpt"/speech_name

#     output_base.parent.mkdir(parents=True, exist_ok=True)

#     detailed_df = pd.DataFrame(detailed_results)
#     detailed_df.to_csv(f"{output_base}_detailed.csv", index=False, encoding="utf-8-sig")



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
#         )    

import pandas as pd
from pathlib import Path


BASE_FOLDER = Path("/Users/ctrl2/Desktop/election_manifest_OELP/chunks/speeches")
RESULTS_FOLDER =  r"/Users/ctrl2/Desktop/election_manifest_OELP/results/gpt"
EXCEL_FILE = r"/Users/ctrl2/OneDrive/Documents/Annotation sheet.xlsx"
df=pd.read_excel(EXCEL_FILE) 

df["GPT model"] = df["GPT model"].astype("object")
df["GPT_primary"] = df["GPT_primary"].astype("object")
df["GPT_secondary"] = df["GPT_secondary"].astype("object")
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
for party in ["AIADMK", "DMK","TVK"]:

    party_folder = BASE_FOLDER / party

    if not party_folder.exists():
        
        continue

    speech_folders = sorted([folder for folder in party_folder.iterdir() if folder.is_dir()])

    for speech_folder in speech_folders:

        speech_name = speech_folder.name

        csv_file = Path(RESULTS_FOLDER) / f"{speech_name}_detailed.csv"

        if not csv_file.exists():
            print(f"NO CSV: {speech_name}")
            continue

        

        
        detailed_df = pd.read_csv(csv_file, encoding="utf-8-sig")
        

        for _, row in detailed_df.iterrows():

            chunk_file = str(row["Chunk"]).strip()
            chunk_path = speech_folder / chunk_file

            if not chunk_path.exists():
                print(f"  WARNING: Missing {chunk_path}")
                continue

            # Read actual chunk text
            with open(chunk_path, "r", encoding="utf-8") as f:
                chunk_text = f.read().strip()
      
            primary = row["Primary_Category"]
            secondary = row["Secondary_Category"]
            mask=((df["party"].astype(str).str.strip() == party) & 
            (df["speech"].astype(str).str.strip() == speech_name) & 
            (df["chunk"].astype(str).str.strip() == chunk_text))


            df.loc[mask, "GPT model"] = "openai/gpt-oss-20b"
            df.loc[mask, "GPT_primary"] = primary
            df.loc[mask, "GPT_secondary"] = secondary

         

df.to_excel(EXCEL_FILE, index=False)

print("\n" + "=" * 70)
print("GPT RESULTS ADDED TO ANNOTATION SHEET")
print("=" * 70)


print("Total Excel rows:", len(df))
print("Excel saved to:")
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





