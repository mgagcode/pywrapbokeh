#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Example using WrapBokeh

"""
from datetime import datetime, timedelta
from bokeh.layouts import column, row, layout, Spacer
from bokeh.plotting import figure
from bokeh.models import LinearAxis, Range1d
from bokeh.models import Slider, RangeSlider
from bokeh.models.widgets.inputs import DatePicker, MultiSelect, TextInput, Select
from bokeh.models.widgets.buttons import Button, Toggle, Dropdown
from bokeh.models.widgets import Paragraph, Div
from bokeh.models.widgets import CheckboxButtonGroup, CheckboxGroup, RadioGroup, RadioButtonGroup


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
    if not args:
        widgets.get("s_age").value = 25
        widgets.get("s_amp").value = 1
        text_age = "Please tell me how old you are..."
    else:
        text_age = "Wow, you are {} years old!".format(widgets.get("s_age").value)

    p_text_age = Paragraph(text=text_age, width=None, height=None)

    # make a graph, example at https://bokeh.pydata.org/en/latest/docs/user_guide/plotting.html
    amplitude = float(args.get("s_amp", 1.0))
    x = arange(-2 * pi, 2 * pi, 0.1)
    y = amplitude * sin(x)
    y2 = linspace(0, 100, len(y))
    p = figure(x_range=(-6.5, 6.5), y_range=(-2.0, 2.0), width=600, height=200)
    p.circle(x, y, color="red")
    p.extra_y_ranges = {"foo": Range1d(start=0, end=100)}
    p.circle(x, y2, color="blue", y_range_name="foo")
    p.add_layout(LinearAxis(y_range_name="foo"), 'left')

    doc_layout = layout(sizing_mode='scale_width')
    doc_layout.children.append(row(Div(text="""<h1>pywrapBokeh</h1>"""),
                               row(Paragraph(text="""Play with all these widgets."""))))
    doc_layout.children.append(column(widgets.get("s_age"), p_text_age))
    doc_layout.children.append(row(widgets.get("dp_birthday"), row(widgets.get("msel_fruit"))))
    doc_layout.children.append(column(widgets.get("s_amp"), p))
    doc_layout.children.append(row(widgets.get("b_test"), widgets.get("toggle_1"), widgets.get("dropdn_1")))
    doc_layout.children.append(row(widgets.get("sel_relations"), widgets.get("cbbg_music"), widgets.get("cbg_music")))
    doc_layout.children.append(row(widgets.get("rbg_music"), widgets.get("rg_music"), widgets.get("rslider_amp")))

    # Create a dominate document, see https://github.com/Knio/dominate
    d = widgets.dominate_document()
    d = widgets.render(d, doc_layout)
    return "{}".format(d)


widgets = WrapBokeh(PAGE_URL, app.logger)
widgets.add("s_age", Slider(title='Age',
                            value=25,
                            start=1,
                            end=99,
                            step=1,
                            callback_policy='mouseup',
                            width=200))

widgets.add("dp_birthday", DatePicker(title="Birthday",
                                      min_date=None,
                                      max_date=datetime.today(),
                                      value=datetime.today(),
                                      width=300))

widgets.add("msel_fruit", MultiSelect(options=[('0', 'Apples'),
                                               ('1', 'Strawberries'),
                                               ('2', 'Oranges'),
                                               ('3', 'Grapefruit'),
                                               ('4', 'Banannas')],
                                      value=[],
                                      title="Fruit"))

widgets.add("s_amp", Slider(title='Amplitude',
                            value=1,
                            start=0,
                            end=2,
                            step=0.1,
                            callback_policy='mouseup',
                            width=200))

widgets.add("b_test", Button(label="Press me!"))
widgets.add("toggle_1", Toggle(label="Toggle me!"))
widgets.add("dropdn_1", Dropdown(label="Menu", menu=[("First",  '0'),
                                                     ("Second", '1'),
                                                     None,
                                                     ("End",    '2')]))

widgets.add("sel_relations", Select(options=[('0', 'Father'),
                                          ('1', 'Mother'),
                                          ('2', 'Baby'),
                                          ('3', 'Sister'),
                                          ('4', 'brother')],
                                 value=None,
                                 title="Relations"))

widgets.add("cbbg_music", CheckboxButtonGroup(labels=["Rock", "Country", "Classical"], active=[]))
widgets.add("cbg_music", CheckboxGroup(labels=["Rock", "Country", "Classical"], active=[]))
widgets.add("rbg_music", RadioButtonGroup(labels=["Rock", "Country", "Classical"], active=None))
widgets.add("rg_music", RadioGroup(labels=["Rock", "Country", "Classical"], active=None))

widgets.add("rslider_amp", RangeSlider(title='Amplitude',
                                       value=(0.5, 1.5),
                                       start=0,
                                       end=2,
                                       step=0.1,
                                       callback_policy='mouseup',
                                       width=200))

widgets.init()

