from flask import Flask,redirect,url_for
from flask import render_template,request
from flaskstudy003.models import User
app = Flask(__name__)




@app.route('/')
def index():
    return render_template('index.html')

# 注册
@app.route('/regist/',methods=['get','post'])
def user_regist():

    if request.method == 'POST':

        print(request.form)

        user = User()
        user.name = request.form['user_name']
        user.pwd = request.form['user_pwd']
        user.email = request.form['user_email']
        user.age = request.form['user_age']
        user.face = request.form['user_face']
        user.birthday = request.form['user_birth']

        # 注册完成之后，重定向到登录页面,并把用户名也带过去（携带查询参数(get 方法)）
        return redirect(url_for('user_login',username = user.name ))

    return render_template('user_regist.html')

# 登录
@app.route('/login/',methods=['get','post'])
def user_login():
    return render_template('user_login.html')

if __name__ == '__main__':
    # 调试模式
    app.run(debug=True)
    #邮箱：123@qq