import subprocess

# 🚀 Aapki saari 6 files ki list yahan aagayi hai
scripts_to_run = [
    "fetch_jio.py",
    "fetch_live_spider.py",
    "fetch_vip_cricket.py",
    "scraper.py",
    "vip_spider.py",
    "fetch_cricket.py"
]

print("🚀 Starting DarTV Master Fetcher...\n")

for script in scripts_to_run:
    print(f"▶️ Running {script}...")
    try:
        # Yeh line har script ko terminal ki tarah run karegi
        subprocess.run(["python", script], check=True)
        print(f"✅ Successfully finished {script}\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running {script}: {e}\n")
    except FileNotFoundError:
        print(f"⚠️ File nahi mili: {script}. Naam check karein!\n")

print("🎉 All scripts executed successfully!")
