import os, requests, shutil, re
from bs4 import BeautifulSoup
from urllib.parse import unquote, urljoin

# الإعدادات
BASE_URL = "https://myrient.erista.me/files/"
OUTPUT_DIR = "Myrient_Full_Archive"
PROGRESS_FILE = "progress.txt"

def save_progress(url):
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        f.write(url)

def get_last_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    return None

def crawl(current_url, current_path, last_progress, found_resume_point):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(current_url, headers=headers, timeout=30)
        if response.status_code != 200: return found_resume_point
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for link in soup.find_all('a'):
            href = link.get('href')
            
            # 1. فلتر الروابط المزعجة والدائرية
            if not href or href.startswith(('?', '..', '/')) or 'http' in href: continue
            
            # 2. تجاهل الكلمات التقنية والقانونية ليركز على الألعاب
            bad_patterns = ['contact', 'disclaimer', 'faq', 'donate', 'erista', 'romvault', 'datvault', 'dokuwiki', 'discord']
            if any(word in href.lower() for word in bad_patterns): continue
            
            new_url = urljoin(current_url, href)
            
            # 3. نظام الاستكمال (Resume)
            if last_progress and not found_resume_point:
                if last_progress == new_url:
                    found_resume_point = True
                    print(f"✨ تم العثور على نقطة التوقف: {new_url}")
                continue

            # 4. تنظيف الاسم من الرموز الممنوعة
            name = unquote(href).strip('/')
            safe_name = re.sub(r'[<>:"/\\|?*]', '-', name)[:100] # تقصير الاسم لحماية النظام
            full_path = os.path.join(current_path, safe_name)

            if href.endswith('/'):
                # منع التكرار اللانهائي (مجلد داخل نفسه)
                if safe_name.lower() in current_path.lower().split(os.sep): continue
                
                # منع المسارات الطويلة جداً (أقصى حد 200 حرف)
                if len(full_path) > 200: continue

                os.makedirs(full_path, exist_ok=True)
                print(f"🎮 أرشيف: {safe_name}")
                save_progress(new_url) 
                found_resume_point = crawl(new_url, full_path, last_progress, found_resume_point)
            else:
                # حفظ الرابط في ملف نصي
                os.makedirs(full_path, exist_ok=True)
                with open(os.path.join(full_path, "link.txt"), "w", encoding="utf-8") as f:
                    f.write(new_url)
                    
        return found_resume_point
    except Exception as e:
        print(f"⚠️ تخطي خطأ بسيط: {e}")
        return found_resume_point

if __name__ == "__main__":
    last_p = get_last_progress()
    found_p = False if last_p else True
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    print(f"🚀 المحرك يعمل... البدء من: {last_p if last_p else 'البداية'}")
    crawl(BASE_URL, OUTPUT_DIR, last_p, found_p)
    
    print("📦 جاري ضغط البيانات المجمعة...")
    shutil.make_archive("Myrient_Complete_Backup", 'zip', OUTPUT_DIR)
