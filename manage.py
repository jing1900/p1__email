#-*- encoding=UTF-8 -*-
from stagram import app,db
from stagram.models import User
from stagram.models import Image,Comment
import random
import unittest
from sqlalchemy import or_,and_
'''脚本'''
#导入manager
from flask_script import Manager


manager = Manager(app)

@manager.command
def run_test():
	#每次跑之前，清空下数据库
	db.drop_all()
	db.create_all()
	#让其自行从目录里找测试用例，该目录下以test开头的
	tests = unittest.TestLoader().discover('./')
	#跑这个测试用例
	unittest.TextTestRunner().run(tests)

#从服务器上获取图片
def get_image():
	return 'http://images.nowcoder.com/head/' + str(random.randint(0, 1000)) + 'm.png'
@manager.command
def init_database():
	'''前面这两行是为了方便演示，正常情况下，这两行是要删掉的，只在第一次运行时创建表'''
	#先删除所有表
	db.drop_all()
	#再把所有表创建起来,这里是把所有定义好的数据类，根据类名和变量名创建好.可以在终端里面这样跑python manage.py init_database
	#在终端执行完这个，就可以用deraidb查看，test数据库里面已经被创建了一个名叫table的表。一切都很顺利
	db.create_all()
	'''增--先添加100个用户'''
	for i in range(1,100):
		#这样初始化之后，盐为空，confirmed为0，confirmed为null
		db.session.add(User('User'+str(i),str(i)+'@qq.com','pw'+str(i),False))
		#为每个人添加三张图片
		for j in range(0, 3):  # 每人发三张图
			# 这里user_id应该为i，因为循环是从1开始的，而自增是从1开始的
			db.session.add(Image(get_image(), i ))
			#每张图片加三条评论
			for k in range(0,3):
				db.session.add(Comment('this is a comment'+str(k),3*(i-1)+j+1,i))

	db.session.commit()#数据库事务就是没提交时，啥都不是

	'''更新,50-100内的偶数用户'''
	for i in range(50,100,2):
		user = User.query.get(i)
		user.username = '[*]'+User.username
	#直接用update方式更新，update的参数是一个字典,更新51-100之间的奇数
	for i in range(0, 100, 10):
		# 通过update函数
		User.query.filter_by(id=i + 1).update({'username': '牛客新' + str(i)})

	db.session.commit()

	'''删'''
	#删除从50-100的奇数评论
	for i in range(50,100,2):
		comment = Comment.query.get(i+1)
		db.session.delete(comment)
	db.session.commit()

	'''查'''
	#查全部
	#print(User.query.all())
	#查第三个
	#print(User.query.get(3))
	#有条件的查询
	#print(User.query.filter_by(id = 5).first())
	#根据id将序取，然后偏移一下，取两个
	#print(User.query.order_by(User.id.desc()).offset(1).limit(2).all())
	#打印以0结尾的用户名
	#print(User.query.filter(User.username.endswith('0')).limit(3).all())
	#组合查询.这里如果去掉之后的all（），就会打印数据库查询语句
	#print(User.query.filter(or_(User.id == '88',User.id == '99')).all())
	#print(User.query.filter(and_(User.id > '88', User.id < '90')).all())
	#返回第一个或者报404错误
	#print(User.query.filter(and_(User.id > '88', User.id < '90')).first_or_404())
	#分页查询
	#print(User.query.paginate(page=1,per_page=10).items)
	#逆序后分页查询
	#print(User.query.order_by(User.id.desc()).paginate(page=1, per_page=10).items)
	#1对多的查询，这里以第一个用户为例
	#user1 = User.query.get(1)
	#print(user1.images)#这是因为我们已经把user和images表关联起来了，在image表中，可以容易的根据外键来查到对应的表
	#直接这样查询是没有结果的，我们需要在user里制定backref.images = db.relationship('Image',backref='user',lazy='dynamic')
	#image1 = Image.query.get(1)
	#print(image1.user)

	#为第100个用户增加至10张图片
	for i in range(0,7):
		db.session.add(Image(get_image(), 99))
	db.session.commit()


if __name__ == '__main__':
	manager.run()