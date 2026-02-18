import requests
import json
from datetime import datetime
import pytz
import re

# ---------------------------------------------------------
# SOURCES: Yeh 3 alag sources ko scan karega taake chances zyada hon
# ---------------------------------------------------------
SOURCES = [
    "https://iptv-org.github.io/iptv/languages/hin.m3u", # Indian Hindi
    "https://iptv-org.github.io/iptv/categories/sports.m3u", # Global Sports
    "https://raw.githubusercontent.com/maheshkurmi/TV-Channels/master/Playlists/Sports.m3u" # Community List
]

# CRICKET KEYWORDS: Sirf in naam wale channels uthayega
KEYWORDS = ["cricket", "star sports", "sony sports", "willow", "ptv sports", "ten sports", "astro cricket", "sky sports cricket"]

def get_all_streams():
    found_channels = []
    seen_urls = set()
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

    for url in SOURCES:
        try:
            print(f"📡 Scanning: {url.split('/')[-1]}...")
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200: continue
            
            lines = response.text.splitlines()
            current_info = {}

            for line in lines:
                line = line.strip()
                if line.startswith("#EXTINF:"):
                    name = line.split(",")[-1].strip()
                    # Check if name contains any of our keywords
                    if any(key in name.lower() for key in KEYWORDS):
                        logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                        current_info = {
                            "name": name,
                            "logo": logo_match.group(1) if logo_match else "",
                            "group": "Cricket"
                        }
                elif line.startswith("http") and current_info:
                    stream_url = line
                    if stream_url not in seen_urls:
                        current_info["url"] = stream_url
                        current_info["id"] = f"cricket-{len(found_channels) + 1}"
                        found_channels.append(current_info)
                        seen_urls.add(stream_url)
                    current_info = {}
        except Exception as e:
            print(f"⚠️ Error scanning {url}: {e}")
            
    return found_channels

def main():
    print("🚀 Starting Cricket Channel Hunt...")
    channels = get_all_streams()
    
    if not channels:
        print("❌ Koi live cricket link nahi mili. Purani file delete nahi kar raha.")
        return

    output = {
        "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %I:%M:%S %p"),
        "total_cricket_channels": len(channels),
        "channels": channels
    }

    with open('cricket_channels.json', 'w') as f:
        json.dump(output, f, indent=4)
    
    print(f"✅ Mubarak ho! {len(channels)} Cricket channels mil gaye aur 'cricket_channels.json' mein save ho gaye.")

if __name__ == "__main__":
    main()