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

class EditCommentHandler(handler.Handler):
	def get(self, post):
		comment = comments.Comments.get_by_id(long(post), parent=None)
		username = self.check_cookie()
		if username == comment.author:
			self.render("edit_comment.html", comment=comment, comment_id=post)
		else:
			self.redirect("/login")

	def post(self, post):
		delete_request = self.request.get("delete")
		username = self.check_cookie()
		comment = comments.Comments.get_by_id(long(post), parent=None)
		if username == comment.author:
			if delete_request:
				blog = posts.Posts.get_by_id(comment.post_id, parent=None)
				blog.comments -= 1
				blog.put()
				db.delete(comment)
				time.sleep(1) # delay so page doesn't load before db updates
				self.redirect("/post/" + str(blog.key().id()))
			else:		
				content = self.request.get("content")
				if content:
					comment.content = content
					comment.put()
					time.sleep(1) # delay so page doesn't load before db updates
					self.redirect("/post/" + str(comment.post_id))
				else:
					error = "Needs content! Use the delete button to remove."
					self.render("edit_comment.html", comment=post, 
								comment_id=post, error=error)
		else:
			self.redirect("/login")
