# -*- coding: utf-8 -*-
from flask import Flask,redirect,url_for,g,flash,get_flashed_messages,session,make_response
from flask import render_template,request
from models import User
import sqlite3
# 协助定义装饰器
from functools import wraps


from forms import RegistForm,LoginForm,PwdForm,InfoForm

app = Flask(__name__)

# app 里指定数据库路径
app.config['DATABASE'] = r'D:\flaskstudy006\database.db'
# 要使用session的话，必须要设置secret key
app.config['SECRET_KEY'] = r'de lu da shu 666'

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



@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    if hasattr(g, 'db'):
        g.db.close()


# 检验登录装饰器（访问控制）
def user_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not 'user_name' in session:
            # 仅仅做个展示，在没有访问权跳转到的登录页面，显示你刚才要访问的页面链接
            return redirect(url_for('user_login', next = request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def index():

    # 全部查询
    all = query_user_to_db()
    for user in all:
        print(user.to_list())

    # 制造响应设置cookie
    resp = make_response(render_template('index.html'))

    return resp

# 注册
@app.route('/regist/',methods=['get','post'])
def user_regist():
    form = RegistForm()
    if form.validate_on_submit():
        # 获取查询参数
        print(request.form)

        user = User()
        # 以 wt-form 方式表单数据
        user.name = form.data['user_name']
        user.pwd = form.data['user_pwd']
        user.email = form.data['user_email']
        user.age = form.data['user_age']
        user.face = form.data['user_face']
        user.birthday = form.data['user_birth']

        # 如果用户已经存在了，就不执行插入操作
        if query_user_by_name(user.name):
            # 消息闪现（给下一个视图传递消息）
            flash(u'用户已存在',category='err')
            return render_template('user_regist.html',form=form)

        insert_user_to_db(user)
        flash(u'用户注册成功',category='ok')
        # 注册完成之后，重定向到登录页面,并把用户名也带过去（携带查询参数(get 方法)）
        return redirect(url_for('user_login',username = user.name ))
    # 因为有表单要填，所以提前加一个 form=form
    return render_template('user_regist.html',form=form)

# 个人中心
@app.route('/usercenter/',methods=['GET'])
@user_login_req
def user_center():
    return render_template('user_center.html')


# 个人信息详情
@app.route('/detail/',methods=['GET'])
@user_login_req
def user_detail():
    user = query_user_by_name(session.get('user_name'))
    return render_template('user_detail.html',user = user)


# 个人修改密码
@app.route('/pwd/',methods=['GET','POST'])
@user_login_req
def user_pwd():
    form = PwdForm()
    if form.validate_on_submit():

        old_pwd = request.form['old_pwd']
        new_pwd = request.form['new_pwd']
        user = query_user_by_name(session.get('user_name'))
        if str(old_pwd) != str(user.pwd):
            flash('旧密码输入有误！',category='err')
            return render_template('user_pwd.html',form=form)
        else:
            user.pwd = new_pwd
            update_user_to_db(user.name,user)
            # 修改完密码之后，删掉用户信息，让他重新登录
            session.pop('user_name', None)
            flash('修改密码成功，请重新登录！',category='ok')
            return redirect(url_for('user_login',username = user.name))
    return render_template('user_pwd.html',form=form)


# 个人修改资料
@app.route('/info/',methods=['GET','POST'])
@user_login_req
def user_info():
    form = InfoForm()

    user = query_user_by_name(session['user_name'])
    if form.validate_on_submit():

        oldname = user.name
        user.name = request.form['user_name']
        user.email = request.form['user_email']
        user.age = request.form['user_age']
        user.face = request.form['user_face']
        user.birthday = request.form['user_birth']
        update_user_to_db(oldname,user)

        session['user_name'] = user.name

        return redirect(url_for('user_detail'))
    return render_template('user_info.html',user = user,form=form)


# 注销个人账户
@app.route('/del/',methods=['GET','POST'])
@user_login_req
def user_del():
    if request.method == 'POST':
        delete_user_to_db(session.get('user_name'))
        return redirect(url_for('log_out'))
    return render_template('user_del.html')


# 登录
@app.route('/login/',methods=['get','post'])
def user_login():
    form = LoginForm()

    if form.validate_on_submit():
        user_name = request.form['user_name']
        user_pwd = request.form['user_pwd']
        query_user = query_user_by_name(user_name)
        if not query_user:
            flash(u'用户不存在', category='err')
            return render_template('user_login.html',form = form)
        else:
            if str(query_user.pwd) != str(user_pwd):
                flash(u'密码输入有误', category='err')
                return render_template('user_login.html',form = form)
            else:
                # flash(u'登录成功', category='ok')
                # 手动加入cookie（session） 信息
                session['user_name'] = user_name
                return render_template('index.html')

    return render_template('user_login.html',form = form)
# 退出
@app.route('/logout/',methods=['GET'])
@user_login_req
def log_out():

    session.pop('user_name',None)
    return redirect(url_for('index'))


# 定制错误页面
@app.errorhandler(404)
def page_not_found(error):
    resp = make_response(render_template('page_not_found.html'), 404)
    return resp


if __name__ == '__main__':
    # 调试模式
    app.run(debug=True)
    #邮箱：123@qq