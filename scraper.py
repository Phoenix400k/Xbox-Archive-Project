import os, requests, shutil
from bs4 import BeautifulSoup
from urllib.parse import unquote, urljoin

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

def crawl(current_url, current_path, last_progress, found_resume_point, depth=0):
    # لمنع الحلقات المفرغة (إذا زاد العمق عن 15 مستوى توقف)
    if depth > 15: return found_resume_point
    
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(current_url, headers=headers, timeout=30)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for link in soup.find_all('a'):
            href = link.get('href')
            # إضافة منع المجلدات المتكررة (مثل files/files)
            if not href or href.startswith('?') or href in ['../', '/', 'files/']:
                continue
            
            new_url = urljoin(current_url, href)
            
            if last_progress and not found_resume_point:
                if last_progress == new_url:
                    found_resume_point = True
                    print(f"✨ تم الاستئناف من: {new_url}")
                continue

            name = unquote(href).strip('/')
            safe_name = "".join([c if c not in '<>:"/\\|?*' else '-' for c in name])
            full_path = os.path.join(current_path, safe_name)

            if href.endswith('/'):
                # تأكد أن المجلد الجديد ليس تكراراً للمجلد الحالي
                if name.lower() in current_path.lower(): continue
                
                os.makedirs(full_path, exist_ok=True)
                print(f"📁 أرشفة: {safe_name}")
                save_progress(new_url) 
                found_resume_point = crawl(new_url, full_path, last_progress, found_resume_point, depth + 1)
            else:
                file_dir = full_path.rsplit('.', 1)[0]
                # تقصير المسار إذا كان طويلاً جداً
                if len(file_dir) > 150: file_dir = file_dir[:150]
                os.makedirs(file_dir, exist_ok=True)
                with open(os.path.join(file_dir, "url.txt"), "w", encoding="utf-8") as f:
                    f.write(new_url)
        return found_resume_point
    except Exception as e:
        print(f"⚠️ خطأ بسيط (تجاوز): {e}")
        return found_resume_point

if __name__ == "__main__":
    last_p = get_last_progress()
    found_p = False if last_p else True
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    crawl(BASE_URL, OUTPUT_DIR, last_p, found_p)
    shutil.make_archive("Myrient_Complete_Backup", 'zip', OUTPUT_DIR)
