#blog.py

from handlers.mainhandler import Handler, render_str
from google.appengine.api import memcache
from verify import *
from secure_pass import *
from handlers.blog.blogdata import Post, User
import json
import os
import logging
import time
from datetime import datetime, timedelta
import random
from main import DEBUG



class SiteHandler(Handler):

    def render(self,template=None,**params):
        defparams = dict(pagetitle='My Blog',time=None, user=self.logged_user)
        defparams.update(params)
        Handler.render(self,template,**defparams)

    def set_user_cookie(self,username,expires=30):
        user = make_sec_cookie(username)
        self.response.set_cookie('user',user,expires=datetime.today() + timedelta(expires),
                                   httponly=True)

    def delete_user_cookie(self):
        self.response.delete_cookie('user')


    def initialize(self,*args,**kargs):
        Handler.initialize(self,*args,**kargs)
        cookie = self.request.cookies.get('user','')
        self.logged_user = verify_user_cookie(cookie)

    def get_post(self,id):
        return int(id)<2**63 and memcache.get(id) or self.set_post_cache(id)

    def set_post_cache(self,id):
        # existing = memcache.get('existing')
        # if not existing:
            # logging.error('Existing post cache not found')
            # return
        # if int(id) in existing:
            # logging.info('DB read')
            # post = Post.get_by_id(int(id))
        # else:
            # post = None
        post = Post.get_by_id(int(id))
        if post:
            value = post, time.time()
            memcache.set(id,value)
            return value

    def get_posts(self, number=10):
        return memcache.get('posts') or self.set_front_cache(number)


    def set_front_cache(self,number=10):
        logging.info('DB read')
        posts = Post.all().order('-created').fetch(limit=number)
        value = posts, time.time()
        memcache.set('posts',value)
        return value

    def update_front_cache(self,newpost,number=10):
        client = memcache.Client()

        while True:
            posts, queried= client.gets('posts')
            posts.insert(0,newpost)
            posts = posts[:number]
            value = posts, queried


            if client.cas('posts',value):
                break

            logging.info('cas failed')


class JSON(SiteHandler):
    def get(self, id = None):
        self.response.headers['Content-Type'] = "application/json; charset=utf-8"

        if id:
            post = self.get_post(id)
            jsonobj = json.dumps(post[0].as_dict() if post else {})
            self.write(jsonobj)

        else:
            posts = self.get_posts()[0]
            jsonobj = json.dumps([post.as_dict() for post in posts] if posts else [])
            self.write(jsonobj)


class BlogHandler(SiteHandler):
    def get(self, id=None):

        if id:
            post = self.get_post(id)
            if post:
                queried, post = '%d' % (time.time() - post[1]), post[0]
                logging.info(post)

                subject = post.subject
                post = render_str('/blog/post.html', post=post)

                self.render(r'/blog/permalink.html', post=post,
                            posttitle=subject, time=queried)
            else:
                self.redirect('/blog')
        else:
            posts, queried= self.get_posts()
            queried = '%d'%(time.time() - queried)
            posts = [render_str('/blog/post.html',post = post) for post in posts]

            self.render(r'blog/home.html',posts=posts, time = queried)

class NewPost(SiteHandler):
    _template = 'blog/newpost.html'
    def get(self):
        if self.logged_user or DEBUG:
            self.render()
        else:
            self.redirect(r'/blog/login')
    def post(self):
        subject=self.request.get('subject')
        content = self.request.get('content')
        if subject and content:
            post=Post(subject=subject,content=content)
            post.put()
            post_id = str(post.key().id())

            self.update_front_cache(post)
            self.redirect(r'/blog/%s'%post_id)
        else:
            error = 'Title and content are required'
            self.render(error=error, subject=subject, content=content)


class SignUp(SiteHandler):
    _template = '/blog/signup.html'
    def get(self):
        self.render(pagetitle='SignUp')
    def post(self):
        user,password,verify,email = [self.request.get(input)
                                     for input in
                                     ('username','password','verify','email')]

        avail = User.avail_user(user)
        vuser = verify_user(user) and avail
        vpass = verify_pass(password)
        vverify = password == verify
        vemail = verify_email(email) if email else True

        if all([vuser,vpass,vverify,vemail]):
            User.store_user(user,password,email)
            self.set_user_cookie(user)
            self.redirect('/blog')

        else:
            kwargs = {'username': user,
                      'email': email,
                      'nameerr': '' if vuser else ('Username not available'
                                        if not avail else 'Invalid username'),
                      'passerr': ('' if vpass else 'Invalid password') if vverify else '',
                      'verifyerr': '' if vverify else "Passwords don't match",
                      'emailerr': '' if vemail else 'Invalid email'}

            self.render(pagetitle='SignUp', **kwargs)


class Login(SiteHandler):
    _template = 'blog/login.html'
    def get(self):
        if self.logged_user:

            self.render('blog/already_loggedin.html',pagetitle="Hi %s"%self.logged_user,
                        logged_user=self.logged_user)
        else:
            self.render(pagetitle='Login', username='',loginerr='')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        user = User.query_user(username)
        if user and verify_hash(password,user.password):
            self.set_user_cookie(username)
            self.redirect('/blog')
        else:
            self.render(loginerr='Invalid Login',username=username)

class Logout(SiteHandler):
    def get(self):
        self.delete_user_cookie()
        self.redirect('/blog')

class Flush(SiteHandler):
    def get(self):
        if self.logged_user or DEBUG:
            memcache.flush_all()
        self.redirect('/blog/')


class SetExistingCache(SiteHandler):
    def get(self):
        # if self.logged_user:
            # allposts = list(Post.all())
            # existing = [post.key().id() for post in allposts]
            # memcache.set('existing',existing)

        self.redirect('/blog')

class Test(SiteHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        if self.logged_user or DEBUG:
            posts = list(Post.all())
            out = '\n'.join(str(type(post)) for post in posts)
            self.write(out)
