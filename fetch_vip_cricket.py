import requests
import json
from datetime import datetime
import pytz
import re

# ---------------------------------------------------------
# 🕵️‍♂️ THE JUGAAD SOURCES (Hidden Aggregators)
# ---------------------------------------------------------
# Yeh wo lists hain jahan aksar paid channels leak hote hain
SOURCES = [
    "https://iptv-org.github.io/iptv/categories/sports.m3u",
    "https://raw.githubusercontent.com/Mikes1278/IPTV/main/playlist.m3u", 
    "https://raw.githubusercontent.com/FunctionError/PiratesTv/main/combined_playlist.m3u"
]

# 🎯 TARGET KEYWORDS (WebCric & CricHD Special)
# Hum sirf in namon ko dhoondenge
VIP_TAGS = [
    "crichd", "webcric", "smartcric", "willow", "astro cricket", 
    "star sports", "ptv sports", "ten sports", "sky sports cricket"
]

def get_vip_streams():
    found_channels = []
    seen_urls = set()
    
    print("🕵️‍♂️ Jasoosi shuru kar raha hoon...")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}

    for url in SOURCES:
        try:
            print(f"📡 Scanning Source: {url.split('/')[-1]}...")
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code != 200: continue
            
            lines = response.text.splitlines()
            current_name = ""
            current_logo = ""

            for line in lines:
                line = line.strip()
                if line.startswith("#EXTINF:"):
                    # Name safayi
                    raw_name = line.split(",")[-1].strip()
                    logo_match = re.search(r'tvg-logo="([^"]+)"', line)
                    current_logo = logo_match.group(1) if logo_match else ""
                    current_name = raw_name
                    
                elif line.startswith("http") and current_name:
                    # ✅ MAGIC FILTER: Kya ye WebCric/CricHD wala channel hai?
                    is_vip = any(tag in current_name.lower() for tag in VIP_TAGS)
                    
                    if is_vip and line not in seen_urls:
                        # Logo Fallback
                        if not current_logo:
                            current_logo = "https://i.imgur.com/9O0jF1m.png" # Cricket Generic Logo

                        found_channels.append({
                            "id": f"vip-{len(found_channels)+1}",
                            "name": current_name.replace("24/7", "").strip(), # Naam saaf kiya
                            "logo": current_logo,
                            "url": line,
                            "group": "VIP Cricket"
                        })
                        seen_urls.add(line)
                    current_name = ""
        except Exception as e:
            print(f"⚠️ Error: {e}")
            
    return found_channels

def main():
    channels = get_vip_streams()
    
    if not channels:
        print("❌ Kuch nahi mila. Internet check karein.")
        return

    # JSON Structure waisa hi rakha hai jaisa App.tsx ko pasand hai
    output = {
        "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %I:%M:%S %p"),
        "channels": channels # Key change ki hai taake App.tsx asani se padhe
    }

    with open('vip_cricket.json', 'w') as f:
        json.dump(output, f, indent=4)
    
    print(f"\n✅ BOOM! {len(channels)} VIP Cricket Links hack kar liye!")
    print(f"📁 File saved as: vip_cricket.json")

if __name__ == "__main__":
    main()