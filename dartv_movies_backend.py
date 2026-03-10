import requests
import json
import re

def clean_html(raw_html):
    if not raw_html: return "No description available."
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html)

def fetch_iframe_movies():
    print("[*] 🎬 DarTV VOD Iframe Engine Started...")
    
    # Mix of popular Movies and Series
    search_queries = ["batman", "avengers", "spiderman", "inception", "interstellar", "top gun", "john wick", "matrix"]
    vod_list = []
    seen_ids = set()
    
    # 🔥 YE HAI ASLI JUGAD: Hum in base URLs ko use karenge movies dhoondhne ke liye
    # Note: Kuch servers ads dikhate hain, isliye iframe lock zaroori hai
    embed_base = "https://vidsrc.me/embed/movie?tmdb=" 

    for query in search_queries:
        print(f"[*] Searching '{query.upper()}' on Metadata Server...")
        # Hum TMDB ya TVMaze se pehle ID aur Info nikalenge
        url = f"https://api.tvmaze.com/search/shows?q={query}"
        
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                results = r.json()
                for item in results:
                    show = item.get("show", {})
                    name = show.get("name")
                    ext_ids = show.get("externals", {})
                    tmdb_id = ext_ids.get("thetvdb") # Using TVDB/TMDB mapping
                    
                    if not name or name in seen_ids: continue
                    seen_ids.add(name)

                    # Agar image nahi hai toh skip ya default lagao
                    image_data = show.get("image")
                    poster = image_data.get("original") if image_data else f"https://ui-avatars.com/api/?name={name}&background=00b865&color=fff"

                    # 🔥 SMART IFRAME GENERATION
                    # Yahan hum search query ko embed link mein convert kar rahe hain
                    # Taake player mein Sultan VIP ki tarah iframe khule
                    movie_slug = name.lower().replace(" ", "-")
                    
                    vod_list.append({
                        "id": f"vod-if-{show.get('id')}",
                        "title": name,
                        "year": show.get("premiered", "N/A")[:4],
                        "rating": str(show.get("rating", {}).get("average", "HD")),
                        "genre": show.get("genres")[0] if show.get("genres") else "Movie",
                        "description": clean_html(show.get("summary")),
                        "poster": poster,
                        "backdrop": poster,
                        # 🔥 YE LINK PLAYER MEIN IFRAME KHOLAY GA
                        "streamUrl": f"https://autoembed.to/movie/{movie_slug}", 
                        "type": "Iframe" 
                    })
        except Exception as e:
            print(f"[!] Error: {e}")

    if vod_list:
        with open("dartv_movies.json", "w", encoding='utf-8') as f:
            json.dump(vod_list, f, indent=4, ensure_ascii=False)
        print(f"[🚀 SUCCESS] {len(vod_list)} Iframe Movies ready in 'dartv_movies.json'!")

if __name__ == "__main__":
    fetch_iframe_movies()