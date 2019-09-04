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
    album = db.relationship('Album',backref = 'user',lazy=True)
    album_favor = db.relationship('AlbumFavor',backref = 'user',lazy=True)


    #规定查询之后的信息呈现
    def __repr__(self):
        return '<User %r>' % self.name


    def check_pwd(self,pwd):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.pwd,pwd)

# 相册标签类
class AlbumTag(db.Model):

    __tablename__ = 'album_tag'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    album = db.relationship('Album',backref = 'album_tag',lazy=True)


    def __repr__(self):
        return '<AlbumTag %r>' % self.name

# 相册类
class Album(db.Model):

    __tablename__ = 'album'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    desc = db.Column(db.TEXT)
    photonum = db.Column(db.Integer, default=0)
    privacy = db.Column(db.Integer, default=0)
    favornum = db.Column(db.Integer, default=0)
    clicknum = db.Column(db.Integer, default=0)
    uuid = db.Column(db.String(120), nullable=False)
    addtime = db.Column(db.DATETIME, default=datetime.now)
    tag_id = db.Column(db.Integer, db.ForeignKey('album_tag.id'),nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    album_favor = db.relationship('AlbumFavor',backref = 'album',lazy=True)
    photo = db.relationship('Photo',backref = 'album',lazy=True)


    def __repr__(self):
        return '<Album %r>' % self.title

# 相册收藏类
class AlbumFavor(db.Model):

    __tablename__ = 'album_favor'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)
    addtime = db.Column(db.DATETIME, default=datetime.now)



class Photo(db.Model):

    __tablename__ = 'photo'

    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(120), nullable=False)#原图文件名
    fname_s = db.Column(db.String(120), nullable=False)#展示图文件名
    fname_t = db.Column(db.String(120), nullable=False)#缩略图文件名
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'), nullable=False)
    addtime = db.Column(db.DATETIME, default=datetime.now)



if __name__ == '__main__':
    db.drop_all()
    db.create_all()






















