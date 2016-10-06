from google.appengine.ext import db

class Posts(db.Model):
	subject = db.StringProperty(required = True)
	content = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	author = db.StringProperty(required = True)
	likes = db.IntegerProperty(required = True)
	comments = db.IntegerProperty(required = True)

