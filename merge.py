import feedparser
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring

FEEDS = [
    "https://www.google.com/alerts/feeds/00744178061068326504/7865044773089010058",
    "https://www.ign.com/rss/v2/articles/feed?channel=playstation"
]

KEYWORDS = [
    "console", 
    "games", 
    "release", 
    "deals", 
    "discount", 
    "Sony", 
    "Nintendo", 
    "GTA", 
    "PlayStation",
    "PS5"
]

def matches(entry):
    text = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
    return any(k.lower() in text for k in KEYWORDS)

entries = []
seen_links = set()  # This tracks unique URLs to prevent duplicates

for url in FEEDS:
    try:
        feed = feedparser.parse(url)
        for e in feed.entries:
            link = e.get("link", "")
            
            # Check 1: Does it match keywords?
            # Check 2: Have we seen this link already in this run?
            if matches(e) and link not in seen_links:
                seen_links.add(link)
                entries.append({
                    "title": e.get("title", ""),
                    "link": link,
                    "published": e.get("published_parsed")
                })
    except Exception as e:
        print(f"Error parsing {url}: {e}")

# Sort by date (newest first)
entries.sort(key=lambda x: x["published"] or datetime.min.timetuple(), reverse=True)

# Build the RSS XML
rss = Element("rss")
rss.set("version", "2.0")
channel = SubElement(rss, "channel")

SubElement(channel, "title").text = "Filtered & De-duplicated Feed"
SubElement(channel, "link").text = "https://github.com"
SubElement(channel, "description").text = "Keyword filtered RSS with no duplicates"

for e in entries[:100]:
    item = SubElement(channel, "item")
    SubElement(item, "title").text = e["title"]
    SubElement(item, "link").text = e["link"]

with open("feed.xml", "wb") as f:
    f.write(tostring(rss, encoding="utf-8"))
