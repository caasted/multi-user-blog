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
	def render_post(self, content="", error=""):
		username = self.check_cookie()
		page_url = self.request.url
		post_id = page_url.split('/')
		if len(post_id) > 0:
			post = posts.Posts.get_by_id(long(post_id[-1]), parent=None)
			query = 'select * from Comments where post_id = :post_id'
			comments = db.GqlQuery(query, post_id = long(post_id[-1]))
			self.render("post.html", posts=post, comments=comments, 
				content=content, error=error, username=username)
		else:
			self.redirect("/")

	def get(self):
		self.render_post()

	def post(self):
		content = self.request.get("content")
		error_msg = ""
		username = self.check_cookie()
		if username and content:
			page_url = self.request.url
			post_id = page_url.split('/')
			comment = comments.Comments(post_id=long(post_id[-1]), content=content, 
								author=username)
			comment.put()
			post = posts.Posts.get_by_id(long(post_id[-1]), parent=None)
			if post.comments:
				post.comments += 1
			else:
				post.comments = 1
			post.put()
			time.sleep(1) # delay so page doesn't load before db updates
			self.render_post()
		elif username:
			error = "We need some content!"
			self.render_post(error=error)
		else:
			self.redirect("/login")

