# -*- coding: utf-8 -*-
# 视图函数存放,views 只负责带有路由装饰器的视图
import os
import json
import uuid
import shutil
from random import randint
# 协助定义装饰器
from functools import wraps

from flask import redirect,url_for,flash,session,make_response
from flask import render_template,request

from apps import app
from apps.models import User, Album, Photo, AlbumTag, AlbumFavor
from apps.forms import RegistForm,LoginForm,PwdForm,InfoForm,AlbumInfoForm,AlbumUploadForm
from apps import db
from apps.utils import secure_filename_with_uuid,create_thumbnail,create_show

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

        # 如果用户已经存在了，就不执行插入操作
        user_qusery = User.query.filter_by(name=form.data['user_name']).first()
        if user_qusery:
            # 消息闪现（给下一个视图传递消息）
            flash(u'用户已存在', category='err')
            return render_template('user_regist.html', form=form)

        # 如果邮箱已经存在了，就不执行插入操作
        user_qusery = User.query.filter_by(email=form.data['user_email']).first()
        if user_qusery:
            # 消息闪现（给下一个视图传递消息）
            flash(u'邮箱已存在', category='err')
            return render_template('user_regist.html', form=form)

        # 如果手机号已经存在了，就不执行插入操作
        user_qusery = User.query.filter_by(phone=form.data['user_phone']).first()
        if user_qusery:
            # 消息闪现（给下一个视图传递消息）
            flash(u'手机号已存在', category='err')
            return render_template('user_regist.html', form=form)


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


# 个人收藏相册
@app.route('/user/album/favor/<int:page>',methods=['GET','POST'])
@user_login_req
def user_album_favor(page=None):
    albumtags = AlbumTag.query.all()

    tagid = request.args.get('tag', 'all')

    uid = session.get('user_id', '')

    # 联合查询实例
    if tagid == 'all':
        albums = Album.query.join(AlbumFavor).filter(Album.privacy == 'private',AlbumFavor.user_id == uid
                                    ).order_by(Album.addtime.desc()).paginate(page=page,per_page=6)
    else:
        albums = Album.query.join(AlbumFavor).filter(Album.privacy == 'private', Album.tag_id == int(tagid),
                                                     AlbumFavor.user_id == uid).order_by(
            Album.addtime.desc()).paginate(page=page,per_page=6)


    for album in albums.items:

        cover = album.photo[randint(0, len(album.photo) - 1)].fname_t
        folder = album.user.name + '/' + album.title

        # 动态的给 album 对象添加一个 coverimgurl 属性
        coverimgurl = photoSet.url(filename=folder + '/' + cover)
        album.coverimgurl = coverimgurl


    return render_template('user_album_favor.html',albumtags=albumtags,albums=albums)


# 个人上传的相册
@app.route('/user/album/upload/<int:page>',methods=['GET','POST'])
@user_login_req
def user_album_upload(page=None):
    albumtags = AlbumTag.query.all()

    tagid = request.args.get('tag', 'all')

    uid = session.get('user_id', '')


    if tagid == 'all':
        albums = Album.query.filter(Album.user_id == uid
                                                     ).order_by(Album.addtime.desc()).paginate(page=page, per_page=6)
    else:
        albums = Album.query.filter(Album.tag_id == int(tagid),
                                                     Album.user_id == uid).order_by(
            Album.addtime.desc()).paginate(page=page, per_page=6)

    for album in albums.items:
        cover = album.photo[randint(0, len(album.photo) - 1)].fname_t
        folder = album.user.name + '/' + album.title

        # 动态的给 album 对象添加一个 coverimgurl 属性
        coverimgurl = photoSet.url(filename=folder + '/' + cover)
        album.coverimgurl = coverimgurl


    return render_template('user_album_upload.html', albumtags=albumtags, albums=albums)


# 删除个人相册
@app.route('/user/album/upload/del/<int:id>',methods=['GET','POST'])
@user_login_req
def user_album_upload_del(id=None):

    album = Album.query.get_or_404(id)
    folder = session.get('user_name') + '/' + album.title

    # 删除相册下面所有图像，同时删除 photo 表中的记录
    for photo in album.photo:
        imagepath = photoSet.path(folder + '/' + photo.fname)
        imagepaths = photoSet.path(folder + '/' + photo.fname_s)
        imagepatht = photoSet.path(folder + '/' + photo.fname_t)
        os.remove(imagepath)
        os.remove(imagepaths)
        os.remove(imagepatht)

        db.session.delete(photo)
        db.session.commit()

    # 删除相册收藏记录
    for favor in album.album_favor:
        db.session.delete(favor)
        db.session.commit()

    # 删除相册本身,及文件夹
    albumpath = photoSet.config.destination + '/' + folder
    shutil.rmtree(albumpath)

    db.session.delete(album)
    db.session.commit()
    return redirect(url_for('user_album_upload',page=1))

# 修改个人上传的相册
@app.route('/user/album/upload/modify/<int:id>',methods=['GET','POST'])
@user_login_req
def user_album_upload_modify(id=None):
    form = AlbumInfoForm()
    # album = Album.query.filter_by(id=id).first()
    album = Album.query.get_or_404(id)
    if request.method == 'GET':
        # 表单回填
        form.album_desc.data = album.desc
        form.album_privacy.data = album.privacy
        form.album_tag.data = album.tag_id
        form.album_recmm.data = album.recommend

    if form.validate_on_submit():
        album.desc = form.album_desc.data
        album.privacy = form.album_privacy.data
        album.tag_id = int(form.album_tag.data)
        album.recommend = form.album_recmm.data

        db.session.add(album)
        db.session.commit()
        return redirect(url_for('user_album_upload',page=1))
    return render_template('user_album_upload_modify.html',form=form,album=album)


# 相册里增删图片（及新增图片）
@app.route('/user/album/upload/photo/add/<int:id>',methods=['GET','POST'])
@user_login_req
def user_album_upload_photo_add(id=None):
    album = Album.query.get_or_404(id)
    if request.method == 'GET':
        photos = album.photo

        photofolder = album.user.name + '/' + album.title

        for photo in photos:
            imgurl = photoSet.url(filename=photofolder + '/' + photo.fname_t)
            photo.imgurl = imgurl

    if request.method == 'POST':

        filesmul = request.files.getlist('album_upload')

        # 这里中间可以再在这里添加一个自己写的后缀验证器，再进行遍历改名和统计。
        # 这里我们默认文件后缀都是没有问题的

        folder = session.get('user_name') + '/' + album.title

        # 开始遍历每一个合格的照片文件，并保存在当前用户目录
        for file in filesmul:
            # 重命名
            fname = secure_filename_with_uuid(file.filename)

            # 保存文件
            photoSet.save(file, folder=folder, name=fname)

            # 生成缩略图
            fname_thumb = create_thumbnail(path=photoSet.config.destination + os.sep + folder, filename=fname)

            # 生成展示图
            fname_show = create_show(path=photoSet.config.destination + os.sep + folder, filename=fname)

            # 保存到数据库
            photo = Photo(fname=fname, fname_s=fname_show, fname_t=fname_thumb, album_id=album.id)
            db.session.add(photo)
            db.session.commit()

        #将上传的相册文件填入数据库
        album.photonum = int(album.photonum) + len(filesmul)

        db.session.add(album)
        db.session.commit()
        message = u'成功保存' + str(len(filesmul)) + '张图片,当前相册共拥有' + str(album.photonum) + '张图片'
        flash(message=message, category='ok')
        return redirect(url_for('user_album_upload_photo_add', id=id))

    return render_template('user_album_upload_photo_add.html', photos=photos)


# 删除相册里的图片
@app.route('/user/album/upload/photo/del/<int:id>',methods=['GET','POST'])
@user_login_req
def user_album_upload_photo_del(id=None):
    # 照片id
    photo = Photo.query.get_or_404(id)
    album = photo.album

    # 利用 flask-uploads 拼凑出绝对路径
    folder = session.get('user_name') + '/' + album.title
    imagepath = photoSet.path(folder + '/' + photo.fname)
    imagepaths = photoSet.path(folder + '/' + photo.fname_s)
    imagepatht = photoSet.path(folder + '/' + photo.fname_t)

    os.remove(imagepath)
    os.remove(imagepaths)
    os.remove(imagepatht)

    album.photonum = album.photonum - 1
    db.session.delete(photo)
    db.session.add(album)
    db.session.commit()

    return redirect(url_for('user_album_upload_adddel',id = album.id))


# 注销个人账户
@app.route('/user/del/',methods=['GET','POST'])
@user_login_req
def user_del():
    if request.method == 'POST':

        # 根据用户名查询用户
        # user = User.query.filter_by(name = session.get('user_name')).first()
        # 根据id查询用户
        user = User.query.get_or_404(int(session.get('user_id')))

        # 删除用户的头像文件
        delpath = os.path.join(app.config['UPLOADS_DIR'],session.get('user_name'))
        shutil.rmtree(delpath,ignore_errors=True)

        # 删除用户相关的引用，相册，照片，收藏之类的
        for album in user.album:
            for photo in album.photo:
                db.session.delete(photo)
                db.session.commit()

            for favor in album.album_favor:
                db.session.delete(favor)
                db.session.commit()

            db.session.delete(album)
            db.session.commit()

        # 删除用户
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

        # 同一个用户相册同名，返回处理
        exist_count = Album.query.filter(Album.title == album_title,Album.user_id == session.get('user_id')).count()
        if exist_count > 0:
            flash(message='相册标题已经存在，请重新输入标题！',category='err')
            return render_template('album_create.html',form = form)

        album_desc = form.album_desc.data
        album_privacy = form.album_privacy.data
        album_tag = form.album_tag.data
        album_recmm = form.album_recmm.data

        # 确保uuid的唯一性
        existed = True
        album_uuid = str(uuid.uuid4().hex)[:6]
        while existed:
            if Album.query.filter_by(uuid = album_uuid).count() > 0:
                album_uuid = str(uuid.uuid4().hex)[:6]
            else:
                existed = False

        album = Album(title=album_title,desc=album_desc,privacy=album_privacy,tag_id=album_tag,uuid=album_uuid,recommend=album_recmm,
                      user_id=int(session.get('user_id')))

        db.session.add(album)
        db.session.commit()

        return redirect(url_for('album_upload'))

    return render_template('album_create.html',form = form)

@app.route('/album/browse/<int:id>')
def album_browse(id=None):
    # id 是相册的id
    album = Album.query.filter_by(id=id).first()

    # 更新相册点击量
    album.clicknum += 1
    db.session.add(album)
    db.session.commit()

    #取出推荐列表的相册信息（同标签,但并不展示当前相册）
    recommendalbums = Album.query.filter(Album.tag_id == album.tag_id, Album.id != id).all()

    # 取出推荐列表相册展示图片的url
    for recom in recommendalbums:
        cover = recom.photo[randint(0,len(recom.photo)-1)].fname_t
        folder = recom.user.name + '/' + recom.title
        # 动态的给 album 对象添加一个 coverimgurl 属性
        coverimgurl = photoSet.url(filename=folder + '/' + cover)
        recom.coverimgurl = coverimgurl

    # 取出收藏列表的相册信息（当前用户的收藏的相册）
    uid = session.get('user_id','')
    favordalbums = []
    if uid:

        uidalbums = AlbumFavor.query.filter(AlbumFavor.user_id == uid).all()
        for tmpfavor in uidalbums:
            favordalbums.append(tmpfavor.album)

        #取出收藏列表相册展示图片的url
        for falbum in favordalbums:
            cover = falbum.photo[randint(0, len(falbum.photo) - 1)].fname_t
            folder = falbum.user.name + '/' + falbum.title
            # 动态的给 album 对象添加一个 coverimgurl 属性
            favorimgurl = photoSet.url(filename=folder + '/' + cover)
            falbum.favorimgurl = favorimgurl


    #取出作者头像的url
    folder = album.user.name
    userface_url = photoSet.url(filename=folder + '/' + album.user.face)

    # 取出该相册下面所有图片
    # photos = Photo.query.filter_by(album_id=id).all()
    photos = album.photo

    photofolder = album.user.name + '/' + album.title

    for photo in photos:
        imgurl = photoSet.url(filename=photofolder + '/' + photo.fname)
        photo.imgurl = imgurl


    return render_template('album_browse.html', album=album, userface_url=userface_url,
                           recommendalbums=recommendalbums,favordalbums=favordalbums)


@app.route('/album/list/<int:page>')
def album_list(page=None):

    albumtags = AlbumTag.query.all()

    # 如果没有tag对应的键值，就赋值为 all
    tagid = request.args.get('tag','all')

    #按相册标签，公开类型，时间降序排序（并对获取的数据完成分页）
    if tagid == 'all':
        albums = Album.query.filter(Album.privacy == 'private').order_by(Album.addtime.desc()).paginate(page=page,per_page=4)
    else:
        albums = Album.query.filter(Album.privacy =='private',Album.tag_id == int(tagid)).order_by(Album.addtime.desc()).paginate(page=page,per_page=4)

    # albums 是 pagination 对象（不可迭代）
    # albums.items 里面只有当前分页得到的这些数据

    print(albums.items)

    # 外键使用实例：album（一） 里面去找 照片（多） 的相关信息
    for album in albums.items:
        # 基于外键的使用，当拿捏不准，不知道怎么使用的话，可以进行打印，查看效果
        # print(album.photo),可以拿出该相册下面的所有photo
        cover = album.photo[randint(0,len(album.photo)-1)].fname_t
        folder = album.user.name + '/' + album.title

        # 动态的给 album 对象添加一个 coverimgurl 属性
        coverimgurl = photoSet.url(filename=folder + '/' + cover)
        album.coverimgurl = coverimgurl

    return render_template('album_list.html',albumtags = albumtags,albums = albums)


@app.route('/album/upload',methods=['GET','POST'])
@user_login_req
def album_upload():

    form = AlbumUploadForm()

    # 动态给form 表单的内容添加属性并查询当前用户的相册信息
    albums = Album.query.filter_by(user_id=session.get('user_id')).all()
    form.album_title.choices = [(album.id, album.title) for album in albums]

    #如果没有相册，就进不去更新相册里面
    if not form.album_title.choices:
        flash(message='请先创建一个相册，再上传照片！', category='err')
        return redirect(url_for('album_create'))

    if form.validate_on_submit():

        # 如果上传多个文件，也只会返回一个 filestorage 对象
        files1 = request.files['album_upload']
        # 如果上传多个文件，会返回一个 filestorage 对象列表
        filesmul = request.files.getlist('album_upload')

        albumstitle = ''
        # 遍历下拉框标签，找到用户选中的对应的相册title
        for id,title in form.album_title.choices:
            if id == form.album_title.data:
                albumstitle = title

        #将上传的相册文件保存在本地

        # 构造 flask-uploads 配置之下的中间路径
        folder = session.get('user_name')+'/'+albumstitle

        files_url = []
        # 开始遍历每一个合格的照片文件，并保存在当前用户目录
        for file in filesmul:
            # 重命名
            fname = secure_filename_with_uuid(file.filename)

            # 保存文件
            photoSet.save(file, folder=folder, name=fname)

            # 生成缩略图
            fname_thumb = create_thumbnail(path=photoSet.config.destination + os.sep + folder, filename=fname)

            # 生成展示图
            fname_show = create_show(path=photoSet.config.destination + os.sep + folder, filename=fname)


            # 缩率图生成url（这一行代码的意义是利用 photoSet.url 将任意一个本地文件生成 url）
            furl = photoSet.url(folder + '/' + fname_thumb)
            files_url.append(furl)

            #保存到数据库
            photo = Photo(fname=fname,fname_s=fname_show,fname_t=fname_thumb,album_id=form.album_title.data)
            db.session.add(photo)
            db.session.commit()

        # #将上传的相册文件填入数据库
        albumu = Album.query.filter_by(id=form.album_title.data).first()
        albumu.photonum  = int(albumu.photonum) + len(filesmul)

        db.session.add(albumu)
        db.session.commit()
        message = u'成功保存'+str(len(filesmul))+'张图片,当前相册共拥有' + str(albumu.photonum) + '张图片'
        flash(message=message, category='ok')
        return render_template('album_upload.html', form=form, files_url=files_url)
    return render_template('album_upload.html',form = form)

# 相册收藏ajax响应
@app.route('/album/favor/',methods=['GET','POST'])
@user_login_req
def album_favor():
    aid = request.args.get('aid')
    uid = request.args.get('uid')
    act = request.args.get('act')
    # 检测数据库是否已经存在这样一条收藏记录
    existed = AlbumFavor.query.filter_by(user_id = uid,album_id = aid).all()

    album = Album.query.filter_by(id = aid).first()


    # 0 已经收藏 1 收藏成功  2 取消收藏
    if len(existed) >= 1:

        if act == 'add':
            favor_dict = {'ok': '0'}
        elif act == 'del':
            existed = AlbumFavor.query.filter_by(user_id=uid, album_id=aid).first()
            db.session.delete(existed)
            db.session.commit()
            favor_dict = {'ok': '2'}

            # 统计收藏量减一
            album.favornum -= 1
            db.session.add(album)
            db.session.commit()
    else:
        # 添加收藏
        favor = AlbumFavor(user_id = uid,album_id = aid)

        db.session.add(favor)
        db.session.commit()

        favor_dict = {'ok':'1'}

        # 统计收藏量加一
        album.favornum += 1
        db.session.add(album)
        db.session.commit()


    favor_str = json.dumps(favor_dict)
    # json 响应
    return favor_str







# 定制错误页面
@app.errorhandler(404)
def page_not_found(error):
    resp = make_response(render_template('page_not_found.html'), 404)
    return resp

