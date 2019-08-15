# -*- coding: UTF-8 -*-
# 工具模块
import os
def create_folder(folderpath):
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
        os.chmod(folderpath,os.O_RDWR)