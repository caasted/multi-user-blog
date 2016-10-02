import os
import jinja2
import re
import webapp2
import random
import string
import hashlib
import hmac

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), 
								autoescape = True)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(user_username):
	return user_username and USER_RE.match(user_username)

PASSWORD_RE = re.compile(r"^.{3,20}$")
def valid_password(user_password):
	return user_password and PASSWORD_RE.match(user_password)

def valid_verify(user_password, user_verify):
	if user_password == user_verify:
		return True
	return None

EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(user_email):
	return not user_email or EMAIL_RE.match(user_email)

def username_exists(user_username):
	user_match = db.GqlQuery('select * from Users where username = :name', 
								name=user_username)
	for result in user_match:
		if result.username == user_username:
			return True
	return None

def valid_login(username, password):
	user_match = db.GqlQuery('select * from Users where username = :name', 
								name=username)
	for result in user_match:
		if (result.username == username and 
			valid_pw(username, password, result.password)):
			return True
	return None

SECRET = "imnotsosecret"
def hash_str(s):
	return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
	return "%s|%s" % (s, hash_str(s))

def check_secure_val(h):
	val = h.split('|')[0]
	if h == make_secure_val(val):
		return val

def make_salt():
	return ''.join(random.choice(string.letters) for x in xrange(5))

def make_pw_hash(name, pw, salt=None):
	if not salt:
		salt = make_salt()
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return '%s,%s' % (h, salt)

def valid_pw(name, pw, h):
	salt = h.split(',')[1]
	if make_pw_hash(name, pw, salt) == h:
		return True

class Users(db.Model):
	username = db.StringProperty(required = True)
	password = db.TextProperty(required = True)
	email = db.StringProperty(required = False)
	registered = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class MainPage(Handler):
	def get(self):
		self.redirect("/signup")

class SignupHandler(Handler):
	def get(self):
		self.render("signup.html")

	def post(self):
		user_username = self.request.get('username')
		user_password = self.request.get('password')
		user_verify = self.request.get('verify')
		user_email = self.request.get('email')

		username = valid_username(user_username)
		password = valid_password(user_password)
		verify = valid_verify(user_password, user_verify)
		email = valid_email(user_email)

		username_taken = username_exists(user_username)

		if not (username):
			username_error = "That's not a valid username."
		elif (username_taken):
			username_error = "That username is not available."
		else:
			username_error = ""

		if not (password):
			password_error = "That wasn't a valid password."
		else:
			password_error = ""
			
		if not (verify):
			verification_error = "Your passwords didn't match."
		else:
			verification_error = ""
			
		if not (email):
			email_error = "That's not a valid email."
		else:
			email_error = ""
			
		if not (username and password and verify and email and not username_taken):
			self.render("signup.html", username_error = username_error, 
										password_error = password_error, 
										verification_error = verification_error, 
										email_error = email_error, 
										username = user_username, 
										email = user_email)
		else:
			new_user = Users(username = user_username, 
							password = make_pw_hash(user_username, user_password), 
							email = user_email)
			new_user.put()
			self.response.headers.add_header("Set-Cookie", 
				"username={0}; Path=/".format(make_secure_val(user_username)))
			self.redirect("/welcome")

class LoginHandler(Handler):
	def get(self):
		self.render("login.html")

	def post(self):
		username = self.request.get('username')
		password = self.request.get('password')

		if valid_login(username, password):
			self.response.headers.add_header("Set-Cookie", 
				"username={0}; Path=/".format(make_secure_val(username)))
			self.redirect("/welcome")
		else:
			self.render("login.html", login_error = "Invalid login")

class LogoutHandler(Handler):
	def get(self):
		self.response.headers.add_header("Set-Cookie", "username=; Path=/")
		self.redirect("/signup")

class WelcomeHandler(Handler):
	def get(self):
		username = check_secure_val(self.request.cookies.get('username'))
		if username:
			self.render("welcome.html", username = username)
		else:
			self.redirect("/signup")

class UserListHandler(Handler):
	def get(self):
		# TODO: Make only the admin able to view this page
		reg_users = db.GqlQuery('select * from Users')
		self.render('user_list.html', reg_users = reg_users)

app = webapp2.WSGIApplication([('/', MainPage), 
								('/signup', SignupHandler), 
								('/welcome', WelcomeHandler), 
								('/reg_users', UserListHandler), 
								('/login', LoginHandler), 
								('/logout', LogoutHandler), 
								], debug=True)
