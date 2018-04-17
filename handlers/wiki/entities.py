#wiki entities

"""Implements the Datastore kinds for the wiki site. The User kind is the same
for both the Wiki and the Blog and thus it merely exports it as is.
The WikiPage is a new kind that inherits from Post and implements the 
render_str method so that it uses the wiki's templating environment, otherwise it
has the same properties and is identical to a blog Post"""

from handlers.entities import User
from google.appengine.ext import db
from google.appengine.api import memcache
import templating
import logging
import time

class WikiPage(db.Model):
    """
    A Datastore kind for Wiki articles, differs from Post only in the render_str
    method which it changes to use the wiki templateing environment"""
    hash = db.StringProperty(required=True)
    content=db.TextProperty(required=True)
    created=db.DateTimeProperty(auto_now_add=True)
    last_modified=db.DateTimeProperty(auto_now=True)    
    version = db.IntegerProperty()
    
    
    @classmethod        
    def query_by(cls, property, value, criteria="=", limit=None):
        logging.info('DB query')
        query_op = "%s %s "%(property,criteria)
        query = cls.all().filter(query_op, value).order('-created')
        
        if not limit:
            return list(query)
        
        return query.fetch(limit=limit)
    
    @property
    def page_id(self):
        return self.key().id()        
    
    def put_and_cache(self, memcachekey=None, withtime=True):
        logging.info('DB write')
        self.put()       
        self.tocache(memcachekey,withtime)        
        
    def tocache(self,memcachekey=None, withtime=True):
        memcachekey = memcachekey or '_wiki' + self.hash
        value = (self,time.time()) if withtime else self
        res = memcache.set(memcachekey,value)
        logging.info(res)
        return value
        
       
