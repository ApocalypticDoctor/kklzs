import ctypes
import json
import os
import shutil
import subprocess
import sys
import time

import requests
from git import Repo

with open("../template/data.json", "r", encoding="utf-8") as f:
    version_now = json.load(f)["version"]

version_url = "https://raw.githubusercontent.com/ApocalypticDoctor/kklzs/refs/heads/master/template/data.json"
repo_url = "https://github.com/ApocalypticDoctor/kklzs.git"
try:
    version_new = requests.get(version_url, timeout=3).json()["version"]
except:
    version_url = "https://gitee.com/cobic/kklzs/raw/master/template/data.json"
    repo_url = "https://gitee.com/cobic/kklzs.git"
    try:
        version_new = requests.get(version_url, timeout=3).json()["version"]
    except:
        version_new = version_now

def update():
    local_repo_path = "../temp"  # 临时目录用于存放更新后的代码

    # 删除旧的临时目录（如果存在）
    if os.path.exists(local_repo_path):
        os.system("rd /s /q ..\\temp")

    Repo.clone_from(repo_url, local_repo_path, depth=1)
    # # 遍历更新目录中的文件，复制到项目根目录
    for item in os.listdir(local_repo_path):
        src_path = os.path.join(local_repo_path, item)
        dst_path = os.path.join("../", item)

        # 如果目标是目录，则递归删除再复制
        if os.path.isdir(src_path):
            if os.path.exists(dst_path):
                shutil.rmtree(dst_path)
            shutil.copytree(src_path, dst_path)
        else:
            # 如果是文件则直接覆盖
            if os.path.exists(dst_path):
                os.remove(dst_path)
            shutil.copy2(src_path, dst_path)
    os.system("rd /s /q ..\\temp")  # 清理临时目录
    sys.exit(0)