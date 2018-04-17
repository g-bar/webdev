#wiki.py
import webapp2
import os
import templating
from handlers import auth
from handlers.utils.secure_pass import *
from handlers.utils.verify import *
from entities import User, WikiPage
import hashlib
import time
from google.appengine.api import memcache
from google.appengine.ext import db
import logging

from main import DEBUG

class WikiSite(auth.Auth):

    def write(self, *args,**kwargs):
        self.response.write(*args,**kwargs)

    def render(self,template=None,**params):
        template = template or type(self)._template
        if 'pagetitle' not in params:
            params['pagetitle'] = "Wiki"
        template_str = templating.render_str(template, **params)
        self.write(template_str)

class SignUp(WikiSite):
    _template = 'signup.html'

    def get(self):
        referer = self.get_referer()
        self.render(pagetitle='SignUp', referer = referer)


    def get_referer(self):
        referer = self.request.get('referer') or self.request.referer
        if referer and (referer.endswith('/login/') or referer.endswith('/login')):
            referer = None
        return referer or '/wiki/'

    def post(self):
        user,password,verify,email = [self.request.get(input)
                                     for input in
                                     ('username','password','verify','email')]

        referer = str(self.request.get('referer'))

        avail = User.avail_user(user)
        vuser = verify_user(user) and avail
        vpass = verify_pass(password)
        vverify = password == verify
        vemail = verify_email(email) if email else True

        if all([vuser,vpass,vverify,vemail]):
            User.store_user(user,password,email)
            self.set_user_cookie(user)
            self.redirect(referer )



        else:
            kwargs = {'username': user,
                      'email': email,
                      'nameerr': '' if vuser else ('Username not available'
                                        if not avail else 'Invalid username'),
                      'passerr': ('' if vpass else 'Invalid password') if vverify else '',
                      'verifyerr': '' if vverify else "Passwords don't match",
                      'emailerr': '' if vemail else 'Invalid email'}

            self.render(referer = referer, **kwargs)


class Login(WikiSite):
    _template = 'login.html'

    def get(self):

        referer = self.request.get('referer') or self.request.referer or '/wiki/'

        if self.logged_user :

            self.redirect(referer)
        else:
            self.render(pagetitle='Login', username='',loginerr='',
                        referer = referer)

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        referer = str(self.request.get('referer')) or '/wiki/'

        user = User.query_user(username)
        if user and verify_hash(password,user.password):
            self.set_user_cookie(username)
            self.redirect(referer)
        else:
            self.render(pagetitle = 'Login',
                        loginerr='Invalid Login',
                        username=username,
                        referer=referer)

class Logout(WikiSite):

    def get(self):
        self.delete_user_cookie()
        redirect_to = str(self.request.get('goto')) or self.request.referer or '/wiki/'
        self.redirect(redirect_to)


class WikiPageHandler(WikiSite):

    def get(self, url):

        self.set_attributes(url)

        if self.wikipage:
            self.render('permalink.html', wikipage=self.version or self.wikipage,
                                          time = self.queried,
                                          user=self.logged_user,
                                          url = url.strip('/'),
                                          )
        else:
            self.redirect('/wiki/_edit' + url)

    def set_attributes(self,url):

        self.urlhash = self.hashurl(url.strip('/'))
        version = self.request.get('v')
        q = "WikiPage.all().filter('hash = ', self.urlhash).order('-created')"

        if not version:
            self.version = None

        elif not version.isdigit():
            self.redirect(self.request.path, abort = True)

        else:
            q_v = eval(q).filter("version = ", int(version))
            self.version = q_v.get()
            if not self.version:
                self.redirect(self.request.path, abort = True)

        self.wikipage = eval(q).get() or ''
        self.queried = None


    @staticmethod
    def hashurl(url):
        return hashlib.md5(url).hexdigest()

    def get_page(self,urlhash):
        return memcache.get(urlhash) or self.set_page_cache(urlhash)

    def set_page_cache(self,urlhash):
        wikipage = WikiPage.query_by("hash",urlhash,limit=1)
        if wikipage:
            return wikipage[0].tocache(urlhash)



class Edit(WikiPageHandler):

    def get(self,url):
        if self.logged_user:
            self.set_attributes(url)
            # logging.info(self.version.key().id() == self.version.key().id())
            content = self.wikipage and (self.version.content if self.version
                                          else self.wikipage.content)

            self.render('edit.html', content= content,
                                    user=self.logged_user,
                                    goto=url
                        )

        else:
            self.redirect('/wiki/login/?referer=%s'%self.request.url)

    def post(self, url):
        self.set_attributes(url)
        content = self.request.get('content')

        if not content:
            self.render('edit.html', error = "Content cannot be empty")
        else:
            if self.wikipage:
                version = self.wikipage.version + 1
                page = self.version or self.wikipage
                overrite = self.version and self.version.page_id != self.wikipage.page_id

                if page.content != content or overrite:
                    newversion = WikiPage(content=content,
                                          hash=self.urlhash,
                                          version = version,
                                          )
                    newversion.put()

            else:
                newpage = WikiPage(content=content,hash = self.urlhash,version=1)
                newpage.put()
                # newpage.put_and_cache()

            self.redirect('/wiki%s' %url)


class History(WikiPageHandler):
    def get(self, url):
        if self.logged_user:
            self.set_attributes(url)
            pages = WikiPage.query_by("hash", self.urlhash)
            if not pages:
                self.redirect('/wiki/_edit' + url)

            self.render('history.html',
                        pages=pages,
                        user=self.logged_user,
                        url=url.strip('/'),
                        goto=url)

        else:
            self.redirect('/wiki/login/?referer=%s' % self.request.url)


class Flush(WikiSite):
    def get(self):
        memcache.flush_all()
        self.redirect('/wiki/')

class Redirect(WikiSite):
    def get(self):
        self.redirect(self.request.path + '/?' + self.request.query_string)