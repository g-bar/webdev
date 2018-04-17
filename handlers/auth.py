#Authentication System
import webapp2
from utils.secure_pass import *
from utils.verify import *
from datetime import datetime,timedelta

class Auth(webapp2.RequestHandler):
    def set_user_cookie(self,username,expires=30):            
        user = make_sec_cookie(username)
        self.response.set_cookie('user',user,expires=datetime.today() + timedelta(expires),
                                   httponly=True)        
                
    def delete_user_cookie(self):
        self.response.delete_cookie('user')                
        
       
    def initialize(self,*args,**kargs):
        webapp2.RequestHandler.initialize(self,*args,**kargs)
        cookie = self.request.cookies.get('user','')
        self.logged_user = verify_user_cookie(cookie)
        
