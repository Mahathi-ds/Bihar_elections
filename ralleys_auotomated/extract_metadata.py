import json
import re
import unicodedata
from urllib.parse import urlparse, parse_qs

SPEAKER_ALIASES =  {
     "narendra modi":        ["narendra modi", "pm narendra modi", "pm modi", "modi", "नरेंद्र मोदी", "नरेन्द्र मोदी", "पीएम मोदी", "प्रधानमंत्री मोदी", "मोदी"],
    "amit shah":            ["amit shah", "amitshah", "अमित शाह", "गृह मंत्री अमित शाह"],
    "nitish kumar":         ["nitish kumar", "cm nitish kumar", "nitish", "नीतीश कुमार", "सीएम नीतीश", "मुख्यमंत्री नीतीश", "नीतीश"],
    "samrat choudhary":     ["samrat choudhary", "samrat chaudhary", "सम्राट चौधरी"],
    "chirag paswan":        ["chirag paswan", "चिराग पासवान", "चिराग"],
    "yogi adityanath":      ["yogi adityanath", "cm yogi", "योगी आदित्यनाथ", "सीएम योगी", "योगी"],
    "jp nadda":             ["jp nadda", "j p nadda", "j.p. nadda", "नड्डा", "जेपी नड्डा"],
    "rajnath singh":        ["rajnath singh", "राजनाथ सिंह", "राजनाथ"],
    "lalan singh":          ["lalan singh", "rajiv ranjan singh", "ललन सिंह", "राजीव रंजन सिंह"],
    "vijay sinha":          ["vijay kumar sinha", "vijay sinha", "विजय कुमार सिन्हा", "विजय सिन्हा"],
    "manoj tiwari":         ["manoj tiwari", "मनोज तिवारी"],
    "ravi kishan":          ["ravi kishan", "रवि किशन"],
    "pawan singh":          ["pawan singh", "पवन सिंह"],
    "nitin gadkari":        ["nitin gadkari", "nitin jairam gadkari", "नितिन गडकरी"],
    "himanta biswa sarma":  ["himanta biswa sarma", "himanta biswa", "हिमंत बिस्वा सरमा", "हिमंता बिस्वा सरमा"],
    "devendra fadnavis":    ["devendra fadnavis", "देवेंद्र फडणवीस", "देवेंद्र फड़नवीस"],
    
    "tej pratap yadav":     ["tej pratap yadav", "tej pratap", "तेज प्रताप यादव", "तेजप्रताप यादव", "तेज प्रताप"],
    "tejashwi yadav":       ["tejashwi yadav", "tejashwi", "तेजस्वी यादव", "तेजस्वी प्रसाद यादव", "तेजस्वी"],
    "rahul gandhi":         ["rahul gandhi", "राहुल गांधी", "राहुल गाँधी"],
    "priyanka gandhi":      ["priyanka gandhi", "प्रियंका गांधी", "प्रियंका गाँधी", "प्रियंका गांधी वाड्रा"],
    "sonia gandhi":         ["sonia gandhi", "सोनिया गांधी", "सोनिया गाँधी"],
    "lalu yadav":           ["lalu yadav", "lalu prasad yadav", "लालू प्रसाद यादव", "लालू यादव", "लालू प्रसाद", "लालू"],
    "mukesh sahani":        ["mukesh sahani", "मुकेश सहनी", "मुकेश साहनी"],
    "pappu yadav":          ["pappu yadav", "rajesh ranjan", "पप्पू यादव", "राजेश रंजन"],
    "akhilesh yadav":       ["akhilesh yadav", "akhilesh", "अखिलेश यादव", "अखिलेश"],
    "dimple yadav":         ["dimple yadav", "डिंपल यादव"],
    "mallikarjun kharge":   ["mallikarjun kharge", "mallikarjun kharge", "मल्लिकार्जुन खरगे", "मल्लिकार्जुन खड़गे"],
    "kanhaiya kumar":       ["kanhaiya kumar", "kanhaiya", "कन्हैया कुमार", "कन्हैया"],
    "ashok gehlot":         ["ashok gehlot", "अशोक गहलोत"],
    "sachin pilot":         ["sachin pilot", "सचिन पायलट"],
    "bhupesh baghel":       ["bhupesh baghel", "भूपेश बघेल"],
    "digvijaya singh":      ["digvijaya singh", "digvijay singh", "दिग्विजय सिंह"],
    "sukhvinder singh sukhu":["sukhvinder singh sukhu", "sukhvinder sukhu", "सुखविंदर सिंह सुक्खू"],
    "deepankar bhattacharya":["deepankar bhattacharya", "dipankar bhattacharya", "दीपांकर भट्टाचार्य"],
    
    "asaduddin owaisi":     ["asaduddin owaisi", "owaisi", "असदुद्दीन ओवैसी", "ओवैसी"],
    "prashant kishor":      ["prashant kishor", "प्रशांत किशोर"]
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
# SPEAKER_PARTY = {

#     "narendra modi": "BJP",

#     "amit shah": "BJP",
#     "samrat choudhary": "BJP",
#     "yogi adityanath": "BJP",
#     "jp nadda": "BJP",
#     "rajnath singh": "BJP",
#     "vijay sinha": "BJP",
#     "manoj tiwari": "BJP",
#     "ravi kishan": "BJP",

#     "nitish kumar": "JDU",
#     "lalan singh": "JDU",

#     "tejashwi yadav": "RJD",
#     "tej pratap yadav": "RJD",
#     "lalu yadav": "RJD",

#     "rahul gandhi": "Congress",
#     "priyanka gandhi": "Congress",

#     "chirag paswan": "LJP",
#     "mukesh sahani": "VIP",

#     "asaduddin owaisi": "AIMIM",

#     "prashant kishor": "Jan Suraaj",
#     "mallikarjun Kharge":"Congress"
# }

SPEAKER_METADATA = {
    "narendra modi":        {"party": "BJP", "alliance": "NDA"},
    "amit shah":            {"party": "BJP", "alliance": "NDA"},
    "nitish kumar":         {"party": "JD(U)", "alliance": "NDA"},
    "samrat choudhary":     {"party": "BJP", "alliance": "NDA"},
    "chirag paswan":        {"party": "LJP(RV)", "alliance": "NDA"},
    "yogi adityanath":      {"party": "BJP", "alliance": "NDA"},
    "jp nadda":             {"party": "BJP", "alliance": "NDA"},
    "rajnath singh":        {"party": "BJP", "alliance": "NDA"},
    "lalan singh":          {"party": "JD(U)", "alliance": "NDA"},
    "vijay sinha":          {"party": "BJP", "alliance": "NDA"},
    "manoj tiwari":         {"party": "BJP", "alliance": "NDA"},
    "ravi kishan":          {"party": "BJP", "alliance": "NDA"},
    "pawan singh":          {"party": "BJP", "alliance": "NDA"},
    "nitin gadkari":        {"party": "BJP", "alliance": "NDA"},
    "himanta biswa sarma":  {"party": "BJP", "alliance": "NDA"},
    "devendra fadnavis":    {"party": "BJP", "alliance": "NDA"},
    
    "tej pratap yadav":     {"party": "RJD", "alliance": "Mahagathbandhan"},
    "tejashwi yadav":       {"party": "RJD", "alliance": "Mahagathbandhan"},
    "rahul gandhi":         {"party": "INC", "alliance": "Mahagathbandhan"},
    "priyanka gandhi":      {"party": "INC", "alliance": "Mahagathbandhan"},
    "sonia gandhi":         {"party": "INC", "alliance": "Mahagathbandhan"},
    "lalu yadav":           {"party": "RJD", "alliance": "Mahagathbandhan"},
    "mukesh sahani":        {"party": "VIP", "alliance": "Mahagathbandhan"},
    "pappu yadav":          {"party": "Independent", "alliance": "Mahagathbandhan"},
    "akhilesh yadav":       {"party": "SP", "alliance": "Mahagathbandhan"},
    "dimple yadav":         {"party": "SP", "alliance": "Mahagathbandhan"},
    "mallikarjun kharge":   {"party": "INC", "alliance": "Mahagathbandhan"},
    "kanhaiya kumar":       {"party": "INC", "alliance": "Mahagathbandhan"},
    "ashok gehlot":         {"party": "INC", "alliance": "Mahagathbandhan"},
    "sachin pilot":         {"party": "INC", "alliance": "Mahagathbandhan"},
    "bhupesh baghel":       {"party": "INC", "alliance": "Mahagathbandhan"},
    "digvijaya singh":      {"party": "INC", "alliance": "Mahagathbandhan"},
    "sukhvinder singh sukhu":{"party": "INC", "alliance": "Mahagathbandhan"},
    "deepankar bhattacharya":{"party": "CPI(ML)L", "alliance": "Mahagathbandhan"},
    
    "asaduddin owaisi":     {"party": "AIMIM", "alliance": "None"},
    "prashant kishor":      {"party": "Jan Suraaj", "alliance": "None"}
}



def _norm(s):

    s = (s or "").lower()

    s = unicodedata.normalize("NFD", s)

    # Remove Devanagari nukta
    s = s.replace("\u093c", "")

    s = unicodedata.normalize("NFC", s)

    # Keep English + Devanagari + spaces
    s = re.sub(r"[^a-z\u0900-\u097f\s]", " ", s)

    return re.sub(r"\s+", " ", s).strip()

def _lookup_canonical(text_norm, alias_dict):

    for canonical, aliases in alias_dict.items():

        for alias in aliases:

            alias_norm = _norm(alias)

            if alias_norm in text_norm:
                return canonical

    return None


def extract_speaker_place(title,descr):

    normalized_title = _norm(title)
    normalized_descr=_norm(descr)


    speaker = _lookup_canonical(
        normalized_title,
        SPEAKER_ALIASES
    )

    if speaker is None:
        speaker = _lookup_canonical(
            normalized_descr,
            SPEAKER_ALIASES
        )


    place = _lookup_canonical(
        normalized_title,
        PLACE_ALIASES
    )

    if place is None:
        place = _lookup_canonical(
            normalized_descr,
            PLACE_ALIASES
        )



    return speaker, place

def get_video_id(url):

    try:

        parsed = urlparse(url)

        query = parse_qs(parsed.query)

        if "v" in query:
            return query["v"][0]

        # In case URL is youtu.be/VIDEO_ID
        if parsed.hostname == "youtu.be":
            return parsed.path.strip("/")

    except Exception:
        pass

    return None


# ============================================================
# MAIN
# ============================================================
def extract_metadata():
    with open("cleaned_videos.json", "r", encoding="utf-8") as f:
        cleaned_videos = json.load(f)

    print(
        f"Loaded {len(cleaned_videos)} videos "
        f"from cleaned_videos.json"
    )


    with open("videos.json", "r", encoding="utf-8") as f:
        original_videos = json.load(f)

    print(
        f"Loaded {len(original_videos)} videos "
        f"from videos.json"
    )

    original_by_id = {}

    for video in original_videos:

        video_id = video.get("id")

        if video_id:
            original_by_id[video_id] = video

    metadata = []

    matched_count = 0
    unmatched_count = 0


    for item in cleaned_videos:


        if not isinstance(item, list) or len(item) < 2:
            print("Skipping malformed entry:", item)
            continue

        title = item[0]
        url = item[1]

        video_id = get_video_id(url)

        if video_id is None:

            print(
                f"Could not extract video ID from URL:\n{url}"
            )

            unmatched_count += 1
            continue
        original_video = original_by_id.get(video_id)

        if original_video is None:

            print(
                f"WARNING: video ID {video_id} "
                f"not found in videos.json"
            )

            unmatched_count += 1
            continue


        matched_count += 1
        original_title = original_video.get( "title", title)

        description = original_video.get( "description", ""
        )

        duration=original_video.get("duration",0)
       

        speaker, place = extract_speaker_place(
            original_title,
            description
        )

        party = None

        if speaker is not None:
           party = SPEAKER_METADATA.get(speaker, {}).get("alliance")


        metadata.append({

            "id": video_id,
    
            "title": title,

            "url": url,

            "description": description,

            "speaker": speaker,

            "place": place,

            "party": party,
            "duration":duration
        })

    print("\n===================================")
    print("Metadata extraction complete")
    print("===================================")

    print(
        f"Cleaned videos      : {len(cleaned_videos)}"
    )

    print(
        f"Matched with videos : {matched_count}"
    )

    print(
        f"Unmatched           : {unmatched_count}"
    )

    print(
        f"Metadata records    : {len(metadata)}"
    )

    print(
        "\nSaved to: video_metadata.json"
    )



    with open("video_metadata.json","w",encoding="utf-8") as f:
            json.dump(metadata,f,indent=4,ensure_ascii=False)
def main():

    # IMPORTANT:
    # This is your EXISTING file.
    # We only READ it.
    extract_metadata()



if __name__ == "__main__":
    main()