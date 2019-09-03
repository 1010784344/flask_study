# -*- coding: UTF-8 -*-
from datetime import datetime
from apps import db


class User(db.Model):
    # 指定表名
    __tablename__ = 'user'
    # __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    pwd = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    face = db.Column(db.String(120), nullable=False)
    desc = db.Column(db.TEXT)
    # 下面这2个不用放表单进行提交，系统自动分配
    uuid = db.Column(db.String(120), nullable=False)
    addtime = db.Column(db.DATETIME, default=datetime.now)


    #规定查询之后的信息呈现
    def __repr__(self):
        return '<User %r>' % self.name


    def check_pwd(self,pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd,pwd)

if __name__ == '__main__':
    db.drop_all()
    db.create_all()






















