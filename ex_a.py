#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Example using WrapBokeh

"""
from flask import Blueprint, request, redirect
from flask import current_app as app
from bokeh.layouts import column, row, layout, Spacer
from pywrapbokeh import WrapBokeh

from ex_utils import redirect_lookup_table

PAGE_URL = '/a/'

ex_a = Blueprint('ex_a', __name__)
@ex_a.route(PAGE_URL, methods=['GET'])
def page_a():
    args = request.args.to_dict()
    app.logger.info(args)

    widgets.process_url(args)

    # redirect to another page based on widget data...
    _redirect = redirect_lookup_table(widgets.get_value("sel_goto_page"))
    if _redirect: return redirect(_redirect)

    # consider this first graph example, https://bokeh.pydata.org/en/latest/docs/user_guide/interaction/callbacks.html

    doc_layout = layout(sizing_mode='scale_width')
    doc_layout.children.append(row(widgets.get_dom("datep_birthday")))
    doc_layout.children.append(row(widgets.get_dom("sel_goto_page")))

    d = widgets.dominate_document()
    d = widgets.render(d, doc_layout)
    return "{}".format(d)


def init_widgets():
    """ init widgets
    :return: True on success, False otherwise
    """
    if not widgets.add_select(name="sel_goto_page",
                              options=[('_', 'Select Next Page'), ('b', 'Page b'), ('c', 'Page c'), ('d', 'Home')],
                              size=2,
                              width=30): return False

    if not widgets.add_datepicker(name="datep_birthday", title='Birthday'): return False

    return True


def reset_widgets():
    """ reset widget values to some default
    """
    pass


widgets = WrapBokeh(PAGE_URL, app.logger)
init_widgets()