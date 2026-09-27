import json
import os
from pathlib import Path

from youtube_transcript_api import YouTubeTranscriptApi


JSON_FILE = "cleaned_videos_metadata.json"
OUTPUT_FOLDER = "transcripts"


# Create transcripts folder
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# --------------------------------------------------
# Read JSON file
# --------------------------------------------------

def get_transcribed_ids(output_folder):
    """
    Scan all transcript folders and collect video IDs that
    have already been transcribed.
    """

    transcribed_ids = set()

    output_path = Path(output_folder)

    if not output_path.exists():
        return transcribed_ids

    for txt_file in output_path.rglob("*.txt"):

        # Video ID is the last part before .txt
        # Example:
        # NDA_amit_shah_nalanda_UwjUPWLqtr8.txt
        # -> UwjUPWLqtr8

        video_id = txt_file.stem.split("_")[-1]

        if video_id:
            transcribed_ids.add(video_id)

    return transcribed_ids

with open(JSON_FILE, "r", encoding="utf-8") as file:
    videos = json.load(file)


# Create YouTube API object
ytt_api = YouTubeTranscriptApi()
transcribed_ids = get_transcribed_ids(OUTPUT_FOLDER)

for number, video in enumerate(videos, start=1):

    print()
    print("=" * 60)
    print("Processing video", number)

    # Get information directly from JSON
    video_id = video["id"]
    if video_id in transcribed_ids:
        print(
            f"[SKIP] Already transcribed: "
            f"{video['title']}"
        )
        continue
    url = video["url"]
    speaker = video["speaker"]
    place = video["place"]
    party = video["party"]

    print("URL:", url)
    print("Video ID:", video_id)
    print("Speaker:", speaker)
    print("Place:", place)
    print("Party:", party)

    try:


        transcript_list = ytt_api.list(video_id)

        print("\nAvailable transcripts:")

        for transcript in transcript_list:
            print(
                "Language:",
                transcript.language,
                "| Code:",
                transcript.language_code,
                "| Generated:",
                transcript.is_generated
            )

        try:

            transcript = transcript_list.find_transcript(["hi"])

            print("Hindi transcript found.")

        except Exception:

            print("Hindi transcript not found.")

            # Try automatically generated Tamil
            try:

                transcript = transcript_list.find_generated_transcript(["hi"])

                print("Automatically generated Hindi transcript found.")

            except Exception:

                print("No Hindi transcript available.")
                continue

        # --------------------------------------------
        # Fetch transcript
        # --------------------------------------------

        fetched_transcript = transcript.fetch()

        # --------------------------------------------
        # Convert transcript to text
        # --------------------------------------------

        full_text = ""

        for snippet in fetched_transcript:
            full_text += snippet.text + " "

        full_text = full_text.strip()

        # --------------------------------------------
        # Create filename
        # --------------------------------------------

        filename = (f"{party}_{speaker}_{place}_{video_id}.txt")

        if party == "NDA":
            output_folder = os.path.join(OUTPUT_FOLDER, "NDA")

        elif party == "Mahagathbandhan":
            output_folder = os.path.join(OUTPUT_FOLDER, "Mahagathbandhan")

        else:
            output_folder = os.path.join(OUTPUT_FOLDER, "None")

        os.makedirs(output_folder, exist_ok=True)

        output_path = os.path.join(output_folder, filename)


        # --------------------------------------------
        # Save transcript
        # --------------------------------------------

        with open(output_path, "w", encoding="utf-8") as file:
            file.write(full_text)

        print()
        print("SUCCESS!")
        print("Transcript saved to:")
        print(output_path)

    except Exception as error:

        print()
        print("ERROR processing this video:")
        print(error)


print()
print("=" * 60)
print("Finished processing all videos.")