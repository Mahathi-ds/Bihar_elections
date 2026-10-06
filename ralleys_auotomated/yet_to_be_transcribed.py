import json
from pathlib import Path


# -----------------------------
# Paths
# -----------------------------
MGB_METADATA = Path("cleaned_videos_metadata_mgb.json")
NDA_METADATA = Path("cleaned_videos_metadata_nda.json")

MGB_TRANSCRIPTS = Path("transcripts/Mahagathbandhan")
NDA_TRANSCRIPTS = Path("transcripts/NDA")

MGB_OUTPUT = Path("videos_to_be_transcribed_mgb.json")
NDA_OUTPUT = Path("videos_to_be_transcribed_nda.json")


# -----------------------------
# Load JSON
# -----------------------------
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# -----------------------------
# Get already-transcribed IDs
# -----------------------------
def get_transcribed_ids(transcript_folder, videos):

    transcript_files = list(transcript_folder.glob("*.txt"))

    print("Number of transcript files:", len(transcript_files))

    transcribed_ids = set()

    metadata_ids = {
        video.get("id")
        for video in videos
        if video.get("id")
    }

    for txt_file in transcript_files:

        filename = txt_file.stem

        matches = [
            video_id
            for video_id in metadata_ids
            if filename.endswith("_" + video_id)
        ]

        if matches:
            video_id = matches[0]
            transcribed_ids.add(video_id)
            print("MATCH:")
            print("  file :", filename)
            print("  id   :", repr(video_id))

        else:
            print("NO MATCH:")
            print("  file :", filename)

    return transcribed_ids






        # for video in videos:
        #     video_id = video.get("id")

        #     if video_id and filename.endswith("_" + video_id):
        #         transcribed_ids.add(video_id)
        #         break



# -----------------------------
# Process one dataset
# -----------------------------
def create_to_be_transcribed(metadata_file, transcript_folder, output_file, name):

    videos = load_json(metadata_file)

    print(f"\n{name}")
    print("-" * 40)
    print("Total metadata videos:", len(videos))

    transcribed_ids = get_transcribed_ids(
        transcript_folder,
        videos
    )
    print(transcribed_ids)

    print("Already transcribed:", len(transcribed_ids))

    videos_to_transcribe = [
        video
        for video in videos
        if video.get("id") not in transcribed_ids
    ]

    print("Still to transcribe:", len(videos_to_transcribe))

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(videos_to_transcribe, f, ensure_ascii=False, indent=2)

    print("Saved:", output_file)


# -----------------------------
# Run both
# -----------------------------
# create_to_be_transcribed(
#     MGB_METADATA,
#     MGB_TRANSCRIPTS,
#     MGB_OUTPUT,
#     "Mahagathbandhan"
# )

create_to_be_transcribed(
    NDA_METADATA,
    NDA_TRANSCRIPTS,
    NDA_OUTPUT,
    "NDA"
)

import json

files = [
    # "videos_to_be_transcribed_mgb.json",
    "videos_to_be_transcribed_nda.json"
]

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"{file}: {len(data)} videos")
