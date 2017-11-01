import unittest
#导入工程
from stagram import app

'''单元测试类,继承unittest的TestCase
一旦run这个测试用例，就会自动把里面以test开头的方法作为测试用例跑
其执行顺序是，setup-test1-teardown,setup-test2-teardown

因此：
1，初始化数据，这个过程在setup里执行
2，执行测试业务，自行写执行函数
3，验证测试数据（assert，断言），这个过程在test函数里
3,清理数据，这个过程放在teardown里'''

'''这里我们对首页做个测试'''
class stagramTest(unittest.TestCase):

	#每次跑单元测试时，它都会跑
	def setUp(self):
		print('setup')
		#测试模式
		app.config['TESTING'] = True
		#把app保存下来
		self.app = app.test_client()


	def tearDown(self):
		print('tearDown')

	def register(self,username,password):
		return self.app.post('/reg/',data={'username':username,'password':password},follow_redirects=True)

	def login(self,username,password):
		return self.app.post('/login/',data={"username": username, "password": password},follow_redirects=True)

	def logout(self):
		return self.app.get('/logout/')

	#测试注册，登录，测试前，先把注册登录都写好，在上面
	def test_reg_login_logout(self):
		#测试注册这里执行成功，会返回一个http response,故可以用状态码来验证
		assert self.register('jing1','1').status_code ==200
		#注册成功后，判断用户名是否在首页的标题上
		assert bytes('-jing1',encoding="utf8") in self.app.open('/').data
		#登出
		self.logout()
		#再次测试，这里应该不在
		assert bytes('-jing1',encoding="utf8") not in self.app.open('/').data
		#登入
		self.login("jing1", "1")
		#再判断
		assert bytes('-jing1',encoding="utf8") in self.app.open('/').data


	#测试profile
	def test_profile(self):
		#这里由于没登录，所以一定会跳转到登录注册界面，因此会response
		r = self.app.open('/profile/3/',follow_redirects=True)
		#判断response状态码
		assert r.status_code == 200
		#查看页面元素里有没有password这个关键词
		assert bytes('password',encoding='utf8') in r.data
		#注册后，再进行判断
		assert self.register('jing2','2')
		#再打开一个用户,判断用户名是否在这个页面，也就是不进行跳转到登录注册页面了
		assert bytes('jing2',encoding='utf8') in self.app.open('/profile/1/', follow_redirects=True).data