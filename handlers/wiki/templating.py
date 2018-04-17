#templating.py
import jinja2
import os
import logging

# template_dir = os.path.normpath(os.path.join(os.getcwd(), r'templates/wiki'))
template_dir = os.path.abspath('templates/wiki')
# logging.info(alternative)

jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir), 
                                trim_blocks=True, autoescape=True)
                                
def render_str(template,**params):
    t = jinja_env.get_template(template)    
    return t.render(params)  
