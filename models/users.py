from google.appengine.ext import db

class Users(db.Model):
	username = db.StringProperty(required = True)
	password = db.TextProperty(required = True)
	email = db.StringProperty()
	registered = db.DateTimeProperty(auto_now_add = True)

