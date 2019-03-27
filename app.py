#!/usr/bin/python3
# -*- coding: utf-8 -*-


from flask import Flask

app = Flask(__name__)


@app.route('/')
def index():
    return "<h1> Hello, world! </h1>"


@app.route('/hi')
@app.route('/hello')
def say_hello():
    return "<h1> Say, Hello! </h1>"


@app.route('/greet/<name>')
def greet(name):
    return "<h1> Hello, %s </h1>" % name


"""
使用 export 文件名 来指定运行的文件
使用 flask run 命令可以在命令行启动开发服务器

pipenv install python-dotenv
》》 如果安装了 python-dotenv, flask run 会自动从 .flaskenv 和 .env
手动设置的环境变量 > .env > .flaskenv
在 .env 和 .flaskenv 中的环境变量都是用等号连接的 key=value 形式
"""

if __name__ == '__main__':
    app.run(debug=True)  # 这种方式已经不被推荐
