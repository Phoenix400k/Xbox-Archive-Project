import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote, urljoin
import shutil

BASE_URL = "https://myrient.erista.me/files/"
OUTPUT_DIR = "Myrient_Full_Archive"

def crawl(current_url, current_path):
    try:
        response = requests.get(current_url, timeout=20)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for link in soup.find_all('a'):
            href = link.get('href')
            if not href or href.startswith('?') or href in ['../', '/']:
                continue
            
            name = unquote(href).strip('/')
            # تنظيف الاسم من الرموز التي يرفضها ويندوز
            safe_name = "".join([c if c not in '<>:"/\\|?*' else '-' for c in name])
            full_path = os.path.join(current_path, safe_name)
            new_url = urljoin(current_url, href)

            if href.endswith('/'): # إذا كان الرابط يؤدي لمجلد
                os.makedirs(full_path, exist_ok=True)
                print(f"📁 إنشاء مجلد: {safe_name}")
                crawl(new_url, full_path) # كرر العملية داخل المجلد الجديد
            else: # إذا كان ملفاً نهائياً
                file_dir = full_path.rsplit('.', 1)[0]
                os.makedirs(file_dir, exist_ok=True)
                with open(os.path.join(file_dir, "link.txt"), "w") as f:
                    f.write(new_url)
    except:
        pass

if __name__ == "__main__":
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    crawl(BASE_URL, OUTPUT_DIR)
    shutil.make_archive("Myrient_Complete_Backup", 'zip', OUTPUT_DIR)
