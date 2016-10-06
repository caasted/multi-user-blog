import webapp2
from handlers import *

app = webapp2.WSGIApplication([('/', mainpage.MainPage), 
								('/signup', signup.SignupHandler), 
								('/welcome', welcome.WelcomeHandler), 
								('/reg_users', userlist.UserListHandler), 
								('/login', login.LoginHandler), 
								('/logout', logout.LogoutHandler), 
								('/edit_blog/([0-9]+)', editblog.EditBlogHandler), 
								('/edit_comment/([0-9]+)', editcomment.EditCommentHandler), 
								('/post/([0-9]+)', postpage.PostPageHandler), 
								], debug=True)
