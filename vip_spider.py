import requests
import json

OUTPUT_FILE = 'sultan_cricket.json'

def sultan_ultimate_json_hunter():
    print("="*60)
    print(" 👑 DAR TV SULTAN v5.3 - LOGO & DRM CATCHER ")
    print("="*60)

    target_json = "https://raw.githubusercontent.com/vaathala00/jow/main/output.json"

    try:
        print(f"⏳ Fetching ultimate JSON from: {target_json}...")
        response = requests.get(target_json, timeout=10)
        data = response.json()

        vip_channels = []

        for item in data:
            # 1. Naam aur Link nikalna
            name = item.get('name', 'Unknown Channel')
            url = item.get('link', '') or item.get('url', '')
            
            # 2. 🎨 LOGO Nikalna (JSON mein logo ya icon ke naam se ho sakta hai)
            logo = item.get('logo', '') or item.get('icon', '') or item.get('tvg-logo', '')
            
            # 3. 🔐 DRM KEYS Nikalna (Agar Tata Play / Jio ka link hua to chabi zaroor hogi)
            clearkey = item.get('clearkey', '') or item.get('key', '')
            license_url = item.get('license_url', '') or item.get('license', '')
            
            if url:
                # Agar MPD hai ya koi key mojood hai to iska matlab DRM protected hai
                is_drm = '.mpd' in url or bool(clearkey) or bool(license_url)
                
                channel_data = {
                    "name": name,
                    "url": url,
                    "logo": logo,  # 🎨 Yahan humne Logo daal diya
                    "category": "Premium Network",
                    "is_drm": is_drm,
                    "type": "DRM" if is_drm else "HLS"
                }
                
                # Agar chabi mili to usay bhi sath bhej do
                if clearkey:
                    channel_data["clearkey"] = clearkey
                if license_url:
                    channel_data["license_url"] = license_url

                vip_channels.append(channel_data)

        if vip_channels:
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(vip_channels, f, indent=4)
            print(f"\n🔥 MUBARAK! {len(vip_channels)} Channels (With LOGO & DRM) '{OUTPUT_FILE}' mein save ho gaye!")
        else:
            print("\n❌ JSON mil gaya par andar links nahi thay.")

    except Exception as e:
        print(f"❌ Error fetching JSON: {e}")

if __name__ == "__main__":
    sultan_ultimate_json_hunter()