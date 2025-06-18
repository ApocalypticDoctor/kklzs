import io
import json
import os
import sys
import zipfile

import requests

with open("../template/data.json", "r", encoding="utf-8") as f:
    version_now = json.load(f)["version"]

version_url = "https://raw.githubusercontent.com/ApocalypticDoctor/kklzs/refs/heads/master/template/data.json"
repo_url = "https://codeload.github.com/ApocalypticDoctor/kklzs/zip/refs/heads/master"
try:
    version_new = requests.get(version_url, timeout=5).json()["version"]
except:
    version_new = version_now

def update():
    response = requests.get(repo_url, timeout=10)
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
        for file_info in zip_file.infolist():
            # 只处理 background 和 template 文件夹及其子文件
            if file_info.filename.startswith('kklzs-master/background/') or \
                    file_info.filename.startswith('kklzs-master/template/'):
                # 去掉最外层的 kklzs-master/
                target_path = os.path.join('../', os.path.relpath(file_info.filename, 'kklzs-master'))

                if file_info.is_dir():
                    os.makedirs(target_path, exist_ok=True)
                else:
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with open(target_path, 'wb') as f:
                        f.write(zip_file.read(file_info.filename))
    sys.exit(0)
