'''生成token'''
from itsdangerous import URLSafeTimedSerializer

from stagram import app

def generate_confirmation_token(email):
	# 过URLSafeTimedSerializer用在用户注册时得到的email地址生成一个令牌。
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])

#确认令牌之后，在confirm_token()函数中，我们可以用loads()方法，
# 它接管令牌和其过期时间——一个小时（3600秒）内有效——作为参数。
# 只要令牌没过期，那它就会返回一个email。
def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except:
        return False
    return email