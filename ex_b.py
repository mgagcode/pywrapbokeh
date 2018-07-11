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

PAGE_URL = '/b/'

ex_b = Blueprint('ex_b', __name__)
@ex_b.route(PAGE_URL, methods=['GET', 'POST'])
def page_b():

    args = widgets.process_req(request)

    # redirect to another page based on widget data...
    _redirect = redirect_lookup_table(args.get("sel_nexturl", None))
    if _redirect: return redirect(_redirect)

    doc_layout = layout(sizing_mode='scale_width')
    doc_layout.children.append(row(Div(text="""<h1>pywrapBokeh</h1><h2>Page B</h2>"""),
                                   Paragraph(text="""Play with all these widgets.""")))

    doc_layout.children.append(column(widgets.get("tin_fname"),
                                      widgets.get("tin_lname"),
                                      widgets.get("b_submit")))

    doc_layout.children.append(row(widgets.get("sel_nexturl")))

    d = widgets.dominate_document()
    d = widgets.render(d, doc_layout)
    return "{}".format(d)


widgets = WrapBokeh(PAGE_URL, app.logger)

widgets.add("tin_fname", TextInput(title="First Name:", placeholder="first name"))
widgets.add("tin_lname", TextInput(title="Last Name:", placeholder="last name"))
widgets.add("b_submit", Button(label="Submit"))

widgets.add("sel_nexturl", Select(options=[('99', 'Select Next Page'),
                                           ('0', 'Home'),
                                           ('1', 'Page A'),
                                           ('3', 'Page C'),
                                           ('4', 'Page D')],
                                    value=None,
                                    title="Select URL"))

# Next


widgets.init()

