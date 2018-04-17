#entities
from google.appengine.ext import db
from google.appengine.api import memcache
import handlers.mainhandler
from utils.secure_pass import make_hash
import json
from datetime import datetime
import time
import logging


class User(db.Model):
    username = db.StringProperty(required=True)
    password = db.StringProperty(required = True)
    email = db.EmailProperty()
    
    @classmethod
    def query_user(cls,user):
        return cls.all().filter('username = ', user).get()
    @classmethod
    def avail_user(cls,user):
        return not cls.query_user(user) 
    
    @classmethod
    def store_user(cls,username,password,email=None):
        password = make_hash(password)           
        properties = dict(username=username,password=password)
        if email: 
            properties['email'] = email
        cls(**properties).put()
    

class Post(db.Model):
    subject=db.StringProperty(required=True)
    content=db.TextProperty(required=True)
    created=db.DateTimeProperty(auto_now_add=True)
    last_modified=db.DateTimeProperty(auto_now=True)         
    
    
    def render(self):
        raise NotImplementedError
        
    def as_dict(self):
        post_dict = {}
        for property in self.properties():
            val = getattr(self,property)
            if isinstance(val,datetime):
                val=val.strftime('%c')
            post_dict[property] = val
            
        return post_dict        
        
    