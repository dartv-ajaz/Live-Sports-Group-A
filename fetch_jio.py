import requests
import json
from datetime import datetime
import pytz
import re

# ---------------------------------------------------------
# CONFIGURATION: Yahan apni M3U Link daalein
# ---------------------------------------------------------
# Filhal yeh ek public playlist hai (Example ke liye)
PLAYLIST_URL = "https://raw.githubusercontent.com/FunctionError/PiratesTv/main/jio_playlist_example.m3u" 
# Agar aapke paas apni link hai (e.g. jio.dinesh29...) toh usay upar replace karein.

def parse_m3u(m3u_content):
    channels = []
    lines = m3u_content.splitlines()
    
    current_channel = {}
    
    for line in lines:
        line = line.strip()
        
        if line.startswith("#EXTINF:"):
            # Logo nikalna
            logo_match = re.search(r'tvg-logo="([^"]+)"', line)
            logo = logo_match.group(1) if logo_match else ""
            
            # Channel Name nikalna
            name = line.split(",")[-1].strip()
            
            current_channel = {
                "name": name,
                "logo": logo,
                "group": "JioTV"
            }
            
        elif line.startswith("http"):
            # URL mil gayi, ab channel save karein
            if current_channel:
                current_channel["url"] = line
                # ID banana (Name se)
                current_channel["id"] = "".join(e for e in current_channel["name"] if e.isalnum())
                
                channels.append(current_channel)
                current_channel = {} # Reset
                
    return channels

def get_jio_channels():
    print("🚀 Fetching JioTV Channels...")
    
    try:
        response = requests.get(PLAYLIST_URL, timeout=10)
        if response.status_code == 200:
            print("✅ Playlist downloaded successfully!")
            return parse_m3u(response.text)
        else:
            print(f"⚠️ Failed to fetch playlist. Status: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Error fetching JioTV: {e}")
        return []

def main():
    channels = get_jio_channels()
    
    # AGAR KOI CHANNEL NA MILE TOH DEMO ADD KAREIN
    if not channels:
        print("⚠️ No channels found. Adding Demo Jio Channels...")
        channels = [
            {
                "id": "jio-news-1",
                "name": "Jio News (Demo)",
                "logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/14/News18_India_logo.svg/1200px-News18_India_logo.svg.png",
                "url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
                "group": "News"
            },
            {
                "id": "jio-sports-1",
                "name": "Jio Sports (Demo)",
                "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/5/5a/Sports18_Logo.svg/1200px-Sports18_Logo.svg.png",
                "url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
                "group": "Sports"
            }
        ]

    # JSON File Save Karna
    output = {
        "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %I:%M:%S %p"),
        "total_channels": len(channels),
        "channels": channels
    }

    with open('jio_channels.json', 'w') as f:
        json.dump(output, f, indent=4)
    
    print(f"\n✅ Saved {len(channels)} channels to 'jio_channels.json'")

if __name__ == "__main__":
    main()