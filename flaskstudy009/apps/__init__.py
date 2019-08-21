# -*- coding: utf-8 -*-
import os
from flask import Flask
from apps.utils import create_folder
app = Flask(__name__)


# 设置上传文件限制
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 拼凑数据库的目录，只不过之前都是写的绝对路径
APPS_DIR = os.path.dirname(__file__)
app.config['DATABASE'] = os.path.join(APPS_DIR,'database.db')

#拼凑用户头像保存路径()
STATIC_DIR = os.path.join(APPS_DIR,'static')
app.config['UPLOADS_DIR_ALT'] = 'uploads'
app.config['UPLOADS_DIR'] = os.path.join(STATIC_DIR,app.config['UPLOADS_DIR_ALT'])

# 如果不存在，就创建，并修改可读可写的权限
create_folder(app.config['UPLOADS_DIR'])


# 第一步配置上传文件保存地址
app.config['UPLOADED_PHOTOS_DEST'] = app.config['UPLOADS_DIR']


app.config['SECRET_KEY'] = r'de lu da shu 666'


# 避免循环导入
from apps import views






