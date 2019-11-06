# -*- coding: UTF-8 -*-
from flask import render_template,request
from apps import app

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        storages = request.files.getlist('file')
        print(storages)
        for fs in storages:
            fs.save(fs.filename)
    return render_template('index.html')
