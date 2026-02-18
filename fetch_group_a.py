import requests
import json
from datetime import datetime
import pytz

def get_live_now_fancode():
    # Aap ki captured query aur exact parameters use ho rahe hain
    print("🚀 Running Version 14 (Fixed): Using Captured Network Query...")
    url = "https://www.fancode.com/graphql"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json"
    }

    payload = {
        "operationName": "HomePageLiveNowMatches",
        "variables": {
            "filter": {
                "collectionId": 19195735,
                "segmentId": 47026,
                "countryId": 7378
            }
        },
        "query": """
        query HomePageLiveNowMatches($filter: CasaMatchesFilter!) {
          homePageLiveNowMatches(filter: $filter) {
            edges {
              id
              match {
                id
                name
                sport { name }
              }
              features {
                matchId
                isPremium
              }
            }
          }
        }
        """
    }

    matches = []
    try:
        response = requests.post(url, json=payload, headers=headers)
        data = response.json()
        edges = data.get("data", {}).get("homePageLiveNowMatches", {}).get("edges", [])
        
        print(f"📡 Found {len(edges)} matches using Captured Query.")

        for edge in edges:
            match_obj = edge.get("match", {})
            features = edge.get("features", {})
            m_id = features.get("matchId") or match_obj.get("id")
            name = match_obj.get("name", "Live Match")
            
            if m_id:
                # Name ko saaf karna agar khali ho
                display_name = name if name.strip() else f"Match {m_id}"
                print(f"✅ Found: {display_name}")
                
                matches.append({
                    "id": m_id,
                    "platform": "FanCode LIVE",
                    "sport": match_obj.get("sport", {}).get("name", "Sport"),
                    "title": f"[LIVE] {display_name}",
                    "url": f"https://www.fancode.com/video/{m_id}",
                    "type": "HLS",
                    "is_premium": features.get("isPremium", False)
                })
    except Exception as e:
        print(f"⚠️ Error: {e}")
    
    return matches

def main():
    # Function ka naam ab bilkul sahi hai
    all_matches = get_live_now_fancode()
    
    if not all_matches:
        print("No matches found. Adding manual backup...")
        all_matches.append({
            "id": "140658",
            "platform": "FanCode Manual",
            "title": "LIVE: Boland T20 (Cricket)",
            "url": "https://www.fancode.com/video/140658",
            "type": "HLS"
        })

    output = {
        "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %I:%M:%S %p"),
        "matches": all_matches
    }

    with open('live_matches_A.json', 'w') as f:
        json.dump(output, f, indent=4)
    print("✅ live_matches_A.json updated successfully!")

if __name__ == "__main__":
    main()