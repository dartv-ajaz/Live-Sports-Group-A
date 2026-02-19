import requests
import json
from datetime import datetime
import pytz

# ---------------------------------------------------------
# 🛡️ BYPASS SOURCES (NO IP ISSUE)
# ---------------------------------------------------------
# Hum direct FanCode nahi, balki in cached sources ko use karenge
# jo already Indian IP se data scrape karke rakhte hain.
SOURCES = [
    "https://raw.githubusercontent.com/byte-capsule/FanCode-Hls-Schedule/main/fancode_schedule.json",
    "https://raw.githubusercontent.com/drm-stream/fancode-feed/main/schedule.json" # Backup Source
]

def fetch_fancode():
    print("🚀 Connecting to FanCode Bypass Servers...")
    
    for url in SOURCES:
        try:
            print(f"📡 Trying Source: {url.split('/')[3]}...")
            response = requests.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                matches = []
                
                # Data Extraction Logic
                raw_matches = data.get("matches", []) if "matches" in data else data
                
                for match in raw_matches:
                    status = match.get("status", "").upper()
                    if status in ["LIVE", "COMPLETED", "UPCOMING"]:
                        matches.append({
                            "id": str(match.get("match_id", "")),
                            "title": match.get("match_name") or match.get("title"),
                            "status": status,
                            "logo": match.get("src_banner") or "https://www.fancode.com/favicon.ico",
                            "url": match.get("stream_url") or match.get("url"),
                            "is_drm": False,
                            "platform": "FanCode"
                        })
                
                if len(matches) > 0:
                    print(f"✅ Success! Found {len(matches)} matches from {url.split('/')[3]}")
                    return matches
            else:
                print(f"❌ Source failed (Status {response.status_code})")
                
        except Exception as e:
            print(f"⚠️ Error with source: {e}")
            continue

    return []

def main():
    matches = fetch_fancode()
    
    # Empty Check: Agar list khali hai toh purani file delete mat karna
    if not matches:
        print("⚠️ Warning: Koi match nahi mila. Shayad Sources down hain.")
        # Hum file overwrite nahi karenge taake purana data bacha rahe
        return

    output = {
        "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %I:%M:%S %p"),
        "total_matches": len(matches),
        "matches": matches
    }

    with open('live_matches_A.json', 'w') as f:
        json.dump(output, f, indent=4)
    
    print(f"💾 Saved to 'live_matches_A.json'")

if __name__ == "__main__":
    main()
