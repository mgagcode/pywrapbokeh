#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Example using WrapBokeh

"""

from datetime import datetime, timedelta
from bokeh.layouts import column, row, layout, Spacer
from bokeh.plotting import figure
from bokeh.models import LinearAxis, Range1d

from flask import Flask, redirect, abort
from flask import request

from numpy import pi, arange, sin, linspace

from pywrapbokeh import WrapBokeh
from ex_a import ex_a

from ex_utils import _redirect_lookup_table

app = Flask(__name__)
app.register_blueprint(ex_a)


widgets = None


@app.route("/", methods=['GET'])
def test_main():
    args = request.args.to_dict()
    print(args)

    # reset page to initial values, if there are no parms
    if not args: reset_widgets()

    widgets.process_url(args)

    # redirect to another page based on widget data...
    _redirect = _redirect_lookup_table(widgets.get_value("sel_goto_page"))
    if _redirect: return redirect(_redirect)

    # make a graph, example at https://bokeh.pydata.org/en/latest/docs/user_guide/plotting.html
    amplitude = float(args.get("slider_amp", 1.0))
    x = arange(-2 * pi, 2 * pi, 0.1)
    y = amplitude * sin(x)
    y2 = linspace(0, 100, len(y))
    p = figure(x_range=(-6.5, 6.5), y_range=(-1.1, 1.1), width=400, height=200)

    p.circle(x, y, color="red")

    p.extra_y_ranges = {"foo": Range1d(start=0, end=100)}
    p.circle(x, y2, color="blue", y_range_name="foo")
    p.add_layout(LinearAxis(y_range_name="foo"), 'left')

    doc_layout = layout(sizing_mode='scale_width')
    doc_layout.children.append(row(widgets.get_dom("datepair_start"), Spacer(width=50), widgets.get_dom("datepair_end")))
    doc_layout.children.append(row(widgets.get_dom("slider_amp"), widgets.get_dom("msel_fruit"), widgets.get_dom("sel_goto_page")))
    doc_layout.children.append(column(p))

    # Create a dominate document, see https://github.com/Knio/dominate
    d = widgets.dominate_document()
    d = widgets.render(d, doc_layout)
    return "{}".format(d)


def init_widgets():
    """ init widgets
    :return: True on success, False otherwise
    """
    start = {"name": "datepair_start", "title": "Start", "value": datetime.today(), "width": 150}
    end = {"name": "datepair_end", "title": "End", "value": datetime.today(), "width": 150}
    if not widgets.add_datepicker_pair(start, end): return False

    if not widgets.add_slider(name="slider_amp",
                              title="Amplitude",
                              value=1,
                              start=0.1,
                              end=2.0,
                              step=0.1): return False

    if not widgets.add_multi_select(name="msel_fruit",
                                    options=[('a', 'Apples'), ('b', 'Strawberries'), ('c', 'Oranges'), ('d', 'Grapefruit')],
                                    size=2,
                                    width=30): return False

    if not widgets.add_select(name="sel_goto_page",
                              options=[('_', 'Select Next Page'), ('a', 'Page a'), ('b', 'Page b'), ('c', 'Page c')],
                              size=2,
                              value=None,
                              width=30): return False

    return True


def reset_widgets():
    """ reset widget values to some default
    """
    widgets.set_value("slider_amp", 1.0)


widgets = WrapBokeh()
init_widgets()

app.run(host="0.0.0.0", port=6800)