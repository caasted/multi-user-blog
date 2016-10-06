import webapp2
from handlers import *

app = webapp2.WSGIApplication([('/', mainpage.MainPage), 
								('/signup', signup.SignupHandler), 
								('/welcome', welcome.WelcomeHandler), 
								('/reg_users', userlist.UserListHandler), 
								('/login', login.LoginHandler), 
								('/logout', logout.LogoutHandler), 
								('/edit_blog', editblog.EditBlogHandler), 
								('/edit_comment', editcomment.EditCommentHandler), 
								('/.*', postpage.PostPageHandler), 
								], debug=True)
