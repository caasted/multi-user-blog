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
	def get(self):
		comment_id = self.request.get("comment_id")
		comment = comments.Comments.get_by_id(long(comment_id), parent=None)
		username = self.check_cookie()
		if username == comment.author:
			self.render("edit_comment.html", comment=comment, comment_id=comment_id)
		else:
			self.redirect("/login")

	def post(self):
		delete_request = self.request.get("delete")
		comment_id = self.request.get("comment_id")
		username = self.check_cookie()
		post = comments.Comments.get_by_id(long(comment_id), parent=None)
		if username == post.author:
			if delete_request:
				blog = posts.Posts.get_by_id(post.post_id, parent=None)
				blog.comments -= 1
				blog.put()
				db.delete(post)
				time.sleep(1) # delay so page doesn't load before db updates
				self.redirect("/" + str(post.post_id))
			else:		
				content = self.request.get("content")
				if content:
					post.content = content
					post.put()
					time.sleep(1) # delay so page doesn't load before db updates
					self.redirect("/" + str(post.post_id))
				else:
					error = "Needs content! Use the delete button to remove."
					self.render("edit_comment.html", comment=post, 
								comment_id=comment_id, error=error)
		else:
			self.redirect("/login")
