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

from ex_index import redirect_lookup_table

# !! WARNING dominate tag names can collide with bokeh names :(
from dominate.tags import style
from dominate.util import raw

PAGE_URL = '/b/'
widgets = None

geo_info = {
    "United States": ["Washington", "New York", "Texas", "California", "Montanna", "Michigan", "New Mexico"],
    "Canada": ["Ontario", "Saskatchewan", "Manitoba", "Alberta", "Quebec", "Britsh Columbia"]
}


ex_b = Blueprint('ex_b', __name__)
@ex_b.route(PAGE_URL, methods=['GET', 'POST'])
def page_b():
    """
    Shows example of doing form input, with drop downs that dynamically
    change content.
    """

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

    widgets.add_css("b_submit", { 'button': {'background-color': '#98FB98'}})

    # update state of state pulldown based on country
    if args.get("sel_country", False) and args["sel_country"] in geo_info.keys():
        widgets.get("sel_state").options = [('', 'Select State')] + [(x, x) for x in geo_info[args["sel_country"]]]

    # on submit, validate form contents
    # TODO: this could be a function
    submitted = args.get("b_submit", False)
    validated = True
    if submitted:
        if args.get("tin_fname", False):
            if args["tin_fname"] in ["", "first name"]:
                validated = False
                widgets.add_css("tin_fname", {'input' :{'background-color': '#F08080'}})

        if args.get("tin_lname", False):
            if args["tin_lname"] in ["", "last name"]:
                validated = False
                widgets.add_css("tin_lname", {'input' :{'background-color': '#F08080'}})

        if args.get("sel_country", False):
            if args["sel_country"] in ["null"]:
                validated = False
                widgets.add_css("sel_country", {'select' :{'background-color': '#F08080'}})

        if args.get("sel_state", False):
            if args["sel_state"] in ["null"]:
                validated = False
                widgets.add_css("sel_state", {'select' :{'background-color': '#F08080'}})

        if validated:
            app.logger.info("validated: {}".format(args))
            # TODO: send form data somewhere as a JSON object
            return redirect("/b/")

    doc_layout = layout(sizing_mode='scale_width')
    doc_layout.children.append(row(Div(text="""<h1>pywrapBokeh</h1><h2>Page B</h2>"""),
                                   Paragraph(text="""Play with all these widgets.""")))

    if submitted and not validated:
        doc_layout.children.append(row(Div(text="""<p style="color:#F08080;">Fix the input errors below...</p>""")))
    else:
        doc_layout.children.append(row(Div(text="""<p>Enter your data...</p>""")))

    wbox = widgetbox(widgets.get("tin_fname"),
                     widgets.get("tin_lname"),
                     widgets.get("sel_country"),
                     widgets.get("sel_state"),
                     widgets.get("b_submit"))

    doc_layout.children.append(row([Spacer(width=200), wbox]))

    doc_layout.children.append(widgets.get("sel_nexturl"))

    return widgets.render(doc_layout)


def init_widgets():
    global widgets
    widgets = WrapBokeh(PAGE_URL, app.logger)

    widgets.add("tin_fname", TextInput(title="First Name:", placeholder="first name", css_classes=['tin_fname']))
    widgets.add("tin_lname", TextInput(title="Last Name:", placeholder="last name", css_classes=['tin_lname']))
    widgets.add("b_submit", Button(label="Submit", css_classes=['b_submit']))


    countries = [('', 'Select Country')] + [(x, x) for x in geo_info.keys()]
    states = [('', 'Select State')] + [(x, x) for x in geo_info["United States"]]

    widgets.add("sel_country", Select(options=countries, value=None, title="Select Country", css_classes=['sel_country']))
    widgets.add("sel_state",   Select(options=states,    value=None, title="Select State",   css_classes=['sel_state']))

    widgets.add("sel_nexturl", Select(options=[('99', 'Select Next Page'),
                                               ('0', 'Home'),
                                               ('1', 'Ajax Stream Example'),
                                               ('3', 'Page C'),
                                               ('4', 'Page D')],
                                      value=None,
                                      title="Select URL",
                                      css_classes=['sel_nexturl']))

    widgets.init()

