import webapp2
import os
import jinja2
import hmac
import hashlib
import random
import string
from . import handler

class WelcomeHandler(handler.Handler):
	def get(self):
		username = self.check_cookie()
		if username:
			self.render("welcome.html", username = username)
		else:
			self.redirect("/signup")

