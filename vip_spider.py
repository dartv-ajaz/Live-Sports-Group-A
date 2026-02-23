import requests
import json
import time

OUTPUT_FILE = 'sultan_cricket.json'

def sultan_mine_sweeper():
    print("="*60)
    print(" 👑 DAR TV SULTAN - FULL DOMAIN MINE SWEEPER ")
    print("="*60)

    # Base setup jo aapne dhunda
    base_domain = "https://lin.mokakdaoni.me/proxy/main.php/stream_"
    # In parameters ke bagair server link nahi kholega
    auth_params = "uid=3400545769&u=admin&p=40cf69bc27188df9d588e6d1b6d7a4505d3178221de98ac4d0f40af984a75444"
    
    # Ye headers stream ko "play" karne ke liye lazmi hain
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'http://livecricketsl.cc.nf/',
        'Origin': 'http://livecricketsl.cc.nf'
    }

    active_channels = []
    
    print(f"🚀 Sultan is sweeping the domain for active streams...")
    
    # 0 se 50 tak scan karte hain, aksar isi range mein channels hote hain
    for i in range(51):
        test_url = f"{base_domain}{i}.m3u8?{auth_params}"
        print(f"🕵️ Testing Channel {i}...", end="\r")
        
        try:
            # Sirf 3 second timeout taake jaldi scan ho
            # 'get' use kar rahe hain thoda data verify karne ke liye
            response = requests.get(test_url, headers=headers, timeout=5, stream=True)
            
            if response.status_code == 200:
                # Agar pehle 100 bytes mil rahe hain to matlab stream live hai
                print(f"\n💎 Found Jewel: Stream {i} is LIVE!")
                
                # IPTV App standard format: URL|Header1=Value&Header2=Value
                playable_url = f"{test_url}|User-Agent={headers['User-Agent']}&Referer={headers['Referer']}"
                
                active_channels.append({
                    "name": f"Sultan VIP {i}",
                    "url": playable_url,
                    "category": "Sultan Proxy Server",
                    "id": f"sultan_{i}"
                })
            else:
                pass # Dead link ko ignore karein
        except:
            continue
        
        time.sleep(0.2) # Server block se bachne ke liye chota sa break

    if active_channels:
        # JSON file update karna
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(active_channels, f, indent=4)
        print(f"\n🔥 MUBARAK! {len(active_channels)} Active links 'sultan_cricket.json' mein bhar diye hain.")
    else:
        print("\n❌ Koi naya link nahi mila. Check karein ke tokens expire to nahi ho gaye?")

if __name__ == "__main__":
    sultan_mine_sweeper()