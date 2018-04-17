from mainhandler import Handler, render_str
from google.appengine.ext import db
from google.appengine.api import memcache
import urllib2
import json
import time
import random
import logging




#Stored old error logs, replaced with logging.exceptions    
# class ErrLog(db.Model):
    # date=db.DateTimeProperty(auto_now_add=True)
    # error=db.TextProperty()
    
    
class ASCII(Handler):    
    _template ='front.html'
    
    def get(self):            
        vals = memcache.get('top') or self.set_cache()
        if len(vals)==3:            
            arts, imgsrc, queried = vals
            queried = "%d"%(time.time() - queried)
        else:
            arts,imgsrc = vals
            queried = None
        
        self.render(arts=arts,imgsrc=imgsrc, time=queried)
        
    def post(self):
        title = self.request.get('title')
        art = self.request.get('art')
        coordinates = self.get_coordinates(self.request.remote_addr)        
        
        if title and art:
            a = Art(title=title, art=art)
            if coordinates:
                a.coordinates = coordinates
            a.put()            
            self.set_cache()
            self.redirect('/asciichan')
            
        else:
            error = "We need a title and some artwork"
            self.render(error=error, title=title, art=art)
    
    def set_cache(self):
        logging.info('Database query')
        arts = list(Art.all().order('-created')[:10])
        imgsrc = self.goog_map_img(arts)            
        qtime = time.time()
        memcache.set('top',(arts,imgsrc,qtime))                               
        return arts, imgsrc, qtime
        
    @staticmethod
    def goog_map_img(arts):    
        
        GOOGMAPSURL =  ("https://maps.googleapis.com/maps/api/staticmap"
               "?size=900x400"               
               "&maptype=roadmap"
               "&{markers}"
               "&key=AIzaSyD_D6bl7k0Os4tthZdAtmsdswbKyEHFC_g")
               
        markers='&'.join("markers=%s"%art.coordinates for art in arts)        
        
        return GOOGMAPSURL.format(markers=markers)                                   
            
    @staticmethod
    def get_coordinates(ip):    
        try:        
            geodata=json.load(urllib2.urlopen('http://ip-api.com/json/%s'%ip))
            coordinates = ','.join(map(str,[geodata['lat'],geodata['lon']]))
        except (urllib2.URLError, KeyError) as err:
            error = "%s: %s"%(err.__class__.__name__, err)
            logging.exception(error)        
            return
        return coordinates    
    
        
class Art(db.Model):
    title = db.StringProperty(required=True)
    art = db.TextProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    coordinates = db.StringProperty(required=False)  
