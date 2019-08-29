# -*- coding: UTF-8 -*-

from flask_sqlalchemy import SQLAlchemy
from apps import app


db = SQLAlchemy(app)



class User(db.Model):
    # 指定表名
    __tablename__ = 'userinfo'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    #规定查询之后的信息呈现
    def __repr__(self):
        return '<User %r>' % self.username






if __name__ == '__main__':
    # 生成一个db文件
    db.create_all()
    admin = User(username='admin', email='admin@example.com')
    guest = User(username='guest', email='guest@example.com')

    db.session.add(admin)
    db.session.add(guest)
    db.session.commit()

    all = User.query.all()

    print(all)

    admin_query = User.query.filter_by(username='admin').first()

    print(admin_query)












