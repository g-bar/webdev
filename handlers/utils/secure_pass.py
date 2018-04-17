#secure_pass.py
import os
import hashlib
import binascii
import hmac
        

def make_hash(value, salt=None):
    salt = salt or os.urandom(64)
    return hmac.new(salt,value,hashlib.sha512).hexdigest() + binascii.hexlify(salt)

def verify_hash(value,hashed):
    try:
        salt = binascii.unhexlify(hashed[-128:])
    except TypeError:
        return
    return make_hash(value,salt) == hashed

def make_sec_cookie(value,salt=None):
    salt = salt and binascii.unhexlify(salt)
    return value + make_hash(value,salt)

def verify_user_cookie(cookie):
    value , salt = cookie[:-256], cookie[-128:]
    if make_sec_cookie(value,salt) == cookie:
        return value
    
        
        
        
###Functions from Intro to Web Development        

# secret = '13sm8nwe' 
# def make_secure_val(val):
    # return '%s|%s' % (val, hmac.new(secret, val, hashlib.sha512).hexdigest())

# def check_secure_val(secure_val):
    # try:
        # val = secure_val.split('|')[0]
    # except IndeError:
        # return
    # if secure_val == make_secure_val(val):
        # return val
    
if __name__ == "__main__":
   h = make_hash(u'dog')
   verify_hash(u'dog',h)
   
   