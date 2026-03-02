import os, requests, shutil
from bs4 import BeautifulSoup
from urllib.parse import unquote, urljoin

# الإعدادات
BASE_URL = "https://myrient.erista.me/files/"
OUTPUT_DIR = "Myrient_Full_Archive"
PROGRESS_FILE = "progress.txt"

def get_last_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def save_progress(url):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        f.write(url)

def crawl(current_url, current_path, last_progress, found_resume_point):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(current_url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for link in soup.find_all('a'):
            href = link.get('href')
            if not href or href.startswith('?') or href in ['../', '/']:
                continue
            
            new_url = urljoin(current_url, href)
            
            # نظام التخطي للاستكمال
            if last_progress and not found_resume_point:
                if last_progress == new_url:
                    found_resume_point = True
                    print(f"✨ تم العثور على نقطة التوقف: {new_url}")
                continue

            name = unquote(href).strip('/')
            safe_name = "".join([c if c not in '<>:"/\\|?*' else '-' for c in name])
            full_path = os.path.join(current_path, safe_name)

            if href.endswith('/'):
                os.makedirs(full_path, exist_ok=True)
                print(f"📁 أرشفة: {safe_name}")
                save_progress(new_url) 
                found_resume_point = crawl(new_url, full_path, last_progress, found_resume_point)
            else:
                file_dir = full_path.rsplit('.', 1)[0]
                os.makedirs(file_dir, exist_ok=True)
                with open(os.path.join(file_dir, "download_link.txt"), "w", encoding="utf-8") as f:
                    f.write(new_url)
        return found_resume_point
    except Exception as e:
        print(f"⚠️ خطأ: {e}")
        return found_resume_point

if __name__ == "__main__":
    last_p = get_last_progress()
    found_p = False if last_p else True
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    print(f"🚀 البدء من: {last_p if last_p else 'البداية'}")
    crawl(BASE_URL, OUTPUT_DIR, last_p, found_p)
    
    print("📦 ضغط الملفات...")
    shutil.make_archive("Myrient_Complete_Backup", 'zip', OUTPUT_DIR)
