#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Example using WrapBokeh

"""
from bokeh.layouts import row, layout, Spacer, widgetbox
from bokeh.models.widgets.buttons import Button
from bokeh.models.widgets import Div

from flask import redirect, abort, Blueprint
from flask import request
from flask import current_app as app

from pywrapbokeh import WrapBokeh
from dominate.tags import *
from dominate.util import raw

from ex2_config import *
PAGE_URL = URL_INDEX

ex2_index = Blueprint('ex2_index', __name__)
@ex2_index.route(PAGE_URL, methods=['GET', 'POST'])
def ex2__index():

    args, _redirect_page_metrics = w.process_req(request)
    if not args: return _redirect_page_metrics
    app.logger.info("{} : args {}".format(PAGE_URL, args))

    if args.get("b_login", False): return redirect(URL_LOGIN)

    # Create a dominate document, see https://github.com/Knio/dominate
    # this line should go after any "return redirect" statements
    w.dominate_document()
    url_page_css(w.dom_doc, PAGE_URL)

    doc_layout = layout(sizing_mode='scale_width')

    doc_layout.children.append(Div(text="""<h1>pywrapBokeh</h1>"""))

    w.add_css("b_login", {'button': {'background-color': '#98FB98', 'min-width': '50px'}})
    left_margin = int(int(args.get("windowWidth", 800)) * 0.1)
    doc_layout.children.append(row([Spacer(width=left_margin), w.get("b_login")]))
    return w.render(doc_layout)


w = WrapBokeh(PAGE_URL, app.logger)
w.add("b_login", Button(label="LOGIN", width=50, css_classes=['b_submit']))
w.init()

