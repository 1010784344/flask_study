from flask import g
import sqlite3

from apps import app

from apps.models import User

# 数据库的初始化代码
def init_db( ):
    # 应用环境在每次请求传入时创建。在初始化数据库的时候，我们并不是用请求来创建的，
    # 这里我们并没有请求，所以我们需要手动创建一个应用环境。
    with app.app_context():
        db = connect_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


def connect_db():
    """Connects to the specific database."""
    #  如果没有数据库的话，connect 会创建一个数据库,同时也就意味着这是一张空表
    rv = sqlite3.connect(app.config['DATABASE'])
    return rv


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()

# 增
def insert_user_to_db(user):
    sql = 'insert into users (name,pwd,email,age,birthday,face) values (?,?,?,?,?,?)'
    args = user.to_list()
    g.db.execute(sql, args)
    g.db.commit()

# 删
def delete_user_to_db(user_name):
    sql = 'delete from users where name = ?'
    args = [user_name]
    g.db.execute(sql, args)
    g.db.commit()


# 改
def update_user_to_db(oldname ,user):
    sql = 'update users set name = ?,pwd = ?,email = ?,age = ?,birthday = ?,face = ? where name = ?'
    args = user.to_list()
    args.append(oldname)
    g.db.execute(sql, args)
    g.db.commit()


# 查
def query_user_to_db():

    all_user = []
    sql = 'select * from users'
    args = []
    sql_select = g.db.execute(sql,args)
    for item in sql_select.fetchall():
        user = User()
        user.from_list(item[1:])
        all_user.append(user)
    return all_user


# 按条件进行查询
def query_user_by_name(user_name):

    sql = 'select * from users where name = ?'
    args = [user_name]
    sql_select = g.db.execute(sql,args)
    item = sql_select.fetchall()
    # 非空判断
    if len(item) < 1:
        return None

    user = User()
    user.from_list(item[0][1:])

    return user

if __name__ == '__main__':
    # 用于创建数据库，只在刚开始的时候执行一次、
    # 同时需要在 app.config['DATABASE'] 指定数据库的路径
    # 否则就会提示 user 表不存在
    init_db()