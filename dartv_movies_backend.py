import requests
import json
import re

# TVMaze ki description mein HTML tags hote hain (<p>, <b>), unhein saaf karne ke liye
def clean_html(raw_html):
    if not raw_html:
        return "No description available."
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html)

def fetch_unstoppable_vods():
    print("[*] 🎬 DarTV VOD Engine Started...")
    print("[*] Connecting to Open TVMaze Database (100% Unblocked)...")
    
    # Humari pasandeeda searches
    search_queries = ["marvel", "batman", "avengers", "star wars", "vikings", "matrix", "spider", "superman", "game of thrones"]
    vod_list = []
    seen_ids = set()
    
    for query in search_queries:
        print(f"[*] Fetching '{query.upper()}' titles...")
        # TVMaze Open Search API
        url = f"https://api.tvmaze.com/search/shows?q={query}"
        
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                results = r.json()
                
                if not results:
                    print(f"    [-] No results for {query}")
                
                for item in results:
                    show = item.get("show", {})
                    show_id = show.get("id")
                    
                    # Duplicate rokne ke liye
                    if not show_id or show_id in seen_ids:
                        continue
                    seen_ids.add(show_id)
                    
                    title = show.get("name", "Unknown Title")
                    
                    # Year (Sirf pehle 4 characters)
                    premiered = show.get("premiered", "")
                    year = premiered[:4] if premiered else "N/A"
                    
                    # Rating
                    rating = show.get("rating", {}).get("average")
                    rating_str = str(rating) if rating else "HD"
                    
                    # Genres
                    genres = show.get("genres", ["Entertainment"])
                    main_genre = genres[0] if genres else "Action"
                    
                    # Clean Description
                    raw_desc = show.get("summary", "")
                    desc = clean_html(raw_desc)
                    if len(desc) > 150:
                        desc = desc[:147] + "..."
                        
                    # HD Poster (Original size)
                    image_data = show.get("image")
                    poster = image_data.get("original") if image_data else f"https://ui-avatars.com/api/?name={title}&background=1e2024&color=00b865&size=512"
                    
                    vod_list.append({
                        "id": f"vod-tvm-{show_id}",
                        "title": title,
                        "year": year,
                        "rating": rating_str,
                        "genre": main_genre,
                        "description": desc,
                        "poster": poster,
                        "backdrop": poster,
                        # 🔥 MUX TEST HD VIDEO LINK (Isey baad mein apne links se badal lena)
                        "streamUrl": "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8",
                        "type": "Video"
                    })
            else:
                print(f"    [!] Error Status Code: {r.status_code}")
                
        except Exception as e:
            print(f"    [!] Connection Error: {e}")
            
    if vod_list:
        print(f"\n[+] BOOM! 🔥 Total {len(vod_list)} VODs HD Posters ke sath save ho gaye!")
        
        # JSON file save karna
        with open("dartv_movies.json", "w", encoding='utf-8') as f:
            json.dump(vod_list, f, indent=4, ensure_ascii=False)
            
        print("[🚀 SUCCESS] 'dartv_movies.json' is ready! Kisi ki majaal nahi jo isey rokay!")
    else:
        print("\n[!] Data fetch nahi ho saka.")

if __name__ == "__main__":
    fetch_unstoppable_vods()