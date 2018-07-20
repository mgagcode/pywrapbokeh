#!/usr/bin/python
# -*- coding: utf-8 -*-
from flask import current_app as app
from dominate.tags import *
from dominate.util import raw

# pages
URL_INDEX = '/'
URL_LOGIN = '/login'
URL_LOGIN_SIGNUP = '/login/signup'


def url_page_css(dom_doc, url):
    with dom_doc.body:

        if url in [URL_INDEX, URL_LOGIN, URL_LOGIN_SIGNUP]:
            style(raw("""body {background: #ffffff url("/media/sharon-mccutcheon-576867-unsplash.jpg") no-repeat left top;)}"""))
            style(raw("""body {background-size: cover;)}"""))
        else:
            app.logger.error("Unknown URL: {}".format(url))