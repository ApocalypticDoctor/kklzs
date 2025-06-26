import io
import json
import os
import threading
import time
import zipfile
from multiprocessing import current_process

import requests
if current_process().name == "MainProcess":
    with open("../template/data.json", "r", encoding="utf-8") as f:
        version_now = json.load(f)["version"]

    version_url = "https://raw.githubusercontent.com/ApocalypticDoctor/kklzs/refs/heads/master/template/data.json"
    repo_url = "https://codeload.github.com/ApocalypticDoctor/kklzs/zip/refs/heads/master"
    try:
        version_new = requests.get(version_url, timeout=3).json()["version"]
    except:
        try:
            version_url = "https://gitee.com/cobic/kklzs/raw/master/template/data.json"
            version_new = requests.get(version_url, timeout=3).json()["version"]
        except:
            version_new = version_now
percent = 0
last = 0
def update(progress_callback):
    global percent, last
    def load():
        global percent, last
        t = time.time()
        while percent <= 36:
            percent = int((time.time() - t) ** 2)
            if percent != last:
                last = percent
                progress_callback(percent)

    threading.Thread(target=load).start()
    response = requests.get(repo_url, timeout=1)
    total_size = len(response.content) - 26390760 - 187798
    downloaded_size = 0
    with (zipfile.ZipFile(io.BytesIO(response.content)) as zip_file):
        for file_info in zip_file.infolist():
            if (file_info.filename.startswith('kklzs-master/background/') or
                file_info.filename.startswith('kklzs-master/template/')) and \
                not file_info.filename.endswith('.exe') and not file_info.filename.endswith('.ttf'):

                target_path = os.path.join('../', os.path.relpath(file_info.filename, 'kklzs-master'))

                if file_info.is_dir():
                    os.makedirs(target_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with zip_file.open(file_info) as src, open(target_path, 'wb') as dst:
                        chunk_size = 8192
                        while True:
                            chunk = src.read(chunk_size)
                            if not chunk:
                                break
                            dst.write(chunk)
                            downloaded_size += len(chunk)
                            if 36 <= int((downloaded_size / total_size) * 100) != last:
                                last = int((downloaded_size / total_size) * 100)
                                progress_callback(percent)
                                time.sleep(0.02)
