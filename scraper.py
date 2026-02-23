import requests
import re
import json

def generate_vast_json_playlist():
    # IPTV ke sabse bade sources
    sources = [
        "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/in.m3u",
        "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/pk.m3u",
        "https://raw.githubusercontent.com/billythekids/free-iptv/main/lists/india.m3u",
        "https://raw.githubusercontent.com/paimon-moe/iptv/main/india.m3u"
    ]
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    print("\n" + "="*50)
    print(" 🚀 VAST SEARCH SHURU HO RAHI HAI ")
    print("="*50)
    
    channels_data = []
    total_scanned = 0
    
    # Categories ke liye keywords
    keywords = {
        "Sports": ["SPORTS", "CRICKET", "TEN 1", "TEN 2", "TEN 3", "SONY TEN", "STAR SPORTS", "WILLOW", "PTV SPORTS", "GEO SUPER", "A SPORTS"],
        "Pakistani Drama": ["ARY", "HUM TV", "GEO ENTERTAINMENT", "PTV HOME", "A-PLUS", "BOL ENTERTAINMENT", "EXPRESS", "LTN"],
        "Indian Drama": ["STAR PLUS", "COLORS", "ZEE TV", "SONY ENTERTAINMENT", "SAB TV", "STAR BHARAT", "DANGAL", "ANDTV", "BINDASS"],
        "Movies": ["MOVIES", "CINEMA", "MAX", "GOLD", "PICTURES", "B4U", "ACTION", "FILMY", "STAR MOVIES", "ZEE CINEMA", "UTV", "HBO", "HOLLYWOOD"]
    }

    for url in sources:
        print(f"\n⏳ Scanning Database: {url[:45]}...")
        try:
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                content = response.text
                matches = re.findall(r'#EXTINF:.*?,(.*?)\n(http.*)', content)
                
                for name, link in matches:
                    total_scanned += 1
                    channel_name = name.strip().upper()
                    matched_category = None
                    
                    # Check karna ke channel kis category mein aata hai
                    for cat, words in keywords.items():
                        if any(w in channel_name for w in words):
                            matched_category = cat
                            break
                    
                    # Agar channel hamari kisi category ka hai
                    if matched_category:
                        channel_info = {
                            "name": channel_name,
                            "url": link.strip(),
                            "category": matched_category,
                            "status": "active"
                        }
                        
                        # Duplicate links check karne ka logic
                        if not any(c['url'] == link.strip() for c in channels_data):
                            channels_data.append(channel_info)
                            print(f"✅ Found [{matched_category}]: {channel_name}")
                            
        except Exception as e:
            print(f"❌ Error: {e}")

    # --- SEARCH COMPLETE SUMMARY ---
    print("\n" + "="*50)
    print(" 📊 SEARCH MUKAMMAL HO GAYI!")
    print(f" 🔍 Total Links Check Kiye: {total_scanned}")
    print(f" 🎉 Kaam ke Channels Mile: {len(channels_data)}")
    print("="*50)

    # --- JSON FILE BANANA ---
    if len(channels_data) > 0:
        print("\n⏳ Ab JSON file ban rahi hai...")
        with open('dartv_vast_channels.json', 'w', encoding='utf-8') as json_file:
            json.dump(channels_data, json_file, indent=4)
        print("🎉 Kamyabi! Aapke channels 'dartv_vast_channels.json' file mein save ho gaye hain.")
    else:
        print("⚠️ Afsos, is waqt koi channel match nahi hua.")

if __name__ == "__main__":
    generate_vast_json_playlist()