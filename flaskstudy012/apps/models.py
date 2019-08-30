# -*- coding: UTF-8 -*-
from datetime import datetime
from apps import db

# class User(object):
#     def __init__(self,name=None,pwd=None,email=None,age=None,birthday=None,face=None):
#         self.name = name
#         self.pwd = pwd
#         self.email = email
#         self.age = age
#         self.birthday = birthday
#         self.face = face
#     def to_list(self):
#         return [self.name, self.pwd, self.email, self.age, self.birthday, self.face]
#
#     def from_list(self,userinfo):
#         self.name = userinfo[0]
#         self.pwd = userinfo[1]
#         self.email = userinfo[2]
#         self.age = userinfo[3]
#         self.birthday = userinfo[4]
#         self.face = userinfo[5]




class User(db.Model):
    # 指定表名
    __tablename__ = 'user'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    pwd = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=False)
    face = db.Column(db.String(120), nullable=False)
    info = db.Column(db.TEXT)
    uuid = db.Column(db.String(120), nullable=False)
    addtime = db.Column(db.DATETIME, default=datetime.now)


    #规定查询之后的信息呈现
    def __repr__(self):
        return '<User %r>' % self.name


if __name__ == '__main__':
    db.drop_all()
    db.create_all()






















