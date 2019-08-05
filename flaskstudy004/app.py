# -*- coding: utf-8 -*-
from flask import Flask,redirect,url_for,g
from flask import render_template,request
from models import User
import sqlite3

app = Flask(__name__)

# app 里指定数据库路径
app.config['DATABASE'] = r'D:\flaskstudy004\database.db'


def connect_db():
    """Connects to the specific database."""
    #  如果没有数据库的话，connect 会创建一个数据库
    rv = sqlite3.connect(app.config['DATABASE'])
    return rv

# 数据库的初始化代码
def init_db( ):
    # 应用环境在每次请求传入时创建。在初始化数据库的时候，我们并不是用请求来创建的，
    # 这里我们并没有请求，所以我们需要手动创建一个应用环境。
    with app.app_context():
        db = connect_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

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



@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()



@app.route('/')
def index():
    return render_template('index.html')

# 注册
@app.route('/regist/',methods=['get','post'])
def user_regist():

    if request.method == 'POST':
        # 获取查询参数
        print(request.form)

        user = User()
        user.name = request.form['user_name']
        user.pwd = request.form['user_pwd']
        user.email = request.form['user_email']
        user.age = request.form['user_age']
        user.face = request.form['user_face']
        user.birthday = request.form['user_birth']
        insert_user_to_db(user)
        # 注册完成之后，重定向到登录页面,并把用户名也带过去（携带查询参数(get 方法)）
        return redirect(url_for('user_login',username = user.name ))

    return render_template('user_regist.html')

# 登录
@app.route('/login/',methods=['get','post'])
def user_login():
    # 全部查询
    all = query_user_to_db()
    for user in all:
        print(user.to_list())
    print('========================')
    # 按条件查询
    users = query_user_by_name('fsdf')
    if users:
        print(users.to_list())
    # 删除
    delete_user_to_db('fsdf')
    print('========================')
    # 全部查询
    all = query_user_to_db()
    for user in all:
        print(user.to_list())





    return render_template('user_login.html')

if __name__ == '__main__':
    # 调试模式
    app.run(debug=True)
    #邮箱：123@qq