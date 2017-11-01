#-*-encoding=UTF-8-*-

from flask import render_template,redirect,request,flash,get_flashed_messages,send_from_directory,url_for
from .models import Image,User,Comment
from flask_login import login_user,logout_user,current_user,login_required
#随机数，加密
import random,hashlib,json,uuid,os
from stagram import db,mail
from .token import generate_confirmation_token, confirm_token
from .qiniusdk import qiniu_update_file
import re
from flask_mail import Mail, Message
import datetime
from .decorators import check_confirmed


'''视图'''
#这里用了flash，就需要在init里加一个secretkey
def redirect_with_msg(target,msg,category):
	if msg != None:
		flash(msg,category=category)
	return redirect(target)

from stagram import app


@app.route('/')
def index():
	paginate = Image.query.order_by(db.desc(Image.id)).paginate(page=1,per_page=10,error_out=False)
	#images = Image.query.order_by('id desc').limit(10).all()
	return render_template('index.html',has_next = paginate.has_next,images = paginate.items)
@app.route('/image/<int:image_id>/')
def image_detail(image_id):
	image = Image.query.get(image_id)
	if image == None:
		return redirect('/')
	return render_template('pageDetail.html',image = image)


@app.route('/profile/<int:user_id>/')
@login_required#访问权限设置
@check_confirmed
def user_detail(user_id):
	user = User.query.get(user_id)
	if user == None:
		return redirect('/')
	#这里我们对用户上传的图片，做一个分页查询，默认显示三个，点击更多，再用ajax方式加载更多。
	paginate = Image.query.filter_by(user_id = user.id).paginate(page=1,per_page=3,error_out=False)
	return render_template('profile.html',user = user,has_next = paginate.has_next,images = paginate.items)

#ajax方式传输数据
@app.route('/profile/images/<int:user_id>/<int:page>/<int:per_page>/')
def user_image(user_id,page,per_page):
	paginate = Image.query.filter_by(user_id=user_id).paginate(page=page, per_page=per_page, error_out=False)

	#此外，页面更多更多到最后肯定不能再展开了，所以那个按钮要消失。因此，这里我们后台需要提供一个参数has_next
	map = {'has_next':paginate.has_next}
	images=[]
	for image in paginate.items:
		imagevo = {'id':image.id,'url':image.url,'comment_count':len(image.comments)}
		images.append(imagevo)
	map['images'] = images
	return json.dumps(map)


@app.route('/reg_login_page/')
def reg_login():
	#这里用来获取注册时反馈的flash
	msg = ''
	for m in get_flashed_messages(with_categories=False,category_filter=['reg_log']):
		msg = msg+m
	#这里我们增加一个字段next，来记录登录后想跳转到的界面.同时，我们需要在login界面里面加一个隐藏字段，来获取next
	#再同时，我们需要在login函数里面做一个判断，如果有next字段，则跳转至next
	return render_template('login.html',msg=msg,next = request.values.get('next'))

@app.route('/reg/',methods={'post','get'})
def reg():
	#request.args:url里面的参数
	#request.form:body里面的数据，也可以用value
	username = request.values.get('username').strip()
	email = request.values.get('email').strip()
	#注册时设置是否确认邮箱为false，即在插入数据库表时，该值为0
	confirmed = False
	#这里为了加强密码，这里我们在model的user里面加了盐.改完记得把数据库重新初始化一下
	password = request.values.get('password').strip()

	#判断是否为空
	if username=='' or email =='' or password =='' :
		return redirect_with_msg('/reg_login_page/',u'用户名或邮箱或密码为空',category='reg_log')
	#判断是否是邮箱格式
	if re.match("[a-zA-Z0-9]+\@+[a-zA-Z0-9]+\.+[a-zA-Z]", email) == None:
		return redirect_with_msg('/reg_login_page/',u'邮箱格式不正确',category='reg_log')

	#判断是否重复,重复的话，flash一个消息过去。因为以后很多地方redirect的时候要带flash,所以我们特意打包一个函数在view的最上面
	user = User.query.filter_by(username = username).first()
	if user != None:
		return redirect_with_msg('/reg_login_page/',u'用户名已注册',category='reg_log')
	#判断邮箱是否已注册
	user = User.query.filter_by(email=email).first()
	if user != None:
		return redirect_with_msg('/reg_login_page/', u'邮箱已注册', category='reg_log')

	#生成盐
	salt = '.'.join(random.sample('0123456789abcdefgABCDEFG',10))
	#加密
	m = hashlib.md5()
	#这里改版之后，需要加encode
	m.update(password.encode("utf8")+salt.encode("utf8"))
	#加密之后的16进制字符串作为密码
	password = m.hexdigest()
	#print(salt)

	##更多判断做完之后，将用户插入数据库,默认确认状态为0
	user = User(username,email,password,0,0,salt)

	#def __init__(self, username, email, password, confirmed, confirmed_on=None, salt=''):
	db.session.add(user)
	db.session.commit()

	#获取token
	token = generate_confirmation_token(email)
	confirm_url = url_for('confirm_email', token=token, _external=True)
	html = render_template('active.html', confirm_url=confirm_url)

	#这里发验证邮件，传入user参数
	msg = Message('Confirm Your Account', sender='2515418348@qq.com', recipients=[str(email)])
	msg.html = html
	mail.send(msg)

	#登入用户，但转入未邮件验证的页面
	login_user(user)
	return redirect('/unconfirmed/')
	#return redirect_with_msg('/reg_login_page/', u'验证邮件已发送', category='reg_log')

	# 注册完之后自动登录
	#login_user(user)

	# 判断页面是否有next字段传入
	#next = request.values.get('next')
	#if next != None and next.startswith('/') > 0:
		#return redirect(next)

	#没有next就跳转至首页
	#return redirect('/')
#待确认页面
@app.route('/unconfirmed/')
@login_required
def unconfirmed():
	if current_user.confirmed:
		return redirect('/')
	flash('Please confirm your account!', 'warning')
	return render_template('/unconfirmed.html')

#邮件确认
'''现在我们通过令牌调用confirm_token()函数。
如果成功，我们更新用户，把email_confirmed属性改成True， 设置datetime为验证发生的时间。
还有，要是用户已经进行过一遍验证过程了——而且已经验证了——我们要提醒用户这点。'''
@app.route('/confirm/<token>')
@login_required
def confirm_email(token):
	#print('run')
	try:
		email = confirm_token(token)
		#print(email)
	except:
		flash('The confirmation link is invalid or has expired.', 'danger')
	user = User.query.filter_by(email=email).first_or_404()
	#print(user)
	if user.confirmed:
		flash('Account already confirmed. Please login.', 'success')
	else:
		#print(user)
		user.confirmed = True
		user.confirmed_on = datetime.datetime.now()
		db.session.add(user)
		db.session.commit()
		flash('You have confirmed your account. Thanks!', 'success')
	return redirect('/')

@app.route('/login/',methods={'post','get'})
def login():
	username = request.values.get('username').strip()
	password = request.values.get('password').strip()

	# 判断是否为空
	if username == '' or password == '':
		return redirect_with_msg('/reg_login_page/', u'用户名或密码为空', category='reg_log')
	#看用户是否存在
	user = User.query.filter_by(username = username).first()
	if user == None:
		return redirect_with_msg('/reg_login_page/', u'用户不存在', category='reg_log')
	#验证密码
	m =hashlib.md5()
	#重新加密
	m.update(password.encode("utf8")+user.salt.encode("utf8"))

	#加密后的与数据库里的做比对
	if m.hexdigest() != user.password:
		return redirect_with_msg('/reg_login_page/', u'密码错误', category='reg_log')

	login_user(user)

	# 判断页面是否有next字段传入
	next = request.values.get('next')
	if next != None and next.startswith('/') >0:
		return redirect(next)
	#没有next就跳转至首页
	return redirect('/')

#将图片保存至本地
def save_to_local(file,filename):
	file_dir = app.config['UPLOAD_DIR']
	#存贮文件
	file.save(os.path.join(file_dir,filename))
	#返回访问地址,可以通过这个地址从浏览器访问该存贮文件
	return '/image/'+filename

#显示图片,根据上面函数的返回地址定义
@app.route('/image/<filename>/')
def show_image(filename):
	return send_from_directory(app.config['UPLOAD_DIR'],filename)

#这里必须用post方法
@app.route('/upload/',methods={'post'})
def upload():
	#获取上传文件的信息
	file = request.files['file']
	#获取多张图片
	#file1 = request.files['file1']

	#上传至服务器
	#后缀名验证（放在app.conf里）
	file_ext = ''
	if file.filename.find('.') > 0:
		file_ext = file.filename.rsplit('.',1)[1].strip().lower()

	if file_ext in app.config['ALLOWED_EXT']:
		#保存文件，重新定义文件名，避免不规范
		filename = str(uuid.uuid1()).replace('-','')+'.'+file_ext
		#再调用自己定义的函数,存贮至本地
		url = save_to_local(file,filename)
		#url = qiniu_update_file(file,filename)
		#入数据库
		if url != None:
			db.session.add(Image(url,current_user.id))
			db.session.commit()

	#上传完返回用户首页
	return redirect('/profile/%d'%current_user.id)


@app.route('/logout/')
def logout():
	logout_user()
	return redirect('/')

@app.route('/addcomment/',methods={'post'})
@login_required
def add_comment():

	image_id = int(request.values['image_id'])
	content = request.values['content']
	comment = Comment(content,image_id,current_user.id)
	db.session.add(comment)
	db.session.commit()
	dic = {'code':0,'id': comment.id,'content': comment.content,'username': comment.user.username,'user_id': comment.user_id}
	return json.dumps(dic)

@app.route('/addindexcomment/',methods={'post'})
@login_required
def add_index_comment():
	image_id = int(request.values['image_id'])
	content = request.values['content']
	comment = Comment(content,image_id,current_user.id)
	db.session.add(comment)
	db.session.commit()
	dic = {'code':0,'id': comment.id,'content': comment.content,'username': comment.user.username,'user_id': comment.user_id,'image_id':comment.image_id}
	return json.dumps(dic)


@app.route('/index/images/<int:page>/<int:per_page>/')
def index_images(page, per_page):
	#逆序读取分页
	paginate = Image.query.order_by(db.desc(Image.id)).paginate(page=page, per_page=per_page, error_out=False)
	#返回map
	map = {'has_next': paginate.has_next}
	images = []
	#遍历分页中的图片
	for image in paginate.items:
		comment_user_username = []
		comment_user_id = []
		comment_content = []
		for comments_i in image.comments:
			comment_user_username.append(comments_i.user.username)
			comment_user_id.append(comments_i.user.id)
			comment_content.append(comments_i.content)
		imgvo = {'id': image.id,
			 'url': image.url,
			 'imageusername': image.user.username,
			 'comment_count': len(image.comments),
			 'user_id': image.user_id,
			 'head_url': image.user.head_url,
			 'created_date': str(image.created_data),
			 'comment_user_username': comment_user_username,
			 'comment_user_id': comment_user_id,
			 'comment_content': comment_content}
		images.append(imgvo)

	map['images'] = images
	return json.dumps(map)
