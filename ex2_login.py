#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Example using WrapBokeh

"""
from bokeh.layouts import row, layout, Spacer, widgetbox
from bokeh.models.widgets.inputs import TextInput, PasswordInput
from bokeh.models.widgets.buttons import Button
from bokeh.models.widgets import Div

from flask import redirect, abort, Blueprint
from flask import request
from flask import current_app as app

from pywrapbokeh import WrapBokeh

from ex2_config import *
PAGE_URL = URL_LOGIN

ex2_login = Blueprint('ex2_login', __name__)
@ex2_login.route(PAGE_URL, methods=['GET', 'POST'])
def ex2__login():

    args, _redirect_page_metrics = w.process_req(request)
    if not args: return _redirect_page_metrics
    app.logger.info("{} : args {}".format(PAGE_URL, args))

    if args.get("b_signup", False): return redirect(URL_LOGIN_SIGNUP)

    # Create a dominate document, see https://github.com/Knio/dominate
    # this line should go after any "return redirect" statements
    w.dominate_document()
    url_page_css(w.dom_doc, PAGE_URL)

    doc_layout = layout(sizing_mode='scale_width')

    doc_layout.children.append(Div(text="""<h1>pywrapBokeh</h1>"""))

    w.add_css("b_submit", {'button': {'background-color': '#98FB98', 'min-width': '60px'}})
    w.add_css("b_signup", {'button': {'background-color': '#98FB98', 'min-width': '60px'}})
    w.add_css("tin_lname", {'input': {'width': '90%'}})
    w.add_css("tin_lpw", {'input': {'width': '90%'}})
    wbox = widgetbox(w.get("tin_lname"), w.get("tin_lpw"), w.get("b_submit"), w.get("b_signup"))
    left_margin = int(int(args.get("windowWidth", 800)) * 0.1)
    doc_layout.children.append(row([Spacer(width=left_margin), wbox]))

    return w.render(doc_layout)


w = WrapBokeh(PAGE_URL, app.logger)

w.add("tin_lname", TextInput(title="Login Name:", placeholder="", css_classes=['tin_lname']))
w.add("tin_lpw", PasswordInput(title="Password:", placeholder="", css_classes=['tin_lpw']))
w.add("b_submit", Button(label="Submit", css_classes=['b_submit']))
w.add("b_signup", Button(label="Sign Up", css_classes=['b_signup']))

w.init()

