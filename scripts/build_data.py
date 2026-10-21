"""Build the Bible library the site loads from data/.

Source: the public-domain translations in github.com/scrollmapper/bible_databases
(formats/json/<ID>.json). Download them into a folder, then:

    python3 scripts/build_data.py <folder with the downloaded .json files>

Output:
    data/versions.json        list of versions and how many chapters each book has
    data/<id>/<book>.json     one file per book: [[verse 1, verse 2, ...], ...] per chapter
                              (book = 1..66, null where a version has no such verse)
"""
import json
import re
import sys
from pathlib import Path

# id on the site, file in scrollmapper, name shown in the menu, language
VERSIONS = [
    ("bsb", "BSB", "Berean Standard Bible (BSB)", "English"),
    ("kjv", "KJV", "King James Version (KJV)", "English"),
    ("asv", "ASV", "American Standard Version 1901 (ASV)", "English"),
    ("nheb", "NHEB", "New Heart English Bible (NHEB)", "English"),
    ("ylt", "YLT", "Young's Literal Translation (YLT)", "English"),
    ("darby", "Darby", "Darby Bible 1889", "English"),
    ("webster", "Webster", "Webster Bible 1833", "English"),
    ("bbe", "BBE", "Bible in Basic English (BBE)", "English"),
    ("geneva", "Geneva1599", "Geneva Bible 1599", "English"),
    ("rv1909", "SpaRV", "Reina-Valera 1909", "Español"),
    ("rv1865", "SpaRV1865", "Reina-Valera 1865", "Español"),
]

def clean(version_id, text):
    text = re.sub(r"\s+", " ", text).strip()
    if version_id == "darby":
        # the source glues some words together: "AndGod", "ofJehovah"
        text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)
    return text

def main(src):
    out = Path(__file__).resolve().parent.parent / "data"
    listing = []
    for vid, file, name, lang in VERSIONS:
        books = json.loads((Path(src) / f"{file}.json").read_text(encoding="utf-8"))["books"]
        assert len(books) == 66, f"{file}: expected 66 books, got {len(books)}"
        (out / vid).mkdir(parents=True, exist_ok=True)
        chapter_counts = []
        for n, book in enumerate(books, start=1):
            chapters = []
            for ch in book["chapters"]:
                verses = [None] * max(v["verse"] for v in ch["verses"])
                for v in ch["verses"]:
                    verses[v["verse"] - 1] = clean(vid, v["text"])
                chapters.append(verses)
            chapter_counts.append(len(chapters))
            (out / vid / f"{n}.json").write_text(
                json.dumps(chapters, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
        listing.append({"id": vid, "name": name, "lang": lang, "chapters": chapter_counts})
        print(f"{vid:8} {sum(chapter_counts):5} chapters")
    (out / "versions.json").write_text(json.dumps(listing, ensure_ascii=False, indent=1), encoding="utf-8")

if __name__ == "__main__":
    main(sys.argv[1])
