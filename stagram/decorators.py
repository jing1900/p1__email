from functools import wraps

from flask import flash, redirect, url_for
from flask_login import current_user
'''装饰器，验证是否已确认邮件'''
def check_confirmed(func):
	@wraps(func)
	def decorated_function(*args, **kwargs):
		if current_user.confirmed is False:
			flash('Please confirm your account!', 'warning')
			return redirect('/unconfirmed/')
		return func(*args, **kwargs)

	return decorated_function