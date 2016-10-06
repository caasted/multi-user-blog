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
from . import handler

class PostPageHandler(handler.Handler):
	def render_post(self, post, content="", error=""):
		username = self.check_cookie()
		entry = posts.Posts.get_by_id(long(post), parent=None)
		query = 'select * from Comments where post_id = :post_id'
		comments = db.GqlQuery(query, post_id = long(post))
		self.render("post.html", posts=entry, comments=comments, 
			content=content, error=error, username=username)

	def get(self, post):
		self.render_post(post)

	def post(self, post):
		content = self.request.get("content")
		error_msg = ""
		username = self.check_cookie()
		if username and content:
			comment = comments.Comments(post_id=long(post), content=content, 
								author=username)
			comment.put()
			entry = posts.Posts.get_by_id(long(post), parent=None)
			if entry.comments:
				entry.comments += 1
			else:
				entry.comments = 1
			entry.put()
			time.sleep(1) # delay so page doesn't load before db updates
			self.render_post(post=post)
		elif username:
			error = "You cannot post blank comments."
			self.render_post(post=post, error=error)
		else:
			self.redirect("/login")

