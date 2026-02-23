import requests
import json
from datetime import datetime
import pytz
import re

# ---------------------------------------------------------
# 🛡️ FALLBACK LIST (Agar Internet kaam na kare toh ye chalega)
# ---------------------------------------------------------
BACKUP_CHANNELS = [
    {"id": "bak-1", "name": "PTV Sports (Pak)", "logo": "https://i.imgur.com/S91918c.png", "url": "https://cdn.ptv.com.pk/livestream/ptvsports/playlist.m3u8", "group": "Backup VIP"},
    {"id": "bak-2", "name": "Ten Sports (Pak)", "logo": "https://i.imgur.com/8Xq5q5X.png", "url": "https://cdn.ptv.com.pk/livestream/tensports/playlist.m3u8", "group": "Backup VIP"},
    {"id": "bak-3", "name": "A Sports", "logo": "https://i.imgur.com/Pj1yWlZ.png", "url": "https://cdn.ptv.com.pk/livestream/asports/playlist.m3u8", "group": "Backup VIP"},
    {"id": "bak-4", "name": "DD Sports (Ind)", "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/8/88/DD_Sports_logo.svg/1200px-DD_Sports_logo.svg.png", "url": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8", "group": "Backup VIP"},
    {"id": "bak-5", "name": "Willow Cricket", "logo": "https://upload.wikimedia.org/wikipedia/en/thumb/6/60/Willow_TV_logo.svg/1200px-Willow_TV_logo.svg.png", "url": "http://tv.digitalview.live:8080/live/willow/willow/1000.m3u8", "group": "Backup VIP"}
]

# ---------------------------------------------------------
# 🌍 PUBLIC SOURCES (Badi Lists)
# ---------------------------------------------------------
SOURCES = [
    "https://iptv-org.github.io/iptv/categories/sports.m3u",
    "https://raw.githubusercontent.com/FunctionError/PiratesTv/main/combined_playlist.m3u"
]

# 🔍 KEYWORDS (In namon ko dhoondo)
KEYWORDS = ["cricket", "willow", "star sports", "sony ten", "ptv sports", "ten sports", "astro", "sky sports", "fox cricket"]

def scan_web():
    found = []
    seen_urls = set()
    print("🌍 Internet scan shuru...")
    
    headers = {"User-Agent": "Mozilla/5.0"}

    for url in SOURCES:
        try:
            print(f"   Scanning: {url}...")
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code != 200: continue
            
            lines = res.text.splitlines()
            current_name = ""
            current_logo = ""

            for line in lines:
                line = line.strip()
                if line.startswith("#EXTINF:"):
                    name = line.split(",")[-1].strip()
                    logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                    current_logo = logo_match.group(1) if logo_match else ""
                    current_name = name
                elif line.startswith("http") and current_name:
                    # Filter: Sirf Cricket walay
                    if any(k in current_name.lower() for k in KEYWORDS):
                        if line not in seen_urls:
                            found.append({
                                "id": f"vip-{len(found)}",
                                "name": current_name,
                                "logo": current_logo or "https://ui-avatars.com/api/?name=Cric",
                                "url": line,
                                "group": "VIP Cricket"
                            })
                            seen_urls.add(line)
                    current_name = ""
        except:
            pass
            
    return found

def main():
    # 1. Web se dhoondo
    channels = scan_web()
    
    # 2. Agar web se kam mile, toh Backup mix karo
    if len(channels) < 5:
        print("⚠️ Web scan weak tha. Backup channels add kar raha hoon.")
        channels.extend(BACKUP_CHANNELS)
    
    # 3. Save karo
    output = {
        "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %I:%M:%S %p"),
        "total": len(channels),
        "channels": channels
    }

    with open('vip_cricket.json', 'w') as f:
        json.dump(output, f, indent=4)
        
    print(f"\n✅ DONE! {len(channels)} Channels 'vip_cricket.json' mein save ho gaye.")

if __name__ == "__main__":
    main()