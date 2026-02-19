import subprocess
import os

# Yahan un sab files ke naam likhein jo aap chalana chahte hain
SCRIPTS = [
    "fetch_jio.py",
    "fetch_cricket.py",
    "fetch_vip_cricket.py",      # Agar aapne hybrid wala save kiya hai
    "fetch_indo_pak.py",         # Agar Indo-Pak wala save kiya hai
    "fetch_live_spider.py"       # Agar Spider wala save kiya hai
]

def run_all_fetchers():
    print("🚀 Auto-Update Protocol Started...")
    
    for script in SCRIPTS:
        # Check karein ke file exist karti hai ya nahi
        if os.path.exists(script):
            print(f"\n------------------------------------------")
            print(f"📡 Running: {script}")
            print(f"------------------------------------------")
            try:
                # Yeh line doosri python file ko chalati hai
                subprocess.run(["python", script], check=True)
                print(f"✅ Success: {script} completed.")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error: {script} failed (Code {e.returncode})")
            except Exception as e:
                print(f"⚠️ Unexpected Error: {e}")
        else:
            print(f"⚠️ Warning: {script} file nahi mili (Skipping...)")

    print("\n🎉 All Fetchers Finished! Data Updated.")

if __name__ == "__main__":
    run_all_fetchers()
