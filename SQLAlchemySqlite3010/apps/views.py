# -*- coding: utf-8 -*-
# 视图函数存放,views 只负责带有路由装饰器的视图
import os
import shutil
# 协助定义装饰器
from functools import wraps

from flask import render_template,request

from apps import app



@app.route('/')
def index():
    # 全部查询
    return render_template('index.html')




