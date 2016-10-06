from google.appengine.ext import db

class Likes(db.Model):
	post_id = db.IntegerProperty(required = True)
	username = db.StringProperty(required = True)

