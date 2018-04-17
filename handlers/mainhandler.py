#main_handler.py
import webapp2
from os.path import dirname,join
import jinja2
import time


template_dir = join(dirname(dirname(__file__)), 'templates')
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), 
                                trim_blocks=True, autoescape=True)
                                
def render_str(template,**params):
    t = jinja_env.get_template(template)
    return t.render(params)

class Handler(webapp2.RequestHandler):
    def write(self,*args,**kargs):
        self.response.write(*args,**kargs)       
    
    def render(self,template=None,**params):
        template = template or type(self)._template
        self.write(render_str(template,**params))         
    
class MainHandler(Handler):
    def get(self):
        self.write('Hello')

class Error404(Handler):
    def get(self):
        self.error(404)
        self.render('404.html')               
