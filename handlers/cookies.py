from mainhandler import Handler
import hmac
import hashlib

def hash_str(s):
    return hmac.new('thisissecret',s,hashlib.sha256).hexdigest()

def make_secure_val(s):
    return "%s,%s" % (s, hash_str('udacity'+s))

def check_secure_val(h):    
    val = h.split(',')[0]
    if hmac.compare_digest(h,make_secure_val(val)):
        return val

class Cookies(Handler):
    def get(self):                   
        val = check_secure_val(self.request.cookies.get('visits',''))        
        visits = 1           
        if val:
            visits = int(val)+1
            
        value = make_secure_val(str(visits))                          
                                  
        self.response.set_cookie('visits',value=value)        
        self.render('cookies.html', visits= visits  )   
        
        
            
        
        