import yt_dlp
import os
import json

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "raw_audios"
def load_cleaned_videos(auto_path="final_videos.json", manual_path="final_videos_manual.json"):
    """Load and combine both output files. Missing files are treated as
    empty (e.g. if you've only run one of the two pipelines so far)."""
    videos = []
    for path in (auto_path, manual_path):
        if not os.path.exists(path):
            print(f"  [warn] {path} not found, skipping")
            continue
        with open(path, "r", encoding="utf-8") as f:
            videos.extend(json.load(f))

    # De-dupe by video id in case the same video ended up in both files.
    unique = {}
    for v in videos:
        unique[v["id"]] = v
    return list(unique.values())


def safe_name(video):
    speaker = (video.get("speaker") or "unknown").replace(" ", "")
    place = (video.get("place") or "unknown").replace(" ", "")
    # video id appended so two different videos sharing the same
    # speaker+place (e.g. same leader visiting the same city twice) never
    # collide on filename and silently overwrite / get skipped.
    return f"{speaker}_{place}_{video['id']}"


def download_video(videos):
    failed = []
    for v in videos:
        party = v.get("party") or "Unclassified"

        out_dir = DATA_DIR / party
        os.makedirs(out_dir, exist_ok=True)

        wav_path = out_dir / f"{safe_name(v)}.wav"

        if wav_path.exists():
            print(f"Skipping {safe_name(v)} — already downloaded.")
            continue

        output_path = str(out_dir / f"{safe_name(v)}.%(ext)s")

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'quiet': False,
            "retries": 10,
            "fragment_retries": 10,
            "sleep_interval": 2,
            "max_sleep_interval": 5,
        }

        print(f"\nDownloading [{party}] {safe_name(v)} from {v['url']} ...")
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([v["url"]])
            print(f"{safe_name(v)} downloaded successfully.")
        except Exception as e:
            print(f"FAILED: {safe_name(v)} — {e}")
            failed.append(v["url"])

    if failed:
        print(f"\n{len(failed)} video(s) failed to download:")
        for url in failed:
            print(f"  {url}")


if __name__ == "__main__":
    videos = load_cleaned_videos()
    download_video(videos)