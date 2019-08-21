# -*- coding: utf-8 -*-
# 视图函数存放,views 只负责带有路由装饰器的视图
import os
import shutil
# 协助定义装饰器
from functools import wraps

from flask import redirect,url_for,flash,session,make_response
from flask import render_template,request

from apps import app
from apps.models import User
from apps.forms import RegistForm,LoginForm,PwdForm,InfoForm
from apps.sqlite_manage import query_user_to_db,insert_user_to_db,query_user_by_name,delete_user_to_db,update_user_to_db
from apps.utils import secure_filename_with_uuid,check_files_extension,ALLOWED_IMAGE_EXTENSIONS

from flask_uploads import configure_uploads, UploadNotAllowed,UploadSet,IMAGES


# 第二步产生 upload 对象的一个实例
photoSet = UploadSet('photos', IMAGES)

# 第三步绑定app 和 UploadSet对象实例
configure_uploads(app, (photoSet))

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

        user = User()
        # 以 wt-form 方式表单数据
        user.name = form.data['user_name']
        user.pwd = form.data['user_pwd']
        user.email = form.data['user_email']
        user.age = form.data['user_age']
        # user.face = form.data['user_face']
        user.birthday = form.data['user_birth']

        # 获取上传文件信息
        filestorage = request.files['user_face']
        user.face = secure_filename_with_uuid(filestorage.filename)

        # 如果用户已经存在了，就不执行插入操作
        if query_user_by_name(user.name):
            # 消息闪现（给下一个视图传递消息）
            flash(u'用户已存在',category='err')
            return render_template('user_regist.html',form=form)

        insert_user_to_db(user)

        try:
            # 插件uploads方式 保存头像文件
            photoSet.save(filestorage,folder=user.name,name=user.face)

        except UploadNotAllowed:
            flash(u'头像文件格式不对！', category='err')
            return render_template('user_regist.html', form=form)
        else:
            flash(u'用户注册成功', category='ok')
            # 注册完成之后，重定向到登录页面,并把用户名也带过去（携带查询参数(get 方法)）
            return redirect(url_for('user_login', username=user.name))

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
    face_url = photoSet.url(user.name+'/'+user.face)
    return render_template('user_detail.html',face_url = face_url,user = user)


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
        #保存旧的用户名
        oldname = user.name
        user.name = request.form['user_name']
        user.email = request.form['user_email']
        user.age = request.form['user_age']
        # user.face = request.form['user_face']
        user.birthday = request.form['user_birth']

        filestorage = request.files['user_face']

        # 如果更改了文件
        if filestorage.filename != '':

            # 删除旧文件，保存新文件
            olduserpath = photoSet.path(user.face,folder=oldname)
            os.remove(olduserpath)

            user.face = secure_filename_with_uuid(filestorage.filename)
            photoSet.save(filestorage,folder=oldname,name=user.face)


        # 方便静态资源的读取（针对用户名修改的情况）
        if oldname != user.name:
            os.rename(os.path.join(app.config['UPLOADS_DIR'],oldname),os.path.join(app.config['UPLOADS_DIR'],user.name))

        update_user_to_db(oldname, user)
        session['user_name'] = user.name
        return redirect(url_for('user_detail'))
    return render_template('user_info.html',user = user,form=form)


# 注销个人账户
@app.route('/del/',methods=['GET','POST'])
@user_login_req
def user_del():
    if request.method == 'POST':
        # 删除用户的头像文件
        delpath = os.path.join(app.config['UPLOADS_DIR'],session.get('user_name'))
        shutil.rmtree(delpath,ignore_errors=True)

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

