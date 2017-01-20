from flask import Flask

app = Flask(__name__)

# 如果在调用Flask()创建应用时设置了instance_relative_config=True，app.config.from_pyfile()将查看在instance文件夹的特殊文件
app = Flask(__name__, instance_relative_config=True)

#加载默认配置
app.config.from_object('config.default')

# 从instance文件夹中加载配置
app.config.from_pyfile('config.py')

#将加载由环境变量APP_CONFIG_FILE指定的文件。这个环境变量的值应该是一个配置文件的绝对路径。
#APP_CONFIG_FILE 可做为linux启动脚本中的变量；例如：
APP_CONFIG_FILE='config/prod.py'
app.config.from_envvar('APP_CONFIG_FILE')



@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
