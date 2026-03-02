import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urljoin
from tqdm import tqdm
import shutil
import time

BASE_URL = "https://myrient.erista.me/files/"
OUTPUT_DIR = "Myrient_Full_Archive"

def get_links(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=20)
        return BeautifulSoup(response.text, 'html.parser')
    except:
        return None

def crawl(current_url, current_path):
    soup = get_links(current_url)
    if not soup: return

    links = soup.find_all('a')
    for link in links:
        href = link.get('href')
        if not href or href.startswith('?') or href in ['../', '/']:
            continue
        
        name = unquote(href).strip('/')
        safe_name = "".join([c if c not in '<>:"/\\|?*' else '-' for c in name])
        full_path = os.path.join(current_path, safe_name)
        new_url = urljoin(current_url, href)

        if href.endswith('/'):  # إذا كان مجلد
            os.makedirs(full_path, exist_ok=True)
            crawl(new_url, full_path) # ادخل داخل المجلد
        else:  # إذا كان ملف
            file_dir = full_path.rsplit('.', 1)[0]
            os.makedirs(file_dir, exist_ok=True)
            with open(os.path.join(file_dir, "download_link.txt"), "w") as f:
                f.write(new_url)

if __name__ == "__main__":
    print("🚀 بدء أرشفة موقع Myrient بالكامل... قد يستغرق هذا وقتاً طويلاً جداً!")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    crawl(BASE_URL, OUTPUT_DIR)
    
    print("📦 جاري ضغط الأرشيف الكامل...")
    shutil.make_archive("Myrient_Complete_Backup", 'zip', OUTPUT_DIR)
    print("✅ تم الانتهاء من أرشفة كل ما تم الوصول إليه!")
