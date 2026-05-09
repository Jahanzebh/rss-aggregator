import feedparser
import time
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
import collections

# --- 1. THE NEWS NET (SOURCES) ---
FEEDS = [
    # === GLOBAL GAMING GIANTS ===
    "https://www.ign.com/rss/v2/articles/feed",
    "https://www.gamespot.com/feeds/news/",
    "https://www.eurogamer.net/feed/news",
    "https://www.polygon.com/rss/index.xml",
    "https://kotaku.com/rss",
    "https://www.destructoid.com/feed/",
    "https://www.dualshockers.com/feed/",

    # === PLAYSTATION SPECIALISTS ===
    "https://blog.playstation.com/feed/",
    "https://www.pushsquare.com/feeds/latest",

    # === INDUSTRY & LEAKS ===
    "https://www.videogameschronicle.com/feed/",
    "https://www.gamesindustry.biz/rss/news",
    "https://www.reddit.com/r/GamingLeaksAndRumours/.rss",

    # === TECHNICAL & DEALS ===
    "https://www.eurogamer.net/feed/digitalfoundry",
    "https://www.reddit.com/r/GameDeals/.rss",
    "https://www.tomshardware.com/gaming/rss",

    # === OFFICIAL STUDIO BLOGS (PRIMARY SOURCES) ===
    "https://www.rockstargames.com/newswire/feed",
    "https://www.ubisoft.com/en-US/news/feed",
    "https://www.ea.com/news/feed",

    # === INDIE GAMES ===
    "https://indiegames.com/feed",
    "https://www.reddit.com/r/IndieGaming/.rss",

    # === HIGH-SIGNAL GAMING COMMUNITIES ===
    "https://www.reddit.com/r/games/.rss",
    "https://www.reddit.com/r/PS5/.rss",
    "https://www.reddit.com/r/XboxSeriesX/.rss",

    # === ESPORTS ===
    "https://www.espn.com/esports/rss/",

    # === YOUR PERSONAL GOOGLE ALERTS ===
    "https://www.google.com/alerts/feeds/00744178061068326504/7865044773089010058",
    "https://www.google.com/alerts/feeds/00744178061068326504/11084685464649422787",
    "https://www.google.com/alerts/feeds/00744178061068326504/11084685464649421116",
    "https://www.google.com/alerts/feeds/00744178061068326504/12317157271606449361",
    "https://www.google.com/alerts/feeds/00744178061068326504/9770814918054868626",
    "https://www.google.com/alerts/feeds/00744178061068326504/561232884005252815",
    "https://www.google.com/alerts/feeds/00744178061068326504/9770814918054868671",
    "https://www.google.com/alerts/feeds/00744178061068326504/17762728314234451441",
    "https://www.google.com/alerts/feeds/00744178061068326504/561232884005249369",
    "https://www.google.com/alerts/feeds/00744178061068326504/9023093616418967248",
    "https://www.google.com/alerts/feeds/00744178061068326504/9023093616418965256"
]

# --- 2. THE RADAR (KEYWORDS) ---
KEYWORDS = [
    # === SUBSCRIPTIONS & SERVICES ===
    "SIE", "Sony Interactive Entertainment", "Gamepass", "PS Plus", "PlayStation Plus",
    "PS+", "subscriptions", "subscription", "Xbox Live", "PSN", "Epic Games", "Steam", "GOG",

    # === HARDWARE & PLATFORMS ===
    "Sony", "PlayStation", "PS5", "PS5 Pro", "Nintendo", "Switch", "Switch 2", "Xbox",
    "Steam Deck", "PC Gaming", "Console", "Handheld", "Cloud gaming",

    # === MAJOR PUBLISHERS & JAPANESE GIANTS ===
    "Tencent", "Take-Two", "Take2", "Rockstar", "2K Games", "Capcom", "Square Enix",
    "Bandai Namco", "Sega", "FromSoftware", "Konami", "PlatinumGames", "Atlus",
    "Activision", "Blizzard", "Ubisoft", "EA", "Electronic Arts", "Bethesda",

    # === FAMOUS STUDIOS & DEVS ===
    "Naughty Dog", "Insomniac", "BioWare", "CD Projekt", "Epic Games", "Bungie",
    "Riot Games", "Valve", "Kojima", "Miyamoto", "Sakurai", "Todd Howard",
    "Druckmann", "Barlog", "Miyazaki",

    # === SPECIFIC FRANCHISES & GAMES ===
    "Final Fantasy", "Persona", "Elden Ring", "Baldur's Gate 3", "Starfield",
    "Dragon Age", "The Elder Scrolls", "Mass Effect", "Metal Gear", "GTA", "GTA 6", "GTA VI",

    # === INDUSTRY BUZZ & CONTENT ===
    "esports", "AAA", "AA", "Indie", "leaks", "rumors", "rumour", "gameplay",
    "trailer", "release date", "patch notes", "DLC", "remaster", "remake", "new release",
    "deals", "discount",

    # === TECHNOLOGY & GRAPHICS ===
    "Ray tracing", "DLSS", "FSR", "frame rate", "4K", "1440p", "120fps", "performance",
    "next-gen", "AI", "machine learning",

    # === GAME CONTENT TYPES ===
    "walkthrough", "speedrun", "emulation", "modding", "mods", "ROM hack",

    # === MONETIZATION & BUSINESS ===
    "battle pass", "cosmetics", "Season Pass", "NFT", "blockchain",

    # === EVENTS ===
    "E3", "Gamescom", "Tokyo Game Show", "GDC", "PAX", "CES",

    # === SOCIAL ISSUES ===
    "crunch", "diversity", "accessibility", "transgender", "inclusivity"
]

# --- 3. THE LOGIC ---

# Diversity Quota: Max items from any one category per run
MAX_PER_CATEGORY = 10

def get_diversity_category(text):
    """Internal logic to identify categories for balancing, keeping keywords organized above."""
    text = text.lower()
    if any(k in text for k in ["xbox", "gamepass", "microsoft", "activision"]):
        return "XBOX"
    if any(k in text for k in ["ps5", "playstation", "sony", "ps plus", "sie", "naughty dog", "insomniac"]):
        return "PLAYSTATION"
    if any(k in text for k in ["nintendo", "switch", "zelda", "mario"]):
        return "NINTENDO"
    if any(k in text for k in ["leak", "rumor", "rumour"]):
        return "LEAKS"
    if any(k in text for k in ["esport", "competitive", "tournament", "pro gaming"]):
        return "ESPORTS"
    if any(k in text for k in ["indie", "indiegame"]):
        return "INDIE"
    return "GENERAL"

def matches(entry):
    title = entry.get("title", "")
    summary = entry.get("summary", "")
    description = entry.get("description", "")
    combined_text = (title + " " + summary + " " + description).lower()
    return any(k.lower() in combined_text for k in KEYWORDS)

feedparser.USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) NewsBot/1.0"

raw_entries = []
seen_links = set()

for url in FEEDS:
    try:
        feed = feedparser.parse(url)
        for e in feed.entries:
            # Use stripped URL (no query params) only for dedup tracking.
            # Store the full original URL so redirect targets are preserved.
            link_for_dedup = e.get("link", "").split('?')[0]
            link = e.get("link", "")  # full URL — keeps Google redirect params intact

            if not link_for_dedup or link_for_dedup in seen_links:
                continue

            if matches(e):
                seen_links.add(link_for_dedup)
                raw_date = e.get("published_parsed") or e.get("updated_parsed") or time.gmtime()

                title = e.get("title", "No Title")
                description = (e.get("summary", "") or e.get("description", ""))[:500]

                raw_entries.append({
                    "title": title,
                    "link": link,
                    "description": description,
                    "published": raw_date,
                    "category": get_diversity_category(title + " " + e.get("summary", ""))
                })
    except Exception as err:
        print(f"Skipping {url}: {err}")

# Sort by newest first
raw_entries.sort(key=lambda x: x["published"], reverse=True)

# Apply diversity filter
final_entries = []
category_counts = collections.defaultdict(int)

for entry in raw_entries:
    cat = entry["category"]
    if category_counts[cat] < MAX_PER_CATEGORY:
        final_entries.append(entry)
        category_counts[cat] += 1
    if len(final_entries) >= 100: break

# --- 4. THE OUTPUT (XML GENERATION) ---
rss = Element("rss")
rss.set("version", "2.0")
channel = SubElement(rss, "channel")

SubElement(channel, "title").text = "Jay Respawns: Ultimate Balanced Feed"
SubElement(channel, "link").text = "https://jayrespawns.com"
SubElement(channel, "description").text = "Organized gaming news, leaks, and updates."

for e in final_entries:
    item = SubElement(channel, "item")
    SubElement(item, "title").text = f"[{e['category']}] {e['title']}"
    SubElement(item, "link").text = str(e["link"])
    SubElement(item, "guid").text = str(e["link"])
    SubElement(item, "description").text = str(e.get("description", ""))

    try:
        pub_date_str = time.strftime("%a, %d %b %Y %H:%M:%S +0000", e["published"])
        SubElement(item, "pubDate").text = pub_date_str
    except:
        current_time = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime())
        SubElement(item, "pubDate").text = current_time

with open("feed.xml", "wb") as f:
    f.write(tostring(rss, encoding="utf-8"))

print(f"Success! Balanced feed created with {len(final_entries)} items.")
