# -*- coding: utf-8 -*-
# 视图函数存放,views 只负责带有路由装饰器的视图
import os
import uuid
import shutil
# 协助定义装饰器
from functools import wraps

from flask import redirect,url_for,flash,session,make_response
from flask import render_template,request

from apps import app
from apps.models import User,AlbumTag,Album
from apps.forms import RegistForm,LoginForm,PwdForm,InfoForm,AlbumInfoForm
from apps import db
from apps.utils import secure_filename_with_uuid

from flask_uploads import configure_uploads, UploadNotAllowed,UploadSet,IMAGES
# 加密
from werkzeug.security import generate_password_hash

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
    # all = db.query.
    # for user in all:
    #     print(user.to_list())

    # 制造响应设置cookie
    resp = make_response(render_template('index.html'))

    return resp



# 注册
@app.route('/user/regist/',methods=['GET','POST'])
def user_regist():
    form = RegistForm()
    if form.validate_on_submit():

        user = User()
        # 以 wt-form 方式表单数据
        user.name = form.data['user_name']
        user.pwd = generate_password_hash(form.data['user_pwd'])
        user.email = form.data['user_email']
        user.phone = form.data['user_phone']
        user.desc = form.data['user_desc']
        user.uuid = str(uuid.uuid4().hex)[:6]

        # 获取上传文件信息
        filestorage = request.files['user_face']
        user.face = secure_filename_with_uuid(filestorage.filename)

        # 如果用户已经存在了，就不执行插入操作
        if User.query.filter_by(name = user.name).first():
            # 消息闪现（给下一个视图传递消息）
            flash(u'用户已存在',category='err')
            return render_template('user_regist.html',form=form)


        try:
            # 插件uploads方式 保存头像文件
            photoSet.save(filestorage,folder=user.name,name=user.face)

        except UploadNotAllowed:
            flash(u'头像文件格式不对！', category='err')
            return render_template('user_regist.html', form=form)
        else:

            db.session.add(user)
            db.session.commit()

            flash(u'用户注册成功', category='ok')
            # 注册完成之后，重定向到登录页面,并把用户名也带过去（携带查询参数(get 方法)）
            return redirect(url_for('user_login', username=user.name))

    # 因为有表单要填，所以提前加一个 form=form
    return render_template('user_regist.html',form=form)

# 个人中心
@app.route('/user/usercenter/',methods=['GET'])
@user_login_req
def user_center():
    return render_template('user_center.html')


# 个人信息详情
@app.route('/user/detail/',methods=['GET'])
@user_login_req
def user_detail():
    user = User.query.filter_by(name = session.get('user_name')).first_or_404()
    face_url = photoSet.url(user.name+'/'+user.face)
    return render_template('user_detail.html',face_url = face_url,user = user)


# 个人修改密码
@app.route('/user/pwd/',methods=['GET','POST'])
@user_login_req
def user_pwd():
    form = PwdForm()
    if form.validate_on_submit():

        old_pwd = request.form['old_pwd']
        new_pwd = request.form['new_pwd']
        user = User.query.filter_by(name=session.get('user_name')).first()
        if not user.check_pwd(old_pwd):
            flash('旧密码输入有误！',category='err')
            return render_template('user_pwd.html',form=form)
        else:
            user.pwd = generate_password_hash(new_pwd)

            db.session.add(user)
            db.session.commit()

            # 修改完密码之后，删掉用户信息，让他重新登录
            session.pop('user_name', None)
            session.pop('user_id', None)

            flash('修改密码成功，请重新登录！',category='ok')
            return redirect(url_for('user_login',username = user.name))
    return render_template('user_pwd.html',form=form)


# 个人修改资料
@app.route('/user/info/',methods=['GET','POST'])
@user_login_req
def user_info():
    form = InfoForm()

    user = User.query.filter_by(name=session['user_name']).first()

    #用户描述提供默认显示
    form.user_desc.data = user.desc

    if form.validate_on_submit():
        #保存旧的用户名
        oldname = user.name
        user.name = request.form['user_name']
        user.email = request.form['user_email']
        user.phone = request.form['user_phone']
        # user.face = request.form['user_face']
        user.desc = request.form['user_desc']

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

        db.session.add(user)
        db.session.commit()

        session['user_name'] = user.name
        session['user_id'] = user.id

        return redirect(url_for('user_detail'))
    return render_template('user_info.html',user = user,form=form)


# 注销个人账户
@app.route('/user/del/',methods=['GET','POST'])
@user_login_req
def user_del():
    if request.method == 'POST':
        # 删除用户的头像文件
        delpath = os.path.join(app.config['UPLOADS_DIR'],session.get('user_name'))
        shutil.rmtree(delpath,ignore_errors=True)

        # user = User.query.filter_by(name = session.get('user_name')).first()
        # 根据id查询用户
        user = User.query.get_or_404(int(session.get('user_id')))
        db.session.delete(user)
        db.session.commit()

        return redirect(url_for('log_out'))
    return render_template('user_del.html')


# 登录
@app.route('/user/login/',methods=['get','post'])
def user_login():
    form = LoginForm()

    if form.validate_on_submit():
        user_name = request.form['user_name']
        user_pwd = request.form['user_pwd']

        #查看用户名是否存在
        query_user = User.query.filter_by(name = user_name).first()
        if not query_user:
            flash(u'用户不存在', category='err')
            return render_template('user_login.html',form = form)
        else:
            if not query_user.check_pwd(str(user_pwd)):
                flash(u'密码输入有误', category='err')
                return render_template('user_login.html',form = form)
            else:
                # flash(u'登录成功', category='ok')
                # 手动加入cookie（session） 信息
                session['user_name'] = user_name
                session['user_id'] = query_user.id
                return render_template('index.html')

    return render_template('user_login.html',form = form)


# 退出
@app.route('/user/logout/',methods=['GET'])
@user_login_req
def log_out():

    session.pop('user_name',None)
    session.pop('user_id', None)

    return redirect(url_for('index'))


@app.route('/album/')
def album_index():

    resp = make_response(render_template('album_index.html'))

    return resp

@app.route('/album/create',methods=['GET','POST'])
@user_login_req
def album_create():
    form = AlbumInfoForm()

    if form.validate_on_submit():
        # 一条post 数据插入数据库
        album_title = form.album_title.data

        # 相册同名，返回处理
        # exist_count = Album.query.filter_by(title=album_title).count()
        # if exist_count > 0:
        #     flash(message='相册标题已经存在，请重新输入标题！',category='err')
        #     return render_template('album_create.html',form = form)

        album_desc = form.album_desc.data
        album_privacy = form.album_privacy.data
        album_tag = form.album_tag.data

        # 确保uuid的唯一性
        existed = True
        album_uuid = str(uuid.uuid4().hex)[:6]
        while existed:
            if Album.query.filter_by(uuid = album_uuid).count() > 0:
                album_uuid = str(uuid.uuid4().hex)[:6]
            else:
                existed = False

        album = Album(title=album_title,desc=album_desc,privacy=album_privacy,tag_id=album_tag,uuid=album_uuid,
                      user_id=int(session.get('user_id')))

        db.session.add(album)
        db.session.commit()

        return redirect(url_for('album_upload'))

    return render_template('album_create.html',form = form)

@app.route('/album/browse')
def album_browse():

    resp = make_response(render_template('album_browse.html'))

    return resp

@app.route('/album/list')
def album_list():

    resp = make_response(render_template('album_list.html'))

    return resp


@app.route('/album/upload')
@user_login_req
def album_upload():

    resp = make_response(render_template('album_upload.html'))

    return resp


# 定制错误页面
@app.errorhandler(404)
def page_not_found(error):
    resp = make_response(render_template('page_not_found.html'), 404)
    return resp

