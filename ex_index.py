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

app = Flask(__name__)
app.register_blueprint(ex_a)


widgets = None


def _redirect_example_multi_select(value):
    if 'a' in value:   return "/a/"
    elif 'b' in value: return "/b/"
    elif 'c' in value: return "/c/"
    elif 'd' in value: return "/"
    else: return None


@app.route("/", methods=['GET'])
def test_main():
    args = request.args.to_dict()
    print(args)

    # reset page to initial values, if there are no parms
    if not args: reset_widgets()

    widgets.process_url(args)

    # redirect to another page based on widget data...
    _redirect = _redirect_example_multi_select(widgets.get_value("ms1"))
    if _redirect: return redirect(_redirect)

    # make a graph, example at https://bokeh.pydata.org/en/latest/docs/user_guide/plotting.html
    amplitude = float(args.get("amp", 1.0))
    x = arange(-2 * pi, 2 * pi, 0.1)
    y = amplitude * sin(x)
    y2 = linspace(0, 100, len(y))
    p = figure(x_range=(-6.5, 6.5), y_range=(-1.1, 1.1), width=400, height=200)

    p.circle(x, y, color="red")

    p.extra_y_ranges = {"foo": Range1d(start=0, end=100)}
    p.circle(x, y2, color="blue", y_range_name="foo")
    p.add_layout(LinearAxis(y_range_name="foo"), 'left')

    doc_layout = layout(sizing_mode='scale_width')
    doc_layout.children.append(row(widgets.get_dom("Start"), Spacer(width=50), widgets.get_dom("End")))
    doc_layout.children.append(row(widgets.get_dom("amp"), widgets.get_dom("ms1")))
    doc_layout.children.append(column(p))

    d = widgets.dominate_document()
    d = widgets.render(d, doc_layout)
    return "{}".format(d)


def init_widgets():
    start = {"name": "Start", "title": "Start", "value": datetime.today(), "width": 150}
    end = {"name": "End", "title": "End", "value": datetime.today(), "width": 150}
    if not widgets.add_datepicker_pair(start, end): return False

    if not widgets.add_slider(name="amp",
                              title="Amplitude",
                              value=1,
                              start=0.1,
                              end=2.0,
                              step=0.1): return False

    if not widgets.add_multi_select(name="ms1",
                                    options=[('a', '1'), ('b', '2'), ('c', '3'), ('d', 'Home')],
                                    size=2,
                                    width=30): return False


def reset_widgets():
    widgets.set_value("amp", 1.0)


widgets = WrapBokeh()
init_widgets()

app.run(host="0.0.0.0", port=6800)