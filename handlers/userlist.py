import webapp2
import os
import jinja2
import hmac
import hashlib
import random
import string
from google.appengine.ext import db
from . import handler
from models import *

class UserListHandler(handler.Handler):
	def get(self):
		username = self.check_cookie()
		if username == 'admin':
			reg_users = db.GqlQuery('select * from Users')
			self.render('user_list.html', reg_users = reg_users)
		else:
			self.redirect("/")

