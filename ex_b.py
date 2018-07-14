#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Example using WrapBokeh

"""
from flask import Blueprint, request, redirect
from flask import current_app as app
from bokeh.layouts import column, row, layout, Spacer, widgetbox
from pywrapbokeh import WrapBokeh
from bokeh.models.widgets import Paragraph, Div
from bokeh.models.widgets.buttons import Button
from bokeh.models.widgets.inputs import Select, TextInput

from ex_utils import redirect_lookup_table

from dominate.tags import *
from dominate.util import raw

import logging
logger = logging.getLogger()

PAGE_URL = '/b/'

ex_b = Blueprint('ex_b', __name__)
@ex_b.route(PAGE_URL, methods=['GET', 'POST'])
def page_b():
    """
    Shows example of doing form input, with drop downs that dynamically
    change content.
    """

    args = widgets.process_req(request)

    # redirect to another page based on widget data...
    _redirect = redirect_lookup_table(args.get("sel_nexturl", None))
    if _redirect: return redirect(_redirect)

    # this line should go after any "return redirect" statements
    d = widgets.dominate_document()

    # update state of state pulldown based on country
    if args.get("sel_country", False) and args["sel_country"] in geo_info.keys():
        widgets.get("sel_state").options = [('', 'Select State')] + [(x, x) for x in geo_info[args["sel_country"]]]

    # on submit, validate form contents
    if args.get("b_submit", False):
        validated = True
        if args.get("tin_fname", False):
            if args["tin_fname"] in ["", "first name"]:
                validate = False
                with d.body:
                    style(raw(""".b_submit button { background-color: #DC143C !important;}"""))

        if validate:
            logger.info("validated")
            return redirect("/")

    doc_layout = layout(sizing_mode='scale_width')
    doc_layout.children.append(row(Div(text="""<h1>pywrapBokeh</h1><h2>Page B</h2>"""),
                                   Paragraph(text="""Play with all these widgets.""")))

    doc_layout.children.append(column(widgets.get("tin_fname"),
                                      widgets.get("tin_lname"),
                                      widgets.get("sel_country"),
                                      widgets.get("sel_state"),
                                      widgets.get("b_submit")))

    doc_layout.children.append(row(widgets.get("sel_nexturl")))

    d = widgets.render(d, doc_layout)
    return "{}".format(d)


widgets = WrapBokeh(PAGE_URL, app.logger)

widgets.add("tin_fname", TextInput(title="First Name:", placeholder="first name", css_classes=['tin_fname']))
widgets.add("tin_lname", TextInput(title="Last Name:", placeholder="last name", css_classes=['tin_lname']))
widgets.add("b_submit", Button(label="Submit", css_classes=['b_submit']))

widgets.add("sel_nexturl", Select(options=[('99', 'Select Next Page'),
                                           ('0', 'Home'),
                                           ('1', 'Page A'),
                                           ('3', 'Page C'),
                                           ('4', 'Page D')],
                                  value=None,
                                  title="Select URL",
                                  css_classes=['sel_nexturl']))

geo_info = {
    "United States": ["Washington", "New York", "Texas", "California", "Montanna", "Michigan", "New Mexico"],
    "Canada": ["Ontario", "Saskatchewan", "Manitoba", "Alberta", "Quebec", "Britsh Columbia"]
}
countries = [('', 'Select Country')] + [(x, x) for x in geo_info.keys()]
states = [('', 'Select State')] + [(x, x) for x in geo_info["United States"]]

widgets.add("sel_country", Select(options=countries, value=None, title="Select Country", css_classes=['sel_country']))
widgets.add("sel_state",   Select(options=states,    value=None, title="Select State",   css_classes=['sel_state']))

# Next
# !! https://stackoverflow.com/questions/40981485/is-there-a-way-to-format-the-widgets-contents

widgets.init()

