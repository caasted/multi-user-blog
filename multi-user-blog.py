import os
import jinja2
import re
import webapp2
import random
import string
import hashlib
import hmac
import time
from google.appengine.ext import db

# Database Models
class Users(db.Model):
	username = db.StringProperty(required = True)
	password = db.TextProperty(required = True)
	email = db.StringProperty()
	registered = db.DateTimeProperty(auto_now_add = True)

class Posts(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	author = db.StringProperty(required = True)
	likes = db.IntegerProperty(required = True)
	comments = db.IntegerProperty(required = True)

class Comments(db.Model):
	post_id = db.IntegerProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	author = db.StringProperty(required = True)

class Likes(db.Model):
	post_id = db.IntegerProperty(required = True)
	username = db.StringProperty(required = True)

# Page Handlers
class Handler(webapp2.RequestHandler):
	template_dir = os.path.join(os.path.dirname(__file__), 'templates')
	jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
									autoescape = True)

	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = self.jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

	def hash_str(self, s):
		SECRET = "imnotsosecret"
		return hmac.new(SECRET, s).hexdigest()

	def make_secure_val(self, s):
		return "%s|%s" % (s, self.hash_str(s))

	def check_secure_val(self, h):
		val = h.split('|')[0]
		if h == self.make_secure_val(val):
			return val

	def make_salt(self):
		return ''.join(random.choice(string.letters) for x in xrange(5))

	def make_pw_hash(self, name, pw, salt=None):
		if not salt:
			salt = self.make_salt()
		h = hashlib.sha256(name + pw + salt).hexdigest()
		return '%s,%s' % (h, salt)

	def valid_pw(self, name, pw, h):
		salt = h.split(',')[1]
		if self.make_pw_hash(name, pw, salt) == h:
			return True

class SignupHandler(Handler):
	def get(self):
		self.render("signup.html")

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
			new_user = Users(username = user_username, 
							password = self.make_pw_hash(user_username, 
								user_password), 
							email = user_email)
			new_user.put()
			self.response.headers.add_header("Set-Cookie", 
				"username={0}; Path=/".format(
					self.make_secure_val(user_username)))
			self.redirect("/welcome")

class LoginHandler(Handler):
	def get(self):
		self.render("login.html")

	def valid_login(self, username, password):
		user_match = db.GqlQuery('select * from Users where username = :name', 
									name=username)
		for result in user_match:
			if (result.username == username and 
				self.valid_pw(username, password, result.password)):
				return True
		return None

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')

		if self.valid_login(username, password):
			self.response.headers.add_header("Set-Cookie", 
				"username={0}; Path=/".format(self.make_secure_val(username)))
			self.redirect("/welcome")
		else:
			self.render("login.html", login_error = "Invalid login")

class LogoutHandler(Handler):
	def get(self):
		self.response.headers.add_header("Set-Cookie", "username=; Path=/")
		self.redirect("/login")

class WelcomeHandler(Handler):
	def get(self):
		cookie_data = self.request.cookies.get('username')
		if cookie_data:
			username = self.check_secure_val(cookie_data)
		else:
			username = None

		if username:
			self.render("welcome.html", username = username)
		else:
			self.redirect("/signup")

class UserListHandler(Handler):
	def get(self):
		cookie_data = self.request.cookies.get('username')
		if cookie_data:
			username = self.check_secure_val(cookie_data)
		else:
			username = None
		if username == 'admin':
			reg_users = db.GqlQuery('select * from Users')
			self.render('user_list.html', reg_users = reg_users)
		else:
			self.redirect("/")

class PostPage(Handler):
	def render_post(self, content="", error=""):
		cookie_data = self.request.cookies.get('username')
		if cookie_data:
			username = self.check_secure_val(cookie_data)
		else:
			username = None
		page_url = self.request.url
		post_id = page_url.split('/')
		if len(post_id) > 0:
			posts = Posts.get_by_id(long(post_id[-1]), parent=None)
			query = 'select * from Comments where post_id = :post_id'
			comments = db.GqlQuery(query, post_id = long(post_id[-1]))
			self.render("post.html", posts=posts, comments=comments, 
				content=content, error=error, username=username)
		else:
			self.redirect("/")

	def get(self):
		self.render_post()

	def post(self):
		content = self.request.get("content")
		error_msg = ""
		cookie_data = self.request.cookies.get('username')
		if cookie_data:
			username = self.check_secure_val(cookie_data)
		else:
			username = None
		
		if username and content:
			page_url = self.request.url
			post_id = page_url.split('/')
			comment = Comments(post_id=long(post_id[-1]), content=content, 
								author=username)
			comment.put()
			post = Posts.get_by_id(long(post_id[-1]), parent=None)
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

class EditBlogHandler(Handler):
	def get(self):
		blog = self.request.get("blog")
		post = Posts.get_by_id(long(blog), parent=None)
		cookie_data = self.request.cookies.get('username')
		if cookie_data:
			username = self.check_secure_val(cookie_data)
		else:
			username = None
		if username == post.author:
			self.render("edit_blog.html", post=post, blog=blog)
		else:
			self.redirect("/")

	def post(self):
		delete_request = self.request.get("delete")
		blog = self.request.get("blog")
		if delete_request:
			post = Posts.get_by_id(long(blog), parent=None)
			db.delete(post)
			time.sleep(1) # delay so page doesn't load before db updates
			self.redirect("/")
		else:
			subject = self.request.get("subject")
			content = self.request.get("content")
			if subject and content:
				post = Posts.get_by_id(long(blog), parent=None)
				post.subject = subject
				post.content = content
				post.put()
				time.sleep(2) # delay so page doesn't load before db updates
				self.redirect("/" + str(blog))
			else:
				error = "Needs both a subject and content! Use the delete button to remove both."
				self.redirect("/edit_blog?blog=%s" % blog)

class EditCommentHandler(Handler):
	def get(self):
		comment_id = self.request.get("comment_id")
		comment = Comments.get_by_id(long(comment_id), parent=None)
		cookie_data = self.request.cookies.get('username')
		if cookie_data:
			username = self.check_secure_val(cookie_data)
		else:
			username = None
		if username == comment.author:
			self.render("edit_comment.html", comment=comment, comment_id=comment_id)
		else:
			self.redirect("/")

	def post(self):
		delete_request = self.request.get("delete")
		comment_id = self.request.get("comment_id")
		if delete_request:
			post = Comments.get_by_id(long(comment_id), parent=None)
			blog = Posts.get_by_id(post.post_id, parent=None)
			blog.comments -= 1
			blog.put()
			db.delete(post)
			time.sleep(1) # delay so page doesn't load before db updates
			self.redirect("/" + str(post.post_id))
		else:		
			content = self.request.get("content")
			if content:
				post = Comments.get_by_id(long(comment_id), parent=None)
				post.content = content
				post.put()
				time.sleep(1) # delay so page doesn't load before db updates
				self.redirect("/" + str(post.post_id))
			else:
				error = "Needs content! Use the delete button to remove."
				comment = Comments.get_by_id(long(comment_id), parent=None)
				self.render("edit_comment.html", comment=comment, 
							comment_id=comment_id, error=error)

class MainPage(Handler):
	def render_front(self, subject="", content="", error=""):
		cookie_data = self.request.cookies.get('username')
		if cookie_data:
			username = self.check_secure_val(cookie_data)
		else:
			username = None
		posts = db.GqlQuery("select * from Posts order by created desc")
		self.render("front.html", subject=subject, content=content, error=error, 
			posts=posts, username=username)

	def get(self):
		self.render_front()

	def post(self):
		error_msg = ""
		cookie_data = self.request.cookies.get('username')
		if cookie_data:
			username = self.check_secure_val(cookie_data)
		else:
			username = None
		blog = self.request.get("blog")
		if blog and username:
			blog_entry = Posts.get_by_id(long(blog), parent=None)
			query = "select * from Likes where post_id = :blog and username = :user"
			like_record = db.GqlQuery(query, blog=long(blog), user=username)
			
			already_liked = None
			for users in like_record:
				if users.username == username:
					already_liked = True
					break
			if blog_entry.author != username and not already_liked:
				if self.request.get("like"):
					new_likes = blog_entry.likes + 1
					blog_entry.likes = new_likes
					blog_entry.put()
					new_like = Likes(post_id=long(blog), username=username)
					new_like.put()
				else:
					error_msg = "You have already unliked this post (or didn't like it before)"
			elif blog_entry.author != username and already_liked:
				if self.request.get("unlike"):
					new_likes = blog_entry.likes - 1
					blog_entry.likes = new_likes
					blog_entry.put()
					query = "select * from Likes where post_id = :blog and username = :username"
					remove_like = db.GqlQuery(query, blog=long(blog), username=username)
					db.delete(remove_like)
				else:
					error_msg = "You have already liked this post"
			else:
				error_msg = "You can't like/unlike on your own posts"
			
			time.sleep(1) # delay so page doesn't load before db updates
			self.render_front(error = error_msg)
		elif username:
			subject = self.request.get("subject")
			content = self.request.get("content")
			if subject and content:
				c = Posts(subject = subject, content = content, 
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

app = webapp2.WSGIApplication([('/', MainPage), 
								('/signup', SignupHandler), 
								('/welcome', WelcomeHandler), 
								('/reg_users', UserListHandler), 
								('/login', LoginHandler), 
								('/logout', LogoutHandler), 
								('/edit_blog', EditBlogHandler), 
								('/edit_comment', EditCommentHandler), 
								('/.*', PostPage), 
								], debug=True)
