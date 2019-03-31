#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
from urllib.parse import urljoin, urlparse

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


def is_safe_url(target):
    ref_url = urlparse(request.host_url)  # 通过 request.host_url 获取程序主机的 url
    test_url = urlparse(urljoin(request.host_url, target))  # 通过 urljoin 将目标 url 转换成绝对 url，通过urlparse 进行验证
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def redirect_back(default='say_hello', **kwargs):  # 定义的重定向回上一个页面的工具方法
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return redirect(target)

    return redirect(url_for(default, **kwargs))


@app.route('/do_someting')
def do_someting():
    # 这里实现重定向回上一层的逻辑
    # return "<h1>Do something page</h1>"
    # return redirect(request.referrer or url_for('say_hello'))  # 通过referer的方式
    # return redirect(request.args.get('next', url_for('say_hello')))
    return redirect_back()


"""
返回局部数据的方式 ajax

1. 纯文本或 html 页面

@app.route('/comments/<int:post_id>')
def comments(post_id):
    ...
    return render_template('comments.html')
    
2. json 数据  json数据可以直接在 JavaScript中 操作

@app.route('/profile/<int:user_id>')
def get_profile(user_id):
    ...
    return jsonify(username=username, bio=bio)
    
3. 空值 

@app.route('/post/delete/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    ...
    return '', 204

4. 异步加载长文章
文章正文下方有个加载更多的按钮，点击加载更多，获取更多文章加载到已显示的文章下方
"""

from jinja2.utils import generate_lorem_ipsum


@app.route('/post')
def show_post():
    post_body = generate_lorem_ipsum(n=2)

    return """
    <h1>A very long post</h1>
    <div class='body'>%s</div>
    <button id="load">Load More</button>
    <script src="https://code.jquery.com/jquery-3.3.1.min.js"></script>
    <script type='text/javascript'>
    $( function (){
        $('#load').click( function (){
            $.ajax({
                url: '/more',  // 目标url
                type: 'get',  // 请求的方式
                success: function(data){  // 返回 2xx 响应后回调的函数
                    $('.body').append(data);  // 加返回的响应插入到页面中
                }
            })
        })
    })
    </script>
    """ % post_body


@app.route('/more')
def more():
    return generate_lorem_ipsum(n=1)


if __name__ == '__main__':
    app.run(debug=True)  # 这种方式已经不被推荐
