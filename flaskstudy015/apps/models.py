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
    privacy = db.Column(db.String(80), default='public')
    favornum = db.Column(db.Integer, default=0)
    clicknum = db.Column(db.Integer, default=0)
    uuid = db.Column(db.String(120), nullable=False)
    addtime = db.Column(db.DATETIME, default=datetime.now)
    tag_id = db.Column(db.Integer, db.ForeignKey('album_tag.id'),nullable=False)
    # 在相册这个类里面 user_id 可以为空，否则在注销的时候会报错
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    album_favor = db.relationship('AlbumFavor',backref = 'album',lazy=True)
    photo = db.relationship('Photo',backref = 'album',lazy=True)


    def __repr__(self):
        return '<Album %r>' % self.title

# 相册收藏类
class AlbumFavor(db.Model):

    __tablename__ = 'album_favor'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
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
    flag = 1
    if flag == 0:
        db.drop_all()
        db.create_all()
    if flag == 1:

        tag0 = AlbumTag(name='AJ1')
        tag1 = AlbumTag(name='AJ4')
        tag2 = AlbumTag(name='AJ6')
        tag3 = AlbumTag(name='AJ13')
        tag4 = AlbumTag(name='AJ11')

        db.session.add(tag0)
        db.session.add(tag1)
        db.session.add(tag2)
        db.session.add(tag3)
        db.session.add(tag4)

        db.session.commit()




















