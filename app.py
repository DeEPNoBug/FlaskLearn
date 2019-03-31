#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import click
from flask import Flask, url_for, redirect, session, request, abort

app = Flask(__name__)

# 使用 config 配置, 配置名必须是大写，小写的不会被读取
app.config["ADMIN_NAME"] = "Admin"  # 配置一条

# 配置多条
# app.config.update(
#     TESTING=True,
#     SECRET_KEY="+dgNmjumLsAOuPkEMs8LWVxH85d1B9dCvAiMdzF3/2k="
# )

# 设置 secret_key 的方式1
# app.secret_key = "+dgNmjumLsAOuPkEMs8LWVxH85d1B9dCvAiMdzF3/2k"

# 方式 二
app.secret_key = os.getenv("SECRET_KEY", "default_secret_key")

# 从配置文件中读取数据
value = app.config["SECRET_KEY"]


@app.route('/')
def index():
    return "<h1> Hello, world! </h1>"


@app.route('/hi')
@app.route('/hello')
def say_hello():
    # return "<h1> Say, Hello! %s</h1>" % value
    # return url_for('index')  # 通过传入的 endpoint 获取到对应的 url

    # 修改say_hello 来实现对session 认证的简单使用
    name = request.cookies.get('name', 'Human')
    response = "<h1> Hello, %s </h1>" % name

    if 'logged_in' in session:
        response += '[Authenticated]'
    else:
        response += '[Not Authenticated]'

    return response


@app.route('/greet/<name>')
def greet(name):
    # return "<h1> Hello, %s </h1>" % name
    return url_for("say_hello", name=name)  # 返回带查询参数的 url，两种方式返回的都是相对的 url ，将 _external=True 就会返回完整的 url


# 创建 Flask 命令
@app.cli.command()
def hello():
    click.echo("Hello, World!")


@app.cli.command('say-hello')
def say_hello2():
    click.echo("Hello, Human!")


# 更多 自定义命令设置 参考 click 的官方文档 https://click.palletsprojects.com/en/7.x/

"""
使用 export 文件名 来指定运行的文件
使用 flask run 命令可以在命令行启动开发服务器

pipenv install python-dotenv
》》 如果安装了 python-dotenv, flask run 会自动从 .flaskenv 和 .env
手动设置的环境变量 > .env > .flaskenv
在 .env 和 .flaskenv 中的环境变量都是用等号连接的 key=value 形式

命令行中使用 flask run --host=0.0.0.0 命令，使 flask 监听所有外部请求
同样可以设置 FLASK_RUN_HOST 和 FLASK_RUN_PORT 来自定义可以访问的ip 和 对外端口
可以使用 内网穿透/端口转发 工具 来让外部访问
https://ngrok.com/
https://localtunnel.github.io/www/

在这一步,安装了 watchdog 来监控文件的变化，自动重载

# flask request 处理url中的内容
https://www.baidu.com/hello?name=gary
path        /hello
full_path   /hello?name=gary
host        www.baidu.com
host_url    http://www.baidu.com/
base_url    https://www.baidu.com/hello
url         https://www.baidu.com/hello?name=gary
url_root    https://www.baidu.com/
"""


# 模拟用户登陆认证
@app.route('/login')
def login():
    session["logged_in"] = True  # 写入session
    return redirect(url_for('say_hello'))


"""
session对象可以像字典一样操作，
我们向session中添加了一个 {"logged_in": True}
"""


@app.route('/admin')
def admin():
    if 'logged_in' not in session:
        abort(403)

    return "欢迎登录超级管理员页面"


@app.route('/logout')
def logout():
    if 'logged_in' in session:
        session.pop("logged_in")

    return redirect(url_for('say_hello'))


@app.route('/foo')
def foo():
    return "<h1>Foo page</h1><a href='%s'>Do Something</a>" % url_for('do_someting')


@app.route('/bar')
def bar():
    return "<h1>Bar page</h1><a href='%s'>Do Something</a>" % url_for('do_someting')


@app.route('/do_someting')
def do_someting():
    # 这里实现重定向回上一层的逻辑
    # return "<h1>Do something page</h1>"
    # return redirect(request.referrer or url_for('say_hello'))  # 通过referer的方式
    return redirect(request.args.get('next', url_for('say_hello')))



if __name__ == '__main__':
    app.run(debug=True)  # 这种方式已经不被推荐
