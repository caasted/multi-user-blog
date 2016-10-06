import webapp2
import os
import jinja2
import hmac
import hashlib
import random
import string
import time
from google.appengine.ext import db
from models import *
from . import handler, like

class MainPage(handler.Handler, like.LikeHandler):
	def render_front(self, subject="", content="", error=""):
		username = self.check_cookie()
		posts = db.GqlQuery("select * from Posts order by created desc")
		self.render("front.html", subject=subject, content=content, error=error, 
			posts=posts, username=username)

	def get(self):
		self.render_front()

	def post(self):
		username = self.check_cookie()
		blog = self.request.get("blog")
		if blog and username:
			error = self.process_like_button(blog, username)
			time.sleep(1) # delay so page doesn't load before db updates
			self.render_front(error = error)
		elif username:
			subject = self.request.get("subject")
			content = self.request.get("content")
			if subject and content:
				c = posts.Posts(subject = subject, content = content, 
					author = username, likes = 0, comments = 0)
				c.put()
				newpost = c.key().id()
				time.sleep(1) # delay so page doesn't load before db updates
				self.redirect("/" + str(newpost))
			else:
				error = "We need both a subject and some content!"
				self.render_front(subject, content, error)
		else:
			self.redirect("/login")

