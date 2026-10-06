import os
import re
import yt_dlp
from difflib import SequenceMatcher
from pathlib import Path
from datetime import datetime
import json
import pandas as pd

QUERIES= [
    # Broad election campaign
    "Bihar election 2025 rally",
    "Bihar election 2025 speech",
    "Bihar election 2025 campaign rally",
    "Bihar election 2025 election rally",
    "Bihar election 2025 campaign speech",
    "Bihar assembly election 2025 rally",
    "Bihar assembly election 2025 speech",
    "Bihar assembly election 2025 campaign",

    # Public meetings / addresses
    "Bihar election 2025 public meeting",
    "Bihar election 2025 public address",
    "Bihar election 2025 election meeting",
    "Bihar election 2025 campaign meeting",
    "Bihar election 2025 election सभा",
    "Bihar election 2025 जनसभा",
    "Bihar election 2025 चुनाव सभा",
    "Bihar election 2025 चुनावी सभा",


    # Full-length content
    "Bihar election 2025 full rally",
    "Bihar election 2025 full speech",
    "Bihar election 2025 full campaign speech",
    "Bihar election 2025 live rally",
    "Bihar election 2025 live speech",
    "Bihar election 2025 campaign live",

    # Constituency / ground campaign language
    "Bihar election 2025 चुनावी रैली",
    "Bihar election 2025 चुनाव प्रचार",
    "Bihar election 2025 चुनावी भाषण",
    "Bihar election 2025 चुनावी जनसभा",
    "Bihar election 2025 प्रचार सभा",
]
DATE_dmy = "14/11/2025"
DATE = datetime.strptime(DATE_dmy, "%d/%m/%Y")
STATE = "Bihar"



SPEAKER_ALIASES = {
    "narendra modi":    ["narendra modi", "pm narendra modi", "pm modi", "modi",
                         "नरेंद्र मोदी", "नरेन्द्र मोदी", "पीएम मोदी",
                         "प्रधानमंत्री मोदी", "मोदी"],
    "amit shah":        ["amit shah", "amitshah",
                         "अमित शाह", "गृह मंत्री अमित शाह"],
    "nitish kumar":     ["nitish kumar", "cm nitish kumar", "nitish",
                         "नीतीश कुमार", "सीएम नीतीश", "मुख्यमंत्री नीतीश", "नीतीश"],
    "tej pratap yadav": ["tej pratap yadav", "tej pratap",
                         "तेज प्रताप यादव", "तेजप्रताप यादव", "तेज प्रताप"],
    "tejashwi yadav":   ["tejashwi yadav", "tejashwi",
                         "तेजस्वी यादव", "तेजस्वी प्रसाद यादव", "तेजस्वी"],
    "rahul gandhi":     ["rahul gandhi", "राहुल गांधी", "राहुल गाँधी"],
    "priyanka gandhi":  ["priyanka gandhi", "प्रियंका गांधी", "प्रियंका गाँधी",
                         "प्रियंका गांधी वाड्रा"],
    "samrat choudhary": ["samrat choudhary", "samrat chaudhary",
                         "सम्राट चौधरी", "सम्राट चौधरी"],
    "chirag paswan":    ["chirag paswan", "चिराग पासवान", "चिराग"],
    "yogi adityanath":  ["yogi adityanath", "cm yogi",
                         "योगी आदित्यनाथ", "सीएम योगी", "योगी"],
    "lalu yadav":       ["lalu yadav", "lalu prasad yadav",
                         "लालू प्रसाद यादव", "लालू यादव", "लालू प्रसाद", "लालू"],
    "mukesh sahani":    ["mukesh sahani", "मुकेश सहनी", "मुकेश साहनी"],
    "asaduddin owaisi": ["asaduddin owaisi", "owaisi",
                         "असदुद्दीन ओवैसी", "ओवैसी"],
    "prashant kishor":  ["prashant kishor", "प्रशांत किशोर"],
    "pawan singh":      ["pawan singh", "पवन सिंह"],
    "jp nadda":         ["jp nadda", "j p nadda", "j.p. nadda", "नड्डा", "जेपी नड्डा"],
    "rajnath singh":    ["rajnath singh", "राजनाथ सिंह", "राजनाथ"],
    "lalan singh":      ["lalan singh", "rajiv ranjan singh", "ललन सिंह", "राजीव रंजन सिंह"],
    "vijay sinha":      ["vijay kumar sinha", "vijay sinha", "विजय कुमार सिन्हा", "विजय सिन्हा"],
    "pappu yadav":      ["pappu yadav", "rajesh ranjan", "पप्पू यादव", "राजेश रंजन"],
    "akhilesh yadav":   ["akhilesh yadav", "akhilesh", "अखिलेश यादव", "अखिलेश"],
    "manoj tiwari":     ["manoj tiwari", "मनोज तिवारी"],
    "ravi kishan":      ["ravi kishan", "रवि किशन"]
}

PLACE_ALIASES = {
    "muzaffarpur": ["muzaffarpur", "muzzaffarpur", "मुजफ्फरपुर", "मुज़फ़्फ़रपुर"],
    "gurua":       ["gurua", "गुरुआ", "गुरूआ"],
    "samastipur":  ["samastipur", "समस्तीपुर"],
    "chhapra":     ["chhapra", "chhapara", "chapra", "छपरा"],
    "lakhisarai":  ["lakhisarai", "लखीसराय", "लखिसराय"],
    "buxar":       ["buxar", "बक्सर"],
    "begusarai":   ["begusarai", "बेगूसराय", "बेगुसराय"],
    "banka":       ["banka", "बांका", "बाँका"],
    "khagaria":    ["khagaria", "खगड़िया", "खगडिया"],
    "karakat":     ["karakat", "काराकाट"],
    "gaighat":     ["gaighat", "गायघाट"],
    "nalanda":     ["nalanda", "नालंदा", "नालन्दा"],
    "darbhanga":   ["darbhanga", "दरभंगा", "दरभङ्गा"],
    "saharsa":     ["saharsa", "सहरसा"],
    "katihar":     ["katihar", "कटिहार"],
    "bhagalpur":   ["bhagalpur", "भागलपुर"],
    "araria":      ["araria", "अररिया"],
    "madhepura":   ["madhepura", "मधेपुरा"],
    "asthawan":    ["asthawan", "अस्थावां", "अस्थावाँ", "अस्थामा"],
    "alinagar":    ["alinagar", "अलीनगर"],
    "rohtas":      ["rohtas", "रोहतास"],
    "sonabarsa":   ["sonabarsa","सोनबरसा"],
    "bettiah":     ["bettiah", "बेतिया"],
    "tarapur":     ["tarapur", "तारापुर"],
    "rajgir":      ["rajgir", "राजगीर"],
    "purnia":      ["purnia", "purnea", "पूर्णिया", "पूरनिया"],
    "motihari":    ["motihari", "मोतिहारी"],
    "hajihaipur":  ["hajipur", "हाजीपुर"],
    "gaya":        ["gaya", "गया"],
    "patna sahib": ["patna sahib", "पटना साहिब"],
    "sonepur":     ["sonepur", "sonpur", "सोनपुर"],
    "paru":        ["paru", "पारू", "पारु"],
    "baisi":       ["baisi", "बैसी", "बायसी"]

}
# def generate_place_aliases(csv_file, state_name):
#     df = pd.read_csv(csv_file)

#     df.columns = [c.strip() for c in df.columns]

#     df = df[df["State/Union territory*"]
#               .str.strip()
#               .str.lower() == state_name.lower()]

#     aliases = {}
    
#     for col in ["City/Town", "District"]:
#         for place in df[col].dropna().unique():
#             place = str(place).strip().lower()
#             aliases.setdefault(place, [place])
        
#     return aliases


import unicodedata
def _norm(s):
    s = (s or "").lower()
    s = unicodedata.normalize("NFD", s)
    s = s.replace("\u093c", "")   # drop nukta
    s = unicodedata.normalize("NFC", s)
    s = re.sub(r"[^a-z\u0900-\u097f\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def _lookup_canonical(title_norm, alias_dict):

    for canon, aliases in alias_dict.items():
        for alias in aliases:
            if _norm(alias) in title_norm:
                return canon

    return None

def extract_speaker_place(title,desr):
    t = _norm(title)
    des = _norm(desr)
    place = _lookup_canonical(t, PLACE_ALIASES)
    if place is None:
        place = _lookup_canonical(des, PLACE_ALIASES)
    return _lookup_canonical(t, SPEAKER_ALIASES), place


def search_youtube(query, max_videos=50):

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,
        "skip_download": True,
        "ignoreerrors": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        results = ydl.extract_info(
            f"ytsearch{max_videos}:{query}",
            download=False
        )
    videos = []
    seen = set()
    for entry in results.get("entries", []):
        if entry is None:
            continue

        video_id = entry.get("id")
        if not video_id or video_id in seen:
            continue

        duration = entry.get('duration')
        if duration is None or duration < 900:
            continue
        uploaddata = entry.get('upload_date')
        upload_date = datetime.strptime(uploaddata, "%Y%m%d")

        if upload_date > DATE:
            continue

        title = entry.get("title", "").lower()
        descri = (entry.get("description") or "").lower()
        combined = title + " " + descri
        was_live = entry.get("was_live", False)

        if not was_live:
            continue
        if "election result" in combined:
            continue
        relevant_keywords = ["rally", "rallies", "speech", "address",
                             "public meeting", "election meeting", "election rally",
                             "campaign rally", "campaign speech", "jan sabha",
                             "जनसभा", "चुनावी सभा", "चुनाव सभा", "चुनावी रैली",
                             "चुनाव प्रचार", "चुनावी भाषण", "प्रचार सभा"]
        if not any(kw in title for kw in relevant_keywords):
            continue
      
        seen.add(video_id)
        release_ts = entry.get("release_timestamp") or entry.get("timestamp")

        videos.append({
            "id":                video_id,
            "title":             entry.get("title", ""),
            "url":               f"https://www.youtube.com/watch?v={video_id}",
            "duration":          duration,
            "channel":           entry.get("channel", ""),
            "channel_id":        entry.get("channel_id", ""),
            "upload_date":       entry.get("upload_date", ""),  
            "release_timestamp": release_ts,                     
            "description":       entry.get("description", ""),
            "view_count":        entry.get("view_count", 0),
            "thumbnail":         entry.get("thumbnail", ""),
            "tags":              entry.get("tags", []),
            "categories":        entry.get("categories", []),
            "search_query":      query,
            "live_status":       entry.get("live_status", ""),
            "was_live":          entry.get("was_live", "")
        })

    # with open("videos.json", "w", encoding="utf-8") as f:
    #     json.dump(videos, f, indent=4, ensure_ascii=False)
    return videos


def normalize_title(title):
    """Strip channel names, punctuation, common words to compare core content"""
    title = title.lower()
    title = re.sub(r'[^a-z\s]', ' ', title)
    title = ' '.join(title.split())
    noise = ['live', 'aaj tak', 'abp', 'ndtv', 'news18', 'zee news', 'rally', 'elections', 'election',
             'india today', '|', ':', '-', '\u00a0', 'full speech', 'addresses', 'public', 'prime minister',
             'cheif minister','pm', 'cm', 'breaking', 'hm', '', '2025', 'bihar', 'mahagathbandhan', 'nda', 'bjp', 'rjd', 'congress']
    for n in noise:
        title = title.replace(n, ' ')
    title = re.sub(r'[^\w\s]', ' ', title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title


def title_similarity(t1, t2):
    """Returns 0.0 to 1.0 — how similar two titles are"""
    return SequenceMatcher(None, normalize_title(t1), normalize_title(t2)).ratio()


def same_date(v1, v2):
    """Check if uploaded within 2 days of each other (covers same event).
    Kept as a coarse fallback for videos missing a release_timestamp."""
    try:
        d1 = datetime.strptime(v1['upload_date'], "%Y%m%d")
        d2 = datetime.strptime(v2['upload_date'], "%Y%m%d")
        return abs((d1 - d2).days) <= 2
    except (ValueError, TypeError):
        return False

MIN_OVERLAP_FRACTION = 0.4


def live_window(v):
    """Returns (start, end) epoch seconds for a video's live broadcast,
    or None if we don't have a usable timestamp for it."""
    start = v.get("release_timestamp")
    duration = v.get("duration")
    if not start or not duration:
        return None
    return start, start + duration


def time_windows_overlap(v1, v2):
    w1, w2 = live_window(v1), live_window(v2)
    if w1 is None or w2 is None:
        return False 
    overlap = min(w1[1], w2[1]) - max(w1[0], w2[0])
    if overlap <= 0:
        return False
    shorter_duration = min(v1["duration"], v2["duration"])
    return (overlap / shorter_duration) >= MIN_OVERLAP_FRACTION


def same_event(v1, v2, title_threshold=0.7):
    """
    True if v1 and v2 are almost certainly the SAME real-world rally,
    just captured/uploaded by different channels.

    Primary path (preferred): broadcast windows overlap substantially
    AND speaker or place matches (or, if neither could be extracted,
    titles are at least loosely similar) — this is what stops two
    genuinely different, simultaneous rallies from being merged just
    because they happened to be live at the same time.

    Fallback path (used when timestamps are missing for either video):
    your original title-similarity + same-day check.
    """
    title1,desr1=v1['title'],v1['description']
    title2,desr2=v2['title'],v2['description']

    

    s1, p1 = extract_speaker_place(title1,desr1)
    s2, p2 = extract_speaker_place(title2,desr2)

    # known on both sides and different -> different events
    if (s1 and s2 and s1 != s2) or (p1 and p2 and p1 != p2):
        return False

    if live_window(v1) and live_window(v2):          # timestamps available
        if not time_windows_overlap(v1, v2):
            return False
        if (s1 and s2) or (p1 and p2):               # speaker OR place agrees
            return True
        return title_similarity(v1["title"], v2["title"]) >= title_threshold

    # no timestamps: fall back to date (+ title unless speaker and place both match)
    if s1 and s2 and p1 and p2:
        return same_date(v1, v2)
    return same_date(v1, v2) and title_similarity(v1["title"], v2["title"]) >= 0.7

def group_similar_videos(videos, title_threshold=0.7):

    n = len(videos)
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx != ry:
            parent[rx] = ry

    for i in range(n):
        for j in range(i + 1, n):
            if same_event(videos[i], videos[j], title_threshold=title_threshold):
                union(i, j)

    groups_dict = {}
    for idx in range(n):
        root = find(idx)
        groups_dict.setdefault(root, []).append(videos[idx])

    return list(groups_dict.values())


def select_best_from_groups(groups):

    kept = []
    for group in groups:
        best = max(group, key=lambda v: v['duration'])
        best['duplicate_count'] = len(group)
        best['duplicate_sources'] = [g['channel'] for g in group]
        kept.append(best)

        if len(group) > 1:
            print(f"Group of {len(group)} -> kept: "
                  f"{best['channel']} ({best['duration']:.0f}s) "
                  f"'{best['title']}'")
            for g in sorted(group, key=lambda v: v['duration'], reverse=True):
                if g['id'] != best['id']:
                    print(f"  dropped: {g['channel']} ({g['duration']:.0f}s) "
                          f"'{g['title']}'")

    titles = [(video["title"], video["url"]) for video in kept]

    with open("cleaned_videos.json", "w", encoding="utf-8") as f:
        json.dump(titles, f, indent=4, ensure_ascii=False)
    return kept


def main():

    # all_videos = []

    # for query in QUERIES:

    #     print(f"\nSearching: {query}")

    #     videos = search_youtube(query, 200)

    #     print(f"Found {len(videos)} candidates")

    #     all_videos.extend(videos)

    # # Remove exact YouTube duplicates from different queries
    # unique_by_id = {}

    # for video in all_videos:
    #     unique_by_id[video["id"]] = video

    # videos = list(unique_by_id.values())
    
    # with open("videos.json", "w", encoding="utf-8") as f:
    #     json.dump(videos, f, indent=4, ensure_ascii=False)

    # print(f"\n==============================")
    # print(f"Total unique videos: {len(videos)}")
    # print(f"==============================")

    # # Now deduplicate videos covering the SAME real-world event

    # with open("videos.json", "r", encoding="utf-8") as f:
    #     videos = json.load(f)
    # print(f"Loaded {len(videos)} videos from videos.json")

    

    # groups = group_similar_videos(
    #     videos,
    #     title_threshold=0.7
    # )

    # print(f"\nFound {len(groups)} unique event groups")

    # unique_videos = select_best_from_groups(groups)

    # print(f"After event dedup: {len(unique_videos)} videos")


    #dividing mgb and nda videos


    
    

    with open("cleaned_videos_metadata.json", "r", encoding="utf-8") as f:
                videos2 = json.load(f)
    print(f"Loaded {len(videos2)} videos from cleaned_videos_metadata.json")
    
    mgb_videos = []
    nda_videos = []

    for video in videos2:
        if video.get("party") == "Mahagathbandhan":
            mgb_videos.append(video)

        elif video.get("party") == "NDA":
            nda_videos.append(video)

    with open("cleaned_videos_metadata_mgb.json", "w", encoding="utf-8") as f:
        json.dump(mgb_videos, f, ensure_ascii=False, indent=2)
    
    with open("cleaned_videos_metadata_nda.json", "w", encoding="utf-8") as f:
        json.dump(nda_videos, f, ensure_ascii=False, indent=2)

 
            

            
            
            

            
        

if __name__ == "__main__":
    main()