import os
import sys
import requests
from bs4 import BeautifulSoup
import zipfile
import tarfile
import gzip
import shutil

URL = "https://stockfishchess.org/download/"
DOWNLOAD_DIR = "./engine/"

def get_os_type():
    if sys.platform.startswith('win'):
        return 'windows'
    elif sys.platform.startswith('linux'):
        return 'ubuntu'
    elif sys.platform.startswith('darwin'):
        return 'mac'
    else:
        return 'unknown'


def get_cpu_features():
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
        
        features = []
        if 'avx2' in cpuinfo.lower():
            features.append('avx2')
        if 'bmi2' in cpuinfo.lower():
            features.append('bmi2')
        if 'sse4' in cpuinfo.lower() or 'sse4_1' in cpuinfo.lower():
            features.append('sse41')
        
        return features if features else ['modern', 'default']
    except:
        return ['modern', 'default']


def extract_file(filepath, download_dir):
    try:
        if filepath.endswith('.zip'):
            with zipfile.ZipFile(filepath, 'r') as zip_ref:
                zip_ref.extractall(download_dir)
            print("Zip file extracted.")
        elif filepath.endswith('.tar.gz') or filepath.endswith('.tgz'):
            with tarfile.open(filepath, 'r:gz') as tar_ref:
                tar_ref.extractall(download_dir)
            print("Tar.gz file extracted.")
        elif filepath.endswith('.tar'):
            with tarfile.open(filepath, 'r:') as tar_ref:
                tar_ref.extractall(download_dir)
            print("Tar file extracted.")
        elif filepath.endswith('.gz'):
            filename = os.path.basename(filepath)
            output_path = os.path.join(download_dir, filename[:-3])
            with gzip.open(filepath, 'rb') as f_in:
                with open(output_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            print("Gzip file extracted.")
        else:
            print(f"Unknown compression format for file: {filepath}")
            return False
        return True
    except Exception as e:
        print(f"Error extracting {filepath}: {str(e)}")
        return False

def main():
    if not os.path.isdir(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    
    current_os = get_os_type()
    cpu_features = get_cpu_features()
    
    print(f"Detected OS: {current_os}")
    print(f"CPU Features: {', '.join(cpu_features)}")
    
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, "html.parser")
    items = soup.find_all("div", class_="download-item")
    
    for item in items:
        item_text = item.get_text()
        print("Checking:", item_text)
        print(cpu_features[0].upper())
        if "64-bit" in item_text:
            link_tag = item.find("a", class_="button-download")
            if link_tag and link_tag["href"]:
                download_url = link_tag["href"]
                print("Matching download link found:", download_url)
                print(download_url)
                if current_os in download_url:

                    filename = download_url.split("/")[-1]
                    filepath = os.path.join(DOWNLOAD_DIR, filename)

                    file_data = requests.get(download_url).content
                    with open(filepath, "wb") as f:
                        f.write(file_data)
                    print(f"File saved to {filepath}")

                    extract_file(filepath, DOWNLOAD_DIR)
                    
                    if os.path.exists(filepath):
                        os.remove(filepath)
                        print("Archive removed.")
                    return
                else:
                    pass

    print(f"Could not find AVX2 download for {current_os}.")

if __name__ == "__main__":
    main()
    print("Done")