# -*- coding: utf-8 -*-
import os
from flask import Flask
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flasker.db'

# TRUE 数据库里面的数据一变化，sqlalchemy 也会跟着变化
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True



# 避免循环导入
from apps import views






