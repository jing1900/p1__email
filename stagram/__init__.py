#-*-encoding=UTF-8-*-
'''放导出信息的'''

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail, Message

#先把app建起来
app = Flask(__name__)
app.jinja_env.line_statement_prefix = '#'
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
#设置config
app.config.from_pyfile('app.conf')
app.secret_key = 'jing'
#定义数据库
db = SQLAlchemy(app)
#login_manager初始化
login_manager = LoginManager(app)
#login_view定义，也就是如果没有登录的话，会默认跳转到这个页
login_manager.login_view = '/reg_login_page/'
mail = Mail(app)




#导出view
from stagram import views
from stagram import models