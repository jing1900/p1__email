#-*- encoding=UTF-8 -*-
from stagram import app,login_manager
from stagram.models import User
'''把网站跑起来的时候，run这个'''

if __name__ == '__main__':

	app.run(debug=True)