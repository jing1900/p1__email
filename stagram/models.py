#-*-encoding=UTF-8-*-
'''数据模型，有问题就去查官方文档，上面什么都有
真的没有比官方文档更好的东西了'''

from stagram import db,login_manager
from datetime import datetime
import random
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from stagram import app

#评论类
class Comment(db.Model):
	#评论id
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	#内容
	content = db.Column(db.String(1024))
	#评论是属于那张图片的
	image_id = db.Column(db.Integer,db.ForeignKey('image.id'))
	#评论是谁发的
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
	#设计一个字段，来表明当前实体属于什么状态
	status = db.Column(db.Integer,default=0)#0,正常，1，被删除
	#将评论和用户关联起来
	user = db.relationship('User')

	def __init__(self, content, image_id, user_id):
		self.content = content
		self.image_id = image_id
		self.user_id = user_id

	def __repr__(self):
		return '<comment %d: %s>'%(self.id,self.content)
#instagram里面的每个图像和其评论点赞和一些其他属性
class Image(db.Model):
	#图片id
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	#url
	url = db.Column(db.String(512))
	#创建时间
	created_data = db.Column(db.DateTime)
	#图片是那个user id发的,这里的user_id是user的外键
	user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
	#评论关联起来
	comments = db.relationship('Comment')

	def __init__(self,url,user_id):
		self.url = url
		self.created_data = datetime.now()
		self.user_id = user_id

	def __repr__(self):
		return '<Pic %d: %s>'%(self.id,self.url)



class User(db.Model):
	# __tablename__ = 'myuser' 指定表名字,不指定就默认类名小写
	'''这里类里的一个变量，就表示表中的一列，具体怎样跟数据库做交互见manage.py'''
	#user id,指明类型，是否主键和是否自动增长
	id = db.Column(db.Integer,primary_key=True,autoincrement=True)
	#用户名，指明类型，和非重复
	username = db.Column(db.String(80),unique=True)
	#邮箱
	#email = db.Column(db.String(80))
	email = db.Column(db.String(80), unique=True, nullable=False)
	#密码
	password = db.Column(db.String(32))

	#头像
	head_url = db.Column(db.String(256))
	#是否邮箱确认
	confirmed = db.Column(db.Boolean, nullable=False, default=False)
	#邮箱确认时间
	confirmed_on = db.Column(db.DateTime, nullable=True)
	# 盐
	salt = db.Column(db.String(32))

	#这里我们怎么将每个人发的图片关联起来呢
	images = db.relationship('Image',backref='user',lazy='dynamic')

	'''定义构造函数'''
	def __init__(self,username,email,password,confirmed,confirmed_on=None,salt =''):
		self.username = username
		self.email = email
		self.password = password
		self.confirmed = confirmed
		self.confirmed_on = confirmed_on
		self.salt = salt
		#这里头像先用牛客网给出的1000张图片之一，中间的变量是0-1000之间随机一个整数
		self.head_url = 'http://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 't.png'

	def __repr__(self):
		return '<User %d : %s>'%(self.id,self.username)
	#认证
	def is_authenticated(self):
		print('is_authenticated')
		return True
	#激活
	def is_active(self):
		print('is_active')
		return True

	#匿名
	def is_anonymous(self):
		print('is_anonymous')
		return False

	#这里不能加@property
	def get_id(self):
		print('get_id')
		return self.id



@login_manager.user_loader
def load_user(user_id):
	return User.query.get(user_id)