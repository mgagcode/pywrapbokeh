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
from dominate.tags import *
from dominate.util import raw

from ex_utils import redirect_lookup_table

PAGE_URL = '/'

ex2_index = Blueprint('ex2_index', __name__)
@ex2_index.route(PAGE_URL, methods=['GET', 'POST'])
def test_main():

    args, _redirect_page_metrics = w.process_req(request)
    if not args: return _redirect_page_metrics
    app.logger.info("{} : args {}".format(PAGE_URL, args))

    # Check login name and password... redirect if valid
    # here

    # Create a dominate document, see https://github.com/Knio/dominate
    # this line should go after any "return redirect" statements
    w.dominate_document()

    with w.dom_doc.body:
        style(raw("""body {background: #ffffff url("media/sharon-mccutcheon-576867-unsplash.jpg") no-repeat left top;)}"""))
        style(raw("""body {background-size: cover;)}"""))

    doc_layout = layout(sizing_mode='scale_width')

    doc_layout.children.append(Div(text="""<h1>pywrapBokeh</h1>"""))

    w.add_css("b_submit", {'button': {'background-color': '#98FB98', 'min-width': '50px'}})
    w.add_css("tin_lname", {'input': {'width': '90%'}})
    w.add_css("tin_lpw", {'input': {'width': '90%'}})
    wbox = widgetbox(w.get("tin_lname"), w.get("tin_lpw"), w.get("b_submit"))
    left_margin = int(int(args.get("windowWidth", 800)) * 0.1)
    doc_layout.children.append(row([Spacer(width=left_margin), wbox]))

    return w.render(doc_layout)


w = WrapBokeh(PAGE_URL, app.logger)

w.add("tin_lname", TextInput(title="Login Name:", placeholder="", css_classes=['tin_lname']))
w.add("tin_lpw", PasswordInput(title="Password:", placeholder="", css_classes=['tin_lpw']))
w.add("b_submit", Button(label="Submit", css_classes=['b_submit']))

w.init()

