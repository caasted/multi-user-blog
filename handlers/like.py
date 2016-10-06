import time
from google.appengine.ext import db
from models import *

class LikeHandler():
	def process_like_button(self, blog, username):
		blog_entry = posts.Posts.get_by_id(long(blog), parent=None)
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
				new_like = likes.Likes(post_id=long(blog), username=username)
				new_like.put()
				return ""
			else:
				return "You have already unliked this post (or didn't like it before)"
		elif blog_entry.author != username and already_liked:
			if self.request.get("unlike"):
				new_likes = blog_entry.likes - 1
				blog_entry.likes = new_likes
				blog_entry.put()
				query = "select * from Likes where post_id = :blog and username = :username"
				remove_like = db.GqlQuery(query, blog=long(blog), username=username)
				db.delete(remove_like)
				return ""
			else:
				return "You have already liked this post"
		else:
			return "You can't like/unlike on your own posts"
