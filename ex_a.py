#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Example using WrapBokeh

"""
from flask import Blueprint, request, redirect
from bokeh.layouts import column, row, layout, Spacer
from pywrapbokeh import WrapBokeh

widgets = None

def _redirect_example_multi_select(value):
    if 'a' in value:   return "/a/"
    elif 'b' in value: return "/b/"
    elif 'c' in value: return "/c/"
    elif 'd' in value: return "/"
    else: return None


ex_a = Blueprint('ex_a', __name__)
@ex_a.route('/a/', methods=['GET'])
def page_a():
    args = request.args.to_dict()
    print(args)

    widgets.process_url(args)

    # redirect to another page based on widget data...
    _redirect = _redirect_example_multi_select(widgets.get_value("ms1"))
    if _redirect: return redirect(_redirect)

    doc_layout = layout(sizing_mode='scale_width')
    doc_layout.children.append(row(widgets.get_dom("ms1")))

    d = widgets.dominate_document()
    d = widgets.render(d, doc_layout)
    return "{}".format(d)


def init_widgets():
    if not widgets.add_multi_select(name="ms1",
                                    options=[('a', '1'), ('b', '2'), ('c', '3'), ('d', 'Home')],
                                    size=2,
                                    width=30): return False


def reset_widgets():
    pass


widgets = WrapBokeh()
init_widgets()