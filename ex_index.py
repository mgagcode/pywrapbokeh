#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Example using WrapBokeh

"""
from datetime import datetime, timedelta
from bokeh.layouts import column, row, layout, Spacer
from bokeh.plotting import figure
from bokeh.models import LinearAxis, Range1d
from bokeh.models import Slider

from flask import redirect, abort, Blueprint
from flask import request
from flask import current_app as app

from numpy import pi, arange, sin, linspace

from pywrapbokeh import WrapBokeh

from ex_utils import redirect_lookup_table

PAGE_URL = '/'

ex_index = Blueprint('ex_index', __name__)
@ex_index.route(PAGE_URL, methods=['GET', 'POST'])
def test_main():

    args = widgets.process_req(request)

    # reset page to initial values, if there are no parms
    if not args: reset_widgets()

#    if args.get("my_sider", False):
#        widgets.set_value("my_sider", int(args.get("my_sider", 1)))

    doc_layout = layout(sizing_mode='scale_width')
    doc_layout.children.append(row(widgets.get("my_sider")))

    # Create a dominate document, see https://github.com/Knio/dominate
    d = widgets.dominate_document()
    d = widgets.render(d, doc_layout)
    return "{}".format(d)

def reset_widgets():
    """ reset widget values to some default
    """
    print("fff")
    widgets.set_value("my_sider", 1)


my_slider = Slider(title='Age', value=25, start=1, end=99, step=1, callback_policy='mouseup', width=200)

widgets = WrapBokeh(PAGE_URL, app.logger)
widgets.add("my_sider", Slider(title='Age',
                               value=25,
                               start=1,
                               end=99,
                               step=1,
                               callback_policy='mouseup',
                               width=200))
widgets.init()

