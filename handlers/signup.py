import re
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

class SignupHandler(handler.Handler):
	def get(self):
		username = self.check_cookie()
		if not username:
			self.render("signup.html")
		else:
			self.redirect("/")

	def valid_username(self, user_username):
		USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
		return user_username and USER_RE.match(user_username)

	def valid_password(self, user_password):
		PASSWORD_RE = re.compile(r"^.{3,20}$")
		return user_password and PASSWORD_RE.match(user_password)

	def valid_verify(self, user_password, user_verify):
		if user_password == user_verify:
			return True
		return None

	def valid_email(self, user_email):
		EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
		return not user_email or EMAIL_RE.match(user_email)

	def username_exists(self, user_username):
		user_match = db.GqlQuery('select * from Users where username = :name', 
									name=user_username)
		for result in user_match:
			if result.username == user_username:
				return True
		return None

	def post(self):
		username = self.check_cookie()
		if not username:
			user_username = self.request.get('username')
			user_password = self.request.get('password')
			user_verify = self.request.get('verify')
			user_email = self.request.get('email')

			username = self.valid_username(user_username)
			username_taken = self.username_exists(user_username)
			password = self.valid_password(user_password)
			verify = self.valid_verify(user_password, user_verify)
			email = self.valid_email(user_email)

			username_error = ""
			password_error = ""
			verification_error = ""
			email_error = ""

			if not (username):
				username_error = "That's not a valid username."
			elif (username_taken):
				username_error = "That username is not available."

			if not (password):
				password_error = "That wasn't a valid password."
				
			if not (verify):
				verification_error = "Your passwords didn't match."
				
			if not (email):
				email_error = "That's not a valid email."
				
			if not (username and password and verify and email and not username_taken):
				self.render("signup.html", username_error = username_error, 
											password_error = password_error, 
											verification_error = verification_error, 
											email_error = email_error, 
											username = user_username, 
											email = user_email)
			else:
				new_user = users.Users(username = user_username, 
								password = self.make_pw_hash(user_username, 
									user_password), 
								email = user_email)
				new_user.put()
				self.response.headers.add_header("Set-Cookie", 
					"username={0}; Path=/".format(
						self.make_secure_val(user_username)))
				self.redirect("/welcome")
		else:
			self.redirect("/")
