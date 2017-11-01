#-*-encoding=UTF-8-*-
from qiniu import Auth,put_data
from stagram import app

#设置ak，sk，bucket_name
q = Auth(app.config['QINIU_ACCESS_KEY'], app.config['QINIU_SECRET_KEY'])
#要上传的空间
bucket_name = app.config['QINIU_BUCKET_NAME']
#domain
domain_prefix = app.config['QINIU_DOMAIN']

def qiniu_update_file(source_file,save_file_name):
	# 生成上传 Token，可以指定过期时间等
	token = q.upload_token(bucket_name, save_file_name)
	#print(source_file))
	localfile = '/home/j/桌面/cb6011c5b7274c7c375f011ca93c4a2f.jpg'
	#ret, info = put_file(token, save_file_name, localfile)
	#source_file.read_into(f)
	#这个七牛网的接口，适合于python2.7.3.5的版本有问题
	ret, info = put_data(token, save_file_name, source_file.stream)
	#上传成功，返回可访问的地址
	if info.status_code == 200:
		return domain_prefix + save_file_name
	return None