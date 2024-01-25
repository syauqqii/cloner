import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, unquote

# ======= START - CONFIGURATION =======
"""
    SETTING NAMA FOLDER UNTUK SETIAP FILE
"""
FOLDER_AUDIO = "audio"
FOLDER_CSS = "css"
FOLDER_GIF = "gif"
FOLDER_IMG = "img"
FOLDER_JS  = "js"
FOLDER_SVG = "svg"
FOLDER_VIDEO = "video"

"""
    TAMBAHKAN KEYWORD YANG TIDAK INGIN DIAMBIL FILENYA,
    MISALNYA :
        FILE YANG TERDAPAT '=' MAKA TIDAK DI SIMPAN.
"""
KEYWORDS = ['=']

# LINE: 72 (START - END)
CUSTOM_OPERATION = False # True / False, DEFAULT: False
EXCEPTION_EXTENSION = ['.blablabla'] # Change blablabla to bebas terserah kamuh
#   ======= END - CONFIGURATION =======

def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def clean_filename(url):
    url = unquote(url)

    filename = os.path.basename(urlparse(url).path)
    valid_characters = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_.")
    
    cleaned_filename = ''.join(char if char in valid_characters else '_' for char in filename)
    cleaned_filename = '_'.join(part for part in cleaned_filename.split('_') if part)

    if '.' in cleaned_filename and cleaned_filename.rsplit('.', 1)[-1].lower() in ['jpg', 'jpeg', 'png', 'gif', 'svg', 'mp4', 'webm', 'css', 'js', 'json']:
        return cleaned_filename

    if not cleaned_filename.endswith('.'):
        cleaned_filename += '.' + filename.split('.')[-1].lower()

    return cleaned_filename

def save_files(folder, files):
    global SKIP_E, SKIP_D, BERHASIL, GAGAL, KEYWORDS, EXCEPTION_EXTENSION

    if not os.path.exists(folder):
        os.makedirs(folder)

    for idx, file_url in enumerate(files, start=1):
        if any(keyword in file_url for keyword in KEYWORDS):
            print(f' > SKIP : {file_url} => ["="]')
            SKIP_E  += 1
            continue

        response = requests.get(file_url)

        if response.status_code == 200:
            file_content = response.content
            cleaned_filename = clean_filename(file_url)

            # === START CUSTOM OPERATION ===
            if CUSTOM_OPERATION:
                if cleaned_filename.endswith(tuple(EXCEPTION_EXTENSION)):
                    cleaned_filename = ' '.join(cleaned_filename.split('_')[1:])
            #  === END CUSTOM OPERATION ===

            file_path = os.path.join(folder, cleaned_filename)

            if os.path.exists(file_path):
                print(f' > SKIP : {file_path} => SUDAH ADA')
                SKIP_D += 1
                continue

            with open(file_path, 'wb') as file:
                file.write(file_content)
            
            print(f' > SAVE : {file_path}')
            BERHASIL += 1
        else:
            print(f' > DROP : {file_url} | ERROR CODE: {response.status_code}')
            GAGAL  += 1

def main():
    try:
        global SKIP_E, SKIP_D, BERHASIL, GAGAL, FOLDER_CSS, FOLDER_IMG, FOLDER_SVG, FOLDER_JS, FOLDER_AUDIO, FOLDER_VIDEO

        os.system("cls||clear")

        URL = input("\n # Masukkan URL: ")

        if not is_valid_url(URL):
            print("\n > ERROR: URL tidak valid!")
            exit(1)

        resp = requests.get(URL)

        if resp.status_code != 200:
            print("\n > ERROR: URL tidak dapat diakses!")
            exit(1)

        html = resp.text
        soup = BeautifulSoup(html, 'html.parser')

        with open(f'index.html', 'w', encoding='utf-8') as file:
            file.write(soup.prettify())

        # GET audioh
        audio_files = [urljoin(URL, audio['src']) for audio in soup.find_all('audio', {'src': True})]

        # GET css
        css_files = [urljoin(URL, link['href']) for link in soup.find_all('link', {'rel': 'stylesheet'})]

        # GET js
        javascript_files = [urljoin(URL, script['src']) for script in soup.find_all('script', {'src': True})]

        # GET img
        image_files = [urljoin(URL, img['src']) for img in soup.find_all('img', {'src': True})]
        img_files = [file for file in image_files if not file.lower().endswith(('.svg', '.gif'))]
        svg_files = [file for file in image_files if file.lower().endswith('.svg')]
        gif_files = [file for file in image_files if file.lower().endswith('.gif')]

        # GET videoh
        video_files = [urljoin(URL, video['src']) for video in soup.find_all('video', {'src': True})]

        print()

        if audio_files:
            save_files(FOLDER_AUDIO, audio_files)

        if css_files:
            save_files(FOLDER_CSS, css_files)

        if javascript_files:
            save_files(FOLDER_JS, javascript_files)

        if gif_files:
            save_files(FOLDER_GIF, gif_files)

        if img_files:
            save_files(FOLDER_IMG, img_files)

        if svg_files:
            save_files(FOLDER_SVG, svg_files)

        if video_files:
            save_files(FOLDER_VIDEO, video_files)

        print(f"\n # TOTAL FILE [{BERHASIL+GAGAL+SKIP_E+SKIP_D}]")
        print(f"   - BERHASIL: {BERHASIL}")
        print(f"   - GAGAL   : {GAGAL}")
        print("   - SKIP {")
        print(f"      - EXCLUDING KEYWORD : {SKIP_E}")
        print(f"      - DUPLICATED        : {SKIP_D}")
        print("     }")
        print("   - HASIL {")
        if audio_files:
            print(f"      - AUDIO : {len(list(set(audio_files)))} file")
        if css_files:
            print(f"      - CSS   : {len(list(set(css_files)))} file")
        if javascript_files:
            print(f"      - JS    : {len(list(set(javascript_files)))} file")
        if gif_files:
            print(f"      - GIF   : {len(list(set(gif_files)))} file")
        if img_files:
            print(f"      - IMG   : {len(list(set(img_files)))} file")
        if svg_files:
            print(f"      - SVG   : {len(list(set(svg_files)))} file")
        if video_files:
            print(f"      - VIDEO : {len(list(set(video_files)))} file")
        print("     }")

    except KeyboardInterrupt:
        print()
        exit(1)
    except:
        print("\n > ERROR: URL tidak dapat diakses!")
        exit(1)

if __name__ == '__main__':
    BERHASIL = 0
    SKIP_D   = 0
    SKIP_E   = 0
    GAGAL    = 0

    main()
