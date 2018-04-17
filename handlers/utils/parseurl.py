#parseurl
import hashlib
def hashurl(url):
    return hashlib.md5(url).hexdigest()
    
