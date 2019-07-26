from flask import Flask
from flask import render_template

# 创建了一个flask 类的实例
app = Flask(__name__)

# 路由
@app.route('/')
# 视图函数
def hello_world():
    return 'Hello World!'


# 动态URL
@app.route('/user/<username>')
def show_user_profile(username):
    return 'User %s' % username
# 动态URL(附带类型转换)
@app.route('/post/<int:post_id>')
def show_post(post_id):
    return 'Post %d' % post_id


# 一个视图函数对应多个url
@app.route('/love/')
@app.route('/521/')
# 视图函数
def beauty_world():
    return 'I Love You'


# 指定 URL 只接受什么样方法
@app.route('/about/',methods=['GET', 'POST'])
def about():
    return 'The about page'

@app.route('/nice/')
def nice():
    return '<h2> nice world </h2>'

@app.route('/amaze/')
def amaze():
    return render_template('index.html')



if __name__ == '__main__':
    # 循环监听浏览器5000端口的输入
    app.run(debug=True)
    # 调试模式