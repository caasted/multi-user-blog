import webapp2
import os
import jinja2
import hmac
import hashlib
import random
import string

class Handler(webapp2.RequestHandler):
	template_dir = os.path.join(os.path.dirname(__file__), '../templates')
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

	def check_cookie(self):
		cookie_data = self.request.cookies.get('username')
		if cookie_data:
			return self.check_secure_val(cookie_data)
