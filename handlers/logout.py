import webapp2
import os
import jinja2
import hmac
import hashlib
import random
import string
from . import handler

class LogoutHandler(handler.Handler):
	def get(self):
		username = self.check_cookie()
		if username:
			self.response.headers.add_header("Set-Cookie", "username=; Path=/")
		self.redirect("/login")

