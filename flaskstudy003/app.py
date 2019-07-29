from flask import Flask
from flask import render_template,request

app = Flask(__name__)




@app.route('/')
def index():
    return render_template('index.html')

# 注册
@app.route('/regist/',methods=['get','post'])
def user_regist():
    return render_template('user_regist.html')

# 登录
@app.route('/login/',methods=['get','post'])
def user_login():
    return render_template('user_login.html')

if __name__ == '__main__':
    # 调试模式
    app.run(debug=True)
