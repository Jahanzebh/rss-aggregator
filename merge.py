import feedparser
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring

FEEDS = [
    "https://example.com/rss",
    "https://example2.com/rss"
]

KEYWORDS = [
    "console games",
    "pc games",
    "new release",
    "game deals and discounts",
    "gaming",
    "Nintendo",
    "Sony", 
  "GTA" 
]

def matches(entry):
    text = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
    return any(k.lower() in text for k in KEYWORDS)

entries = []

for url in FEEDS:
    feed = feedparser.parse(url)
    for e in feed.entries:
        if matches(e):
            entries.append({
                "title": e.get("title", ""),
                "link": e.get("link", ""),
                "published": e.get("published_parsed")
            })

entries.sort(key=lambda x: x["published"] or datetime.min.timetuple(), reverse=True)

rss = Element("rss")
rss.set("version", "2.0")
channel = SubElement(rss, "channel")

SubElement(channel, "title").text = "Filtered Feed"
SubElement(channel, "link").text = "https://github.com"
SubElement(channel, "description").text = "Keyword filtered RSS"

for e in entries[:100]:
    item = SubElement(channel, "item")
    SubElement(item, "title").text = e["title"]
    SubElement(item, "link").text = e["link"]

with open("feed.xml", "wb") as f:
    f.write(tostring(rss, encoding="utf-8"))
