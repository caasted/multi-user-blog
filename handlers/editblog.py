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
	def get(self, post):
		entry = posts.Posts.get_by_id(long(post), parent=None)
		username = self.check_cookie()
		if username == entry.author:
			self.render("edit_blog.html", post=entry, blog=post)
		else:
			self.redirect("/login")

	def post(self, post):
		delete_request = self.request.get("delete")
		username = self.check_cookie()
		entry = posts.Posts.get_by_id(long(post), parent=None)
		if username == entry.author:
			if delete_request:
				db.delete(entry)
				time.sleep(1) # delay so page doesn't load before db updates
				self.redirect("/")
			else:
				subject = self.request.get("subject")
				content = self.request.get("content")
				if subject and content:
					entry.subject = subject
					entry.content = content
					entry.put()
					time.sleep(2) # delay so page doesn't load before db updates
					self.redirect("/post/%s" % post)
				else:
					error = "Needs both a subject and content! Use the delete button to remove both."
					self.redirect("/edit_blog/%s" % post)
		else:
			self.redirect("/login")

