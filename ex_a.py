#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Example using WrapBokeh

"""
from flask import Blueprint, request, redirect, jsonify
from flask import current_app as app
from bokeh.layouts import column, row, layout, Spacer, widgetbox
from bokeh.plotting import figure
from bokeh.models.widgets import Paragraph, Div
from bokeh.models.widgets.inputs import Select
from bokeh.models import AjaxDataSource
from bokeh.models.callbacks import CustomJS


import math
from pywrapbokeh import WrapBokeh

# !! WARNING dominate tag names can collide with bokeh names :(
from dominate.tags import style
from dominate.util import raw

from ex_index import redirect_lookup_table

PAGE_URL = '/a/'
PAGE_URL_GET_DATA = "/get_new_data"
widgets = None

x, y = 0, 0

ex_get_new_data = Blueprint('ex_get_new_data', __name__)
@ex_get_new_data.route(PAGE_URL_GET_DATA, methods=['POST'])
def get_x():
    global x, y
    x = x + 0.1
    y = math.sin(x)
    return jsonify(x=[x], y=[y])


ex_a = Blueprint('ex_a', __name__)
@ex_a.route(PAGE_URL, methods=['GET', 'POST'])
def page_a():
    global widgets

    init_widgets()

    # Create a dominate document, see https://github.com/Knio/dominate
    widgets.dominate_document()
    with widgets.dom_doc.body:  # add css elements here...
        style(raw("""body {background-color:powderblue;}"""))

    args, _redirect_page_metrics = widgets.process_req(request)
    if not args: return _redirect_page_metrics
    app.logger.info("{} : args {}".format(PAGE_URL, args))

    # redirect to another page based on widget data...
    _redirect = redirect_lookup_table(args.get("sel_nexturl", None))
    if _redirect: return redirect(_redirect)

    widgets.get("sel_nexturl").value = '99'

    doc_layout = layout(sizing_mode='scale_width')

    doc_layout.children.append(row(Div(text="""<h1>pywrapBokeh</h1><h2>Page A</h2>"""),
                                   Paragraph(text="""Play with all these widgets.""")))

    source = AjaxDataSource(data=dict(x=[], y=[]),
                            adapter=CustomJS(code="return cb_data.response"),
                            data_url="http://127.0.0.1:6800{}".format(PAGE_URL_GET_DATA),
                            polling_interval=1000,
                            mode='append')

    fig = figure(title="Streaming Example")
    fig.line('x', 'y', source=source)

    doc_layout.children.append(fig)

    doc_layout.children.append(row(widgets.get("sel_nexturl")))

    return widgets.render(doc_layout)


def init_widgets():
    global widgets

    widgets = WrapBokeh(PAGE_URL, app.logger)

    widgets.add("sel_nexturl", Select(options=[('99', 'Select Next Page'),
                                               ('0', 'Home'),
                                               ('2', 'Form Example'),
                                               ('3', 'Page C'),
                                               ('4', 'Page D')],
                                      value=None,
                                      title="Select URL"))

    # Next
    # https://bokeh.pydata.org/en/latest/docs/user_guide/examples/interaction_data_table.html

    widgets.init()

