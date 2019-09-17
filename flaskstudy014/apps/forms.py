 # -*- coding: UTF-8 -*-
# 用来存放表单的
from flask import session
from flask_wtf import FlaskForm
# 文件上传相关的改造
from flask_wtf.file import FileField,FileAllowed,FileRequired

# 导入字段
from wtforms import StringField,PasswordField,IntegerField,DateField,SubmitField,TextAreaField,SelectField
# 验证器(用来对输入的数据进行一些限制)
from wtforms.validators import DataRequired,Length,NumberRange,Email,Regexp


from flask_uploads import IMAGES
from apps.models import AlbumTag

tags = AlbumTag.query.all()


# 注册表单的一个form
class RegistForm(FlaskForm):

    user_name = StringField(label='用户名',
                            validators=[DataRequired(message='用户名不能为空！'),
                                                   Length(min=3,max=15,message='用户名长度在3到15个字符之间！')],
                            render_kw={'id':'user_name','class':'form-control'
                                                                ,'placeholder':'输入用户名'})

    user_pwd = PasswordField(label='用户密码',
                             validators=[DataRequired(message='用户密码不能为空！'),
                                                     Length(min=3, max=5, message='用户密码长度在3到5个字符之间！')],
                            render_kw={'id': 'user_pwd', 'class': 'form-control'
                                , 'placeholder': '输入用户密码'})

    user_email = StringField(label='用户邮箱',
                             validators=[DataRequired(message='用户邮箱不能为空！'),
                                                       Email(message='用户邮箱格式不对！')],
                             render_kw={'id': 'user_email', 'class': 'form-control'
                               , 'placeholder': '输入用户邮箱'})

    user_phone = StringField(label='用户手机',
                            validators=[DataRequired(message='用户手机不能为空！'),Regexp('1[3,4,5,8]\d{9}',message='手机号码格式不正确！')],
                            render_kw={'id': 'user_phone', 'class': 'form-control'
                                 , 'placeholder': '输入用户手机'})

    user_desc = TextAreaField(label='用户描述',
                          validators=[],
                          render_kw={'id': 'user_desc', 'class': 'form-control'
                              , 'placeholder': '输入用户描述'})


    user_face = FileField(label='用户头像',
                           validators=[FileRequired(message='用户头像不能为空！'),FileAllowed(IMAGES,'只允许的图片格式为: %s ！'%str(IMAGES))],
                           render_kw={'id': 'user_face', 'class': 'form-control'
                               , 'placeholder': '输入用户头像'})




    submit = SubmitField(label='提交表单',
                         render_kw={'class': 'btn btn-success','value':'注册'})

# 登录表单
class LoginForm(FlaskForm):
    user_name = StringField(label='用户名',
                            validators=[DataRequired(message='用户名不能为空！'),
                                        ],
                            render_kw={'id': 'user_name', 'class': 'form-control'
                                , 'placeholder': '输入用户名'})

    user_pwd = PasswordField(label='用户密码',
                             validators=[DataRequired(message='用户密码不能为空！'),
                                         ],
                             render_kw={'id': 'user_pwd', 'class': 'form-control'
                                 , 'placeholder': '输入用户密码'})

    submit = SubmitField(
                         render_kw={'class': 'btn btn-success', 'value': '登录'})

# 修改密码表单
class PwdForm(FlaskForm):
    old_pwd = PasswordField(label='用户旧密码',
                            validators=[DataRequired(message='用户旧密码不能为空！'),
                                        ],
                            render_kw={'id': 'old_pwd', 'class': 'form-control'
                                , 'placeholder': '输入用户旧密码'})

    new_pwd = PasswordField(label='用户新密码',
                             validators=[DataRequired(message='用户新密码不能为空！'),
                                         Length(min=3, max=5, message='用户密码长度在3到5个字符之间！')],
                             render_kw={'id': 'new_pwd', 'class': 'form-control'
                                 , 'placeholder': '输入用户新密码'})

    submit = SubmitField(
                         render_kw={'class': 'btn btn-success', 'value': '修改'})


# 修改个人资料表单
class InfoForm(FlaskForm):

    user_name = StringField(label='用户名',
                            validators=[DataRequired(message='用户名不能为空！'),
                                                   Length(min=3,max=15,message='用户名长度在3到15个字符之间！')],
                            render_kw={'id':'user_name','class':'form-control'
                                                                ,'placeholder':'输入用户名'})


    user_email = StringField(label='用户邮箱',
                             validators=[DataRequired(message='用户邮箱不能为空！'),
                                                       Email(message='用户邮箱格式不对！')],
                             render_kw={'id': 'user_email', 'class': 'form-control'
                               , 'placeholder': '输入用户邮箱'})

    user_phone = StringField(label='用户手机',
                             validators=[DataRequired(message='用户手机不能为空！'),Regexp('1[3,4,5,8]\d{9}',message='手机号码格式不正确！')],
                             render_kw={'id': 'user_phone', 'class': 'form-control'
                                 , 'placeholder': '输入用户手机'})

    user_desc = TextAreaField(label='用户描述',
                          validators=[],
                          render_kw={'id': 'user_desc', 'class': 'form-control'
                              , 'placeholder': '输入用户描述'})

    user_face = FileField(label='用户头像',
                           validators=[FileAllowed(IMAGES,'只允许的图片格式为: %s ！'%str(IMAGES))],
                           render_kw={'id': 'user_face', 'class': 'form-control'
                               , 'placeholder': '输入用户头像'})

    submit = SubmitField(label='提交表单',
                         render_kw={'class': 'btn btn-success','value':'修改'})


class AlbumInfoForm(FlaskForm):
    album_title = StringField(label='相册标题',
                            validators=[DataRequired(message='相册标题不能为空！'),
                                                   Length(min=3,max=15,message='用户名长度在3到15个字符之间！')],
                            render_kw={'id':'album_title','class':'form-control'
                                                                ,'placeholder':'输入相册名'})

    album_desc = TextAreaField(label='相册描述',
                              validators=[],
                              render_kw={'id': 'album_desc', 'class': 'form-control'
                                  , 'placeholder': '输入相册描述'})

    album_privacy = SelectField(label='相册浏览权限',
                              validators=[],
                              coerce = str,
                              choices = [('private','只给自己看'),('protect-1','只给粉丝看'),('protect-2','只给收藏看'),('public','所有人可看')],
                              render_kw={'id': 'album_privacy', 'class': 'form-control','rows':'3'
                                  })

    album_tag = SelectField(label='相册类别标签',
                            validators=[],
                            coerce=int,
                            choices= [(tag.id, tag.name) for tag in tags],
                            render_kw={'id': 'album_tag', 'class': 'form-control'
                                  })

    submit = SubmitField(
        render_kw={'class': 'form-control btn btn-primary', 'value': '创建相册'})

class AlbumUploadForm(FlaskForm):
    album_title = SelectField(validators=[DataRequired(message='相册名称不能为空！')],
                            coerce=int,
                            # choices= [(album.id, album.title) for album in albums],

                            render_kw={'id': 'album_title', 'class': 'form-control'
                                  })

    album_upload = FileField(validators=[FileRequired(message='请选择一张或多张图片！'),
                                      FileAllowed(IMAGES, '只允许的图片格式为: %s ！' % str(IMAGES))],
                          render_kw={'id': 'album_upload', 'class': 'form-control','multiple':'multiple'
                              })

    submit = SubmitField(
        render_kw={'class': 'form-control btn btn-primary', 'value': '上传相册图片'})


















