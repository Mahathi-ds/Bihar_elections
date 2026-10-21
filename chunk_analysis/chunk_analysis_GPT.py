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
    "Already executed promises",
    "Others"
]


# #  ============================================================

# # EXCEL_FILE = (
# #     "/Users/ctrl2/OneDrive/Documents/Annotation sheet.xlsx"
# # )

# # df=pd.read_excel(EXCEL_FILE)

def classify_chunk(text):
    prompt = f"""
    You are a political analyst for Tamil Nadu 2026 elections.

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
    Secondary: Education

    """



    try:
        response=client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                    ]
            )
        return response.choices[0].message.content

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
        
        main_cat = None
        secondary_cat = None

        for line in response.splitlines():
            if line.startswith("Main:"):
                main_cat = line.replace("Main:", "").strip()

            elif line.startswith("Secondary:"):
                secondary_cat = line.replace("Secondary:", "").strip()     

        # Make sure returned category is valid
        if main_cat not in CATEGORIES:
            print(f"WARNING: Invalid category returned: {main_cat}")
            main_cat = "Others"
        if secondary_cat == "None":
                secondary_cat = None
        elif secondary_cat not in CATEGORIES:
            print( f"WARNING: Invalid category returned: {secondary_cat}"
                        )
            

        detailed_results.append({
            # "Party": party,
            # "Speech": speech_name,
            "Chunk": chunk_file,
            "Primary_Category": main_cat,
            "Secondary_Category": secondary_cat
        })

        

        time.sleep(8)

    os.makedirs("results", exist_ok=True)
        
    output_base = Path("results") / "gpt"/speech_name

    output_base.parent.mkdir(parents=True, exist_ok=True)

    detailed_df = pd.DataFrame(detailed_results)
    detailed_df.to_csv(f"{output_base}_detailed.csv", index=False, encoding="utf-8-sig")



BASE_FOLDER = "/Users/ctrl2/Desktop/election_manifest_OELP/chunks/speeches"
   
for party in ["TVK"]:

    party_folder = os.path.join(BASE_FOLDER, party)

    if not os.path.exists(party_folder):

        print(
            f"\nWARNING: Folder not found: "
            f"{party_folder}"
        )

        continue


    

    speech_folders = [folder for folder in os.listdir(party_folder)
        if os.path.isdir( os.path.join(party_folder,folder))]

    print(
            f"\nFound {len(speech_folders)} speeches "
            f"for {party}"
        )

    for speech_name in sorted(speech_folders):

        speech_folder = os.path.join(
            party_folder,
            speech_name
        )



        process_speech(
            party=party,
            speech_name=speech_name,
            folder_path=speech_folder
        )    




   
    # --------------------------------------------------------
    # Create summary CSV
    # --------------------------------------------------------

    # Count the primary category assigned to each chunk
    main_categories = [
        result["Primary_Category"]
        for result in detailed_results
        if result["Primary_Category"] in CATEGORIES
    ]

    count = Counter(main_categories)
    total = len(main_categories)

    summary_data = []

    for category in CATEGORIES:
        num = count.get(category, 0)

        if total > 0:
            percentage = round((num / total) * 100, 2)
        else:
            percentage = 0

        summary_data.append({
            "Category": category,
            "Main_Count": num,
            "Percentage (%)": percentage
        })

    summary_df = pd.DataFrame(summary_data)

    summary_path = Path("results") / "gpt" / f"{speech_name}_summary.csv"
    summary_path.parent.mkdir(parents=True, exist_ok=True)

    summary_df.to_csv(
        summary_path,
        index=False,
        encoding="utf-8-sig"
    )

    print("\n" + "=" * 60)
    print(f"Completed: {speech_name}")
    print(f"Total successfully classified chunks: {total}")
    print("=" * 60)

    print(summary_df)
    print(f"\nSummary saved to: {summary_path}")





