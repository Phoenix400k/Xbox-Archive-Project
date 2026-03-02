import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urljoin
from tqdm import tqdm
import shutil

# الروابط المستهدفة
URLS = {
    "Games": "https://myrient.erista.me/files/Redump/Microsoft%20-%20Xbox%20360/",
    "DLC_Digital": "https://myrient.erista.me/files/No-Intro/Microsoft%20-%20Xbox%20360%20%28Digital%29/"
}

def process_section(url, target_path, label):
    print(f"\n>>> فحص القسم: {label}")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        all_links = [a for a in soup.find_all('a') if a.get('href') and not a.get('href').startswith('?') and "Parent Directory" not in a.text]
        
        with tqdm(total=len(all_links), desc=f"أرشفة {label}", unit="file") as pbar:
            for link in all_links:
                href = link.get('href')
                full_name = unquote(href).strip('/')
                game_name = "".join([c if c not in '<>:"/\\|?*' else '-' for c in full_name.rsplit('.', 1)[0]])
                game_dir = os.path.join(target_path, game_name)
                os.makedirs(game_dir, exist_ok=True)
                with open(os.path.join(game_dir, "link.txt"), "w", encoding="utf-8") as f:
                    f.write(urljoin(url, href))
                pbar.update(1)
    except Exception as e:
        print(f"❌ خطأ في {label}: {e}")

if __name__ == "__main__":
    base_folder = "Xbox_Archive"
    os.makedirs(base_folder, exist_ok=True)
    for label, url in URLS.items():
        path = os.path.join(base_folder, label)
        os.makedirs(path, exist_ok=True)
        process_section(url, path, label)
    print("\n📦 جاري ضغط الملفات...")
    shutil.make_archive("Xbox_Full_Backup", 'zip', base_folder)
    print("✅ تم الانتهاء!")
