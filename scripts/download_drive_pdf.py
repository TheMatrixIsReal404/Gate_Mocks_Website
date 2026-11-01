import urllib.request
import http.cookiejar
import re
import sys

def download_file_from_google_drive(file_id, destination):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')]
    
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    resp = opener.open(url)
    content = resp.read()
    
    # Check if this is an HTML warning page
    if b'Google Drive - Virus scan warning' in content or b'download_warning' in content or b'confirm=' in content:
        html = content.decode('utf-8', errors='ignore')
        # find confirm code
        m = re.search(r'confirm=([0-9A-Za-z_]+)', html)
        confirm = m.group(1) if m else "t"
        url = f"https://drive.google.com/uc?export=download&id={file_id}&confirm={confirm}"
        print(f"Following confirmation URL: {url}")
        resp = opener.open(url)
    else:
        # It might be the file directly
        with open(destination, 'wb') as f:
            f.write(content)
        print(f"Downloaded directly: {len(content)} bytes")
        return

    CHUNK = 65536
    total = 0
    with open(destination, 'wb') as f:
        while True:
            chunk = resp.read(CHUNK)
            if not chunk:
                break
            f.write(chunk)
            total += len(chunk)
            if total % (1024 * 1024 * 5) < CHUNK:
                print(f"Downloaded {total / (1024*1024):.1f} MB...")
    print(f"Finished downloading {destination} ({total} bytes)")

if __name__ == '__main__':
    file_id = "1dKoMG8EcD7tcJPQXkvdO1ffGdbG-hq5i"
    dest = "CS_All_Old_Papers.pdf"
    print(f"Downloading {file_id} to {dest}...")
    download_file_from_google_drive(file_id, dest)
