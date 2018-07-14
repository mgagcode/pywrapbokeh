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
from bokeh.models.widgets.inputs import Select

from ex_utils import redirect_lookup_table

PAGE_URL = '/a/'

ex_a = Blueprint('ex_a', __name__)
@ex_a.route(PAGE_URL, methods=['GET', 'POST'])
def page_a():

    args = widgets.process_req(request)

    # redirect to another page based on widget data...
    _redirect = redirect_lookup_table(args.get("sel_nexturl", None))
    if _redirect: return redirect(_redirect)

    # this line should go after any "return redirect" statements
    widgets.dominate_document()  # create dominate document

    # if the clear buttons button is slected, clear the group buttons
    if args.get("but_clear_groups", False):
        widgets.set_value("cbbg_family", None)
        widgets.set_value("rbg_names", None)

    doc_layout = layout(sizing_mode='scale_width')
    doc_layout.children.append(row(Div(text="""<h1>pywrapBokeh</h1><h2>Page A</h2>"""),
                                   Paragraph(text="""Play with all these widgets.""")))

    doc_layout.children.append(row(widgets.get("sel_nexturl")))

    return widgets.render(doc_layout)


widgets = WrapBokeh(PAGE_URL, app.logger)

widgets.add("sel_nexturl", Select(options=[('99', 'Select Next Page'),
                                           ('0', 'Home'),
                                           ('2', 'Page B'),
                                           ('3', 'Page C'),
                                           ('4', 'Page D')],
                                    value=None,
                                    title="Select URL"))

# Next
# https://bokeh.pydata.org/en/latest/docs/user_guide/examples/interaction_data_table.html

widgets.init()

