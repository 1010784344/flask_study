from flask import Flask
from flask import render_template,request

# 创建了一个flask 类的实例
app = Flask(__name__)

# 传递单个变量
@app.route('/<name>')
def amaze(name = None):
    # 传递一个列表
    users = ['123','456','789','798']
    return render_template('index.html',name = name,users = users)

# 传递查询参数
@app.route('/about/')
def about(name=None,users = None):
    # 传递一个列表
    users = ['123', '456', '789', '798']
    print('request: ' ,request)
    # post或者put
    print('request.form: ', request.form)
    # get
    print('request.args: ', request.args['id'])
    print('request.values: ', request.values)
    print('request.cookies: ', request.cookies)
    print('request.headers: ', request.headers)
    print('request.environ: ', request.environ)
    print('request.method: ', request.method)
    # 获取url 对应的视图函数
    print('request.endpoint: ', request.endpoint)



    return render_template('index.html',name = name,users = users)



if __name__ == '__main__':
    # 调试模式
    app.run(debug=True)
