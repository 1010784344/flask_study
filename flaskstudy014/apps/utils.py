# -*- coding: UTF-8 -*-
# 工具模块
import os
from datetime import datetime
import uuid
import PIL
from PIL import Image

from werkzeug.utils import secure_filename


ALLOWED_IMAGE_EXTENSIONS = set(['png','jpg','jpeg','gif','bmp'])
ALLOWED_VIDEO_EXTENSIONS = set(['mp4','avi'])
ALLOWED_AUDIO_EXTENSIONS = set(['mp3','m4a'])



def create_folder(folderpath):
    if not os.path.exists(folderpath):
        os.makedirs(folderpath)
        os.chmod(folderpath,os.O_RDWR)




#修改文件名称(时间戳+uuid)
def change_filename_with_timestamp_uuid(filename):

    fileinfo = os.path.splitext(filename)
    filename = datetime.now().strftime('%Y%m%d%H%M%S')+str(uuid.uuid4().hex)+fileinfo[-1]
    return filename

#修改文件名称(文件名安全+uuid)，避免一个文件上传多次覆盖
def secure_filename_with_uuid(filename):

    fileinfo = os.path.splitext(filename)
    filename_pre = secure_filename(fileinfo[0])

    filename = filename_pre+str(uuid.uuid4().hex)[:6]+fileinfo[-1]
    return filename

# 检测文件后缀名
def check_files_extension(filenamelist,allowed_extensions):
    for filename in filenamelist:
        if '.' in filename and filename.split('.')[1] in allowed_extensions:
            return True
        else:
            return False

# 创建缩略图
def create_thumbnail(path,filename,basewidth=300):

    imagname,ext = os.path.splitext(filename)
    newfilename = imagname + '_thumb_' + ext

    img = Image.open(os.path.join(path,filename))

    if img.size[0] > basewidth:

        # 获取百分比
        w_percent = basewidth / float(img.size[0])
        # 依据百分比修改高度
        h_size = int(float(img.size[1])*w_percent)

        img = img.resize((basewidth,h_size),PIL.Image.ANTIALIAS)

    img.save(os.path.join(path, newfilename))
    return newfilename


# 创建展示图
def create_show(path,filename,basewidth=800):

    imagname,ext = os.path.splitext(filename)
    newfilename = imagname + '_show_' + ext

    img = Image.open(os.path.join(path,filename))

    if img.size[0] < basewidth:

        # 获取百分比
        w_percent = basewidth / float(img.size[0])
        # 依据百分比修改高度
        h_size = int(float(img.size[1])*w_percent)

        img = img.resize((basewidth,h_size),PIL.Image.ANTIALIAS)

    img.save(os.path.join(path, newfilename))
    return newfilename



