import webapp2
import os
import jinja2
import hmac
import hashlib
import random
import string
from google.appengine.ext import db
from models import *
from . import handler

class LoginHandler(handler.Handler):
	def get(self):
		self.render("login.html")

	def valid_login(self, username, password):
		user_match = db.GqlQuery('select * from Users where username = :name', 
									name=username)
		for result in user_match:
			if (result.username == username and 
				self.valid_pw(username, password, result.password)):
				return True
		return None

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')
		if self.valid_login(username, password):
			self.response.headers.add_header("Set-Cookie", 
				"username={0}; Path=/".format(self.make_secure_val(username)))
			self.redirect("/welcome")
		else:
			self.render("login.html", login_error = "Invalid login")

