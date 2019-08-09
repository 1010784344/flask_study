# -*- coding: UTF-8 -*-
# 用来存放表单的
from flask_wtf import FlaskForm
# 导入字段
from wtforms import StringField,PasswordField,IntegerField,DateField,FileField
# 验证器(用来对输入的数据进行一些限制)
from wtforms.validators import DataRequired,Length,NumberRange


# 注册表单的一个form
class RegistForm(FlaskForm):

    user_name = StringField(label='用户名',validators=[DataRequired(message='用户名不能为空！'),
    Length(min=3,max=15,message='用户名长度在3到15个字符之间！')],render_kw={'id':'user_name','class':'form-control'
                                                                ,'placeholder':'输入用户名'})

    user_pwd = PasswordField(label='用户密码', validators=[DataRequired(message='用户密码不能为空！'),
                                                     Length(min=3, max=5, message='用户密码长度在3到5个字符之间！')],
                            render_kw={'id': 'user_pwd', 'class': 'form-control'
                                , 'placeholder': '输入用户密码'})

    user_email = StringField(label='用户邮箱', validators=[DataRequired(message='用户邮箱不能为空！'),
                                                     Length(min=3, max=15, message='用户名长度在3到15个字符之间！')],
                           render_kw={'id': 'user_email', 'class': 'form-control'
                               , 'placeholder': '输入用户邮箱'})

    user_age = IntegerField(label='用户年龄', validators=[DataRequired(message='用户密码不能为空！'),
                                                      NumberRange(min=18,max=70,message='用户年龄在18到70之间！')],
                             render_kw={'id': 'user_age', 'class': 'form-control'
                                 , 'placeholder': '输入用户年龄'})
    user_birth = DateField(label='用户生日', validators=[DataRequired(message='用户生日不能为空！')],
                            render_kw={'id': 'user_birth', 'class': 'form-control'
                                , 'placeholder': '输入用户生日'})

    user_face = DateField(label='提交表单',
                            render_kw={'class': 'btn btn-success','value':'注册'
                                , })







