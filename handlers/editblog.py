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

class EditBlogHandler(handler.Handler):
	def get(self):
		blog = self.request.get("blog")
		post = posts.Posts.get_by_id(long(blog), parent=None)
		username = self.check_cookie()
		if username == post.author:
			self.render("edit_blog.html", post=post, blog=blog)
		else:
			self.redirect("/login")

	def post(self):
		delete_request = self.request.get("delete")
		blog = self.request.get("blog")
		username = self.check_cookie()
		post = posts.Posts.get_by_id(long(blog), parent=None)
		if username == post.author:
			if delete_request:
				db.delete(post)
				time.sleep(1) # delay so page doesn't load before db updates
				self.redirect("/")
			else:
				subject = self.request.get("subject")
				content = self.request.get("content")
				if subject and content:
					post = posts.Posts.get_by_id(long(blog), parent=None)
					post.subject = subject
					post.content = content
					post.put()
					time.sleep(2) # delay so page doesn't load before db updates
					self.redirect("/" + str(blog))
				else:
					error = "Needs both a subject and content! Use the delete button to remove both."
					self.redirect("/edit_blog?blog=%s" % blog)
		else:
			self.redirect("/login")

