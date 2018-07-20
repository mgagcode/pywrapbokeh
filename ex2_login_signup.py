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
PAGE_URL = URL_LOGIN_SIGNUP

ex2_login_signup = Blueprint('ex2_login_signup', __name__)
@ex2_login_signup.route(PAGE_URL, methods=['GET', 'POST'])
def ex2__login_signup():

    args, _redirect_page_metrics = w.process_req(request)
    if not args: return _redirect_page_metrics
    app.logger.info("{} : args {}".format(PAGE_URL, args))

    # Check login name and password... redirect if valid
    # here

    submitted = args.get("b_submit", False)

    # on submit, validate form contents
    validated = True
    if submitted:
        if args.get("tin_fname", False):
            if args["tin_fname"] in ["", "first name"]:
                validated = False
                w.add_css("tin_fname", {'input' :{'background-color': '#F08080'}})

        if args.get("tin_lname", False):
            if args["tin_lname"] in ["", "last name"]:
                validated = False
                w.add_css("tin_lname", {'input' :{'background-color': '#F08080'}})

        if validated:
            app.logger.info("validated: {}".format(args))
            # TODO: send form data somewhere as a JSON object
            return redirect("/b/")

    # Create a dominate document, see https://github.com/Knio/dominate
    # this line should go after any "return redirect" statements
    w.dominate_document()
    url_page_css(w.dom_doc, PAGE_URL)

    doc_layout = layout(sizing_mode='scale_width')

    doc_layout.children.append(Div(text="""<h1>pywrapBokeh</h1>"""))

    w.add_css("tin_fname", {'input': {'width': '90%'}})
    w.add_css("tin_lname", {'input': {'width': '90%'}})
    w.add_css("tin_lpw", {'input': {'width': '90%'}})
    w.add_css("tin_lpw_confirm", {'input': {'width': '90%'}})
    w.add_css("tin_email", {'input': {'width': '90%'}})
    wbox = widgetbox(w.get("tin_fname"),
                     w.get("tin_lname"),
                     w.get("tin_lpw"),
                     w.get("tin_lpw_confirm"),
                     w.get("tin_email"),
                     w.get("b_submit"))
    left_margin = int(int(args.get("windowWidth", 800)) * 0.2)
    doc_layout.children.append(row([Spacer(width=left_margin), wbox]))

    return w.render(doc_layout)


w = WrapBokeh(PAGE_URL, app.logger)

w.add("tin_fname", TextInput(title="First Name:", placeholder="", css_classes=['tin_fname']))
w.add("tin_lname", TextInput(title="Last Name:", placeholder="", css_classes=['tin_lname']))
w.add("tin_lpw", PasswordInput(title="Password:", placeholder="", css_classes=['tin_lpw']))
w.add("tin_lpw_confirm", PasswordInput(title="Confirm Password:", placeholder="", css_classes=['tin_lpw_confirm']))
w.add("tin_email", TextInput(title="Email:", placeholder="", css_classes=['tin_email']))
w.add("b_submit", Button(label="Submit", css_classes=['b_submit']))

w.init()

