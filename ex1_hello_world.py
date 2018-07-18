#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask
from flask import request
from flask import current_app as app
from bokeh.layouts import layout, column
from bokeh.models.widgets import Paragraph, Div
from bokeh.models.widgets.inputs import Select

from pywrapbokeh import WrapBokeh

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def hello():
    # check/get page metrics and get args for the page
    args, _redirect_page_metrics = widgets.process_req(request)
    if not args: return _redirect_page_metrics
    app.logger.info("{} : args {}".format("/", args))

    selected_fruit = args.get("sel_fruit", "Unknown")
    if selected_fruit is not "Unknown":
        selected_fruit = fruits[int(selected_fruit)][1]  # get name of fruit

    # check args here for actions that would redirect to another page
    # if args.get( name ) == something: return redirect( new_url )

    # this line should go after any "return redirect" statements above
    # see https://github.com/Knio/dominate
    widgets.dominate_document()  # create dominate document

    # start a bokeh layout
    doc_layout = layout(sizing_mode='scale_width')

    # append items to the document
    doc_layout.children.append(column(Div(text="""<h1>Hello World!</h1>"""),
                                      Paragraph(text="""Your favorite fruit is {}""".format(selected_fruit))))

    # append a pywrapbokeh widget
    doc_layout.children.append(widgets.get("sel_fruit"))

    # render page
    return widgets.render(doc_layout)


# create pywrapbokeh object
widgets = WrapBokeh("/", app.logger)

# add bokeh widgets to the pywrapbokeh object
# - order does not matter
# - API pattern,
#   - WrapBokeh.add( <name_of_widget>, <bokeh API>(..., [css_classes=['sel_fruit']]))
#   - if you want to affect widget properties (color, font size, etc) you need to set css_classes
fruits = [('0', 'Bananna'), ('1', 'Blueberry'), ('2', 'Orange'), ('3', 'Peach'), ('4', 'Apple')]
widgets.add("sel_fruit", Select(options=fruits, value=None, title="Select Fruit", css_classes=['sel_fruit']))

widgets.init()

app.run(host="0.0.0.0", port=6800, debug=False)

