#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import config

DEBUG = config.debug


blog = 'handlers.blog.blog.%s'
wiki = 'handlers.wiki.wiki.%s'

WIKIRE = r'(/(?:[a-zA-Z0-9_\-]+/?)*)'

app = webapp2.WSGIApplication([

    ('/', 'handlers.mainhandler.MainHandler'),
    ('/asciichan/?','handlers.asciichan.ASCII'),
    ('/cookies/?', 'handlers.cookies.Cookies'),

    #Blog Handlers
    ('/blog/?','handlers.blog.blog.BlogHandler'),
    ('/blog/newpost/?','handlers.blog.blog.NewPost'),
    ('/blog/(\d+)/?','handlers.blog.blog.BlogHandler'),
    ('/blog/signup/?','handlers.blog.blog.SignUp'),
    ('/blog/login/?','handlers.blog.blog.Login'),
    ('/blog/logout/?', blog%'Logout'),
    ('/blog/?.json', blog%'JSON'),
    ('/blog/(\d+)/?.json', blog%'JSON'),
    ('/blog/flush/?', blog%'Flush'),
    ('/blog/setexisting/?',blog%'SetExistingCache'),

    # Handlers for the Wiki

    ('/wiki/login/?', wiki%'Login'),
    ('/wiki/logout/?',wiki%'Logout'),
    ('/wiki/signup/?', wiki%'SignUp'),
    ('/wiki/flush/?' , wiki%'Flush' ),
    ('/wiki', wiki%'Redirect'),
    ('/wiki/_edit', wiki%'Redirect'),
    ('/wiki/_history' , wiki%'Redirect'),
    ('/wiki/_edit' + WIKIRE, wiki%'Edit'),
    ('/wiki/_history' + WIKIRE, wiki%'History'),
    ('/wiki' + WIKIRE, wiki%'WikiPageHandler'),


    #Error Handler

    ('/.*', 'handlers.mainhandler.Error404')


    ], debug=DEBUG)
