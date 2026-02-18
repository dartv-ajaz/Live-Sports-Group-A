import requests
import json
from datetime import datetime
import pytz

def main():
    # Aapki nikali hui asli link
    real_link = "https://in-mc-flive.fancode.com/mumbai/140658_english_hls_8dec9cc28f58754_1ta-di_h264/index.m3u8?hdnea=exp=1771434811~acl=/mumbai/140658_english_hls_8dec9cc28f58754_1ta-di_h264/*~id=80643612_401f0395-5bcf-49~data=80643612~hmac=954d0ca861135b098277e0056026a44ec3153396a49c75815ae5cc6cde4dea2f&deviceId=undefined&advertiserId=undefined"

    matches = []
    
    # 1. Jo link aapne pakdi hai, usay add karte hain
    matches.append({
        "id": "manual-140658",
        "platform": "FanCode LIVE",
        "sport": "Cricket",
        "title": "LIVE: Captured Match (Testing)",
        "team_1": "Live",
        "team_2": "Stream",
        "url": real_link,
        "type": "HLS",
        "is_drm": False
    })

    # Output file banana
    output = {
        "updated_at": datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %I:%M:%S %p"),
        "matches": matches
    }

    with open('live_matches_A.json', 'w') as f:
        json.dump(output, f, indent=4)
    
    print("✅ Asli link save ho gayi hai! Ab Git Push karein.")

if __name__ == "__main__":
    main()