import requests
import json
import time
from datetime import datetime, timezone

# 1. AAPKI ORIGINAL PLAYLISTS (URLs Fixed and Cleaned)
PLAYLIST_URLS = [
    {"id": "cat-sultan", "url": "https://raw.githubusercontent.com/dartv-ajaz/Live-Sports-Group-A/main/sultan_cricket.json"},
    {"id": "cat-cricket", "url": "https://raw.githubusercontent.com/dartv-ajaz/Live-Sports-Group-A/main/cricket_channels.json"},
    {"id": "cat-vip", "url": "https://raw.githubusercontent.com/dartv-ajaz/Live-Sports-Group-A/main/vip_cricket.json"}
]

# 🚀 SMART RETRY ENGINE (Agar server slow ho toh yeh 3 baar try karega)
def fetch_with_retry(url, retries=3):
    for i in range(retries):
        try:
            # Timeout barha kar 20 seconds kar diya hai
            r = requests.get(url, timeout=20)
            if r.status_code == 200:
                return r.json()
            else:
                print(f"    [!] Error {r.status_code} for {url}")
        except Exception as e:
            print(f"    [!] Attempt {i+1} failed... Retrying in 2 seconds.")
            time.sleep(2)
    return None

def fetch_my_channels():
    print("[*] Playlists se channels nikal raha hoon...")
    channels = []
    for pl in PLAYLIST_URLS:
        print(f" -> Fetching {pl['id']}...")
        data = fetch_with_retry(pl["url"])
        
        if data:
            # Handle different JSON structures
            items = data if isinstance(data, list) else data.get("channels", data.get("matches", []))
            
            for item in items:
                name = item.get("name", item.get("title", "Unknown Channel"))
                stream = item.get("url", item.get("streamUrl", item.get("adfree_url", "")))
                logo = item.get("logo", item.get("src", ""))
                
                if stream:
                    channels.append({
                        "name": name,
                        "stream": stream,
                        "logo": logo,
                        "category": pl["id"]
                    })
        else:
            print(f"[!] Failed to fetch {pl['id']} after 3 attempts.")
            
    print(f"[+] Total {len(channels)} channels fetch ho gaye!\n")
    return channels

def fetch_free_live_events():
    print("[*] Free API se Real Live Matches nikal raha hoon...")
    events = []
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    sports = ["Soccer", "Cricket", "Motorsport", "Basketball"]
    
    for sport in sports:
        url = f"https://www.thesportsdb.com/api/v1/json/3/eventsday.php?d={today}&s={sport}"
        data = fetch_with_retry(url)
        if data and "events" in data and data["events"]:
            for e in data["events"]:
                events.append({
                    "sport": sport,
                    "league": e.get("strLeague", "Live Match"),
                    "team1": e.get("strHomeTeam", "Team 1"),
                    "team2": e.get("strAwayTeam", "Team 2"),
                    "time": e.get("strTimestamp", f"{e.get('dateEvent')}T{e.get('strTime')}"),
                    "status": "Live" if e.get("strStatus") not in ["Match Finished", "Finished"] else "Completed",
                    "thumb": e.get("strThumb", "")
                })
            
    print(f"[+] Total {len(events)} Live Matches mil gaye!\n")
    return events

def link_events_to_channels(events, channels):
    print("[*] Smart Linker Engine Start ho raha hai (Matches + Channels)...")
    linked_events = []
    
    # Keywords for routing
    cricket_keywords = ['cricket', 'ptv', 'ten', 'willow', 'astro', 'star sports', 'vip']
    football_keywords = ['football', 'bein', 'sky', 'supersport', 'tnt']
    
    cricket_channels = [c for c in channels if any(k in c['name'].lower() for k in cricket_keywords)]
    football_channels = [c for c in channels if any(k in c['name'].lower() for k in football_keywords)]
    fallback_channels = [c for c in channels if 'sports' in c['name'].lower()]

    for idx, e in enumerate(events):
        if e["status"] == "Completed":
            continue

        target_channels = []
        if e["sport"] == "Cricket":
            target_channels = cricket_channels if cricket_channels else fallback_channels
        elif e["sport"] == "Soccer":
            target_channels = football_channels if football_channels else fallback_channels
        else:
            target_channels = fallback_channels

        matched_links = []
        for ch in target_channels:
            is_sultan = "sultan" in ch["category"].lower()
            is_m3u8 = ".m3u8" in ch["stream"]
            matched_links.append({
                "name": f"⭐ {ch['name']} (VIP)" if is_sultan else ch['name'],
                "url": ch['stream'],
                "type": "Iframe" if is_sultan else ("Video" if is_m3u8 else "Iframe"),
                "isSultan": is_sultan
            })
        
        # Sultan VIP ko hamesha Top (No. 1) par rakho
        matched_links.sort(key=lambda x: not x["isSultan"])

        if matched_links:
            linked_events.append({
                "id": f"live-event-{idx}",
                "sport": "Football" if e["sport"] == "Soccer" else e["sport"],
                "league": e["league"],
                "team1": e["team1"],
                "team2": e["team2"],
                "team1Logo": e["thumb"] or f"https://ui-avatars.com/api/?name={e['team1']}&background=1e2024&color=fff",
                "team2Logo": f"https://ui-avatars.com/api/?name={e['team2']}&background=1e2024&color=fff",
                "status": e["status"],
                "time": e["time"],
                "isHot": True,
                "streamUrl": matched_links[0]["url"], # Top channel ka link main stream banega
                "type": matched_links[0]["type"],
                "multiLinks": matched_links[:20] # Sirf top 20 links bhejo taake json heavy na ho
            })

    return linked_events

if __name__ == "__main__":
    channels = fetch_my_channels()
    events = fetch_free_live_events()
    final_matches = link_events_to_channels(events, channels)

    # Save to JSON
    with open("dartv_live_matches.json", "w") as f:
        json.dump(final_matches, f, indent=4)
        
    print(f"\n[🚀 SUCCESS] {len(final_matches)} LIVE MATCHES TAYYAR HAIN! 'dartv_live_matches.json' file check karein.")