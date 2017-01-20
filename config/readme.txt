config/default.py	默认值，适用于所有的环境或交由具体环境进行覆盖。举个例子，在config/default.py中设置DEBUG = False，在config/development.py中设置DEBUG = True。
config/development.py	在开发环境中用到的值。这里你可以设定在localhost中用到的数据库URI链接。
config/production.py	在生产环境中用到的值。这里你可以设定数据库服务器的URI链接，而不是开发环境下的本地数据库URI链接。
config/staging.py	在你的开发过程中，你可能需要在一个模拟生产环境的服务器上测试你的应用。你也许会使用不一样的数据库，想要为稳定版本的应用替换掉一些配置。