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
from bokeh.models.widgets.sliders import DateSlider
from bokeh.models.widgets.inputs import DatePicker, MultiSelect, TextInput, Select
from bokeh.models.widgets.buttons import Button, Toggle, Dropdown
from bokeh.models.widgets import Paragraph, Div
from bokeh.models.widgets import CheckboxButtonGroup, CheckboxGroup, RadioGroup, RadioButtonGroup

from flask import redirect, abort, Blueprint
from flask import request
from flask import current_app as app

# !! WARNING dominate tag names can collide with bokeh names :(
from dominate.tags import style
from dominate.util import raw

from numpy import pi, arange, sin, linspace

from pywrapbokeh import WrapBokeh

def redirect_lookup_table(value):
    """ based on a key (value) return the next URL to go to
    :param value: key to url
    :return: url, or None if value is not mapped
    """
    if not value: return None

    app.logger.info(value)
    if   '1' in value: return "/a/"
    elif '2' in value: return "/b/"
    elif '3' in value: return "/c/"
    elif '0' in value: return "/"
    else:
        app.logger.error("Unknown link request: {}".format(value))

    return None

PAGE_URL = '/'

ex_index = Blueprint('ex_index', __name__)
@ex_index.route(PAGE_URL, methods=['GET', 'POST'])
def test_main():
    # Create a dominate document, see https://github.com/Knio/dominate
    widgets.dominate_document()
    with widgets.dom_doc.body:  # add css elements here...
        style(raw("""body {background-color:powderblue;}"""))

    args, _redirect_page_metrics = widgets.process_req(request)
    if not args: return _redirect_page_metrics
    app.logger.info("{} : args {}".format(PAGE_URL, args))

    # redirect to another page based on widget data...
    _redirect = redirect_lookup_table(args.get("sel_nexturl", None))
    if _redirect:
        widgets.get("sel_nexturl").value = None
        # TODO: make a widget set value method?
        # TODO: or make a init function for all the widgets, and re-init them?
        return redirect(_redirect)

    # reset page to initial values, if there are no parms
    # the widgets have state, so update if required
    if not args:
        widgets.get("sel_nexturl").value = ''  # reset next url select

        widgets.get("s_age").value = 25
        widgets.get("s_amp").value = 1
        text_age = "Please tell me how old you are..."
    else:
        text_age = "Wow, you are {} years old!".format(widgets.get("s_age").value)

    p_text_age = Paragraph(text=text_age, width=None, height=None)

    # set various widget attributes
    widgets.add_css("dp_birthday", {'input': {'background-color': '#98FB98'},
                                    'label': {'background-color': '#98FB98',
                                              'font-size':        '16px'}})

    widgets.add_css("s_age", {'label': {'background-color': '#98FB98',
                                        'font-size':        '16px'}})

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
                                   Paragraph(text="""Play with all these widgets.""")))
    doc_layout.children.append(column(widgets.get("s_age"), p_text_age))
    doc_layout.children.append(row(widgets.get("dp_birthday"), widgets.get("msel_fruit"), widgets.get("ds_birthday")))
    doc_layout.children.append(column(widgets.get("s_amp"), p))
    doc_layout.children.append(row(widgets.get("b_test"), widgets.get("toggle_1"), widgets.get("dropdn_1")))
    doc_layout.children.append(row(widgets.get("sel_nexturl"), widgets.get("cbbg_music"), widgets.get("cbg_music")))
    doc_layout.children.append(row(widgets.get("rbg_music"), widgets.get("rg_music"), widgets.get("rslider_amp")))

    return widgets.render(doc_layout)


widgets = WrapBokeh(PAGE_URL, app.logger)
widgets.add("s_age", Slider(title='Age',
                            value=25,
                            start=1,
                            end=99,
                            step=1,
                            callback_policy='mouseup',
                            width=200,
                            css_classes=['s_age']))

widgets.add("dp_birthday", DatePicker(title="Birthday",
                                      min_date=None,
                                      max_date=datetime.today(),
                                      value=datetime.today(),
                                      width=300,
                                      css_classes=['dp_birthday']))

widgets.add("msel_fruit", MultiSelect(options=[('0', 'Apples'),
                                               ('1', 'Strawberries'),
                                               ('2', 'Oranges'),
                                               ('3', 'Grapefruit'),
                                               ('4', 'Banannas')],
                                      value=[],
                                      title="Fruit",
                                      css_classes=['msel_fruit']))

widgets.add("ds_birthday", DateSlider(title="Birthday",
                                      end=datetime.today(),
                                      start=datetime.today() - timedelta(days=30),
                                      step=1,
                                      value=datetime.today(),
                                      callback_policy='mouseup',
                                      css_classes=['ds_birthday']))

widgets.add("s_amp", Slider(title='Amplitude',
                            value=1,
                            start=0,
                            end=2,
                            step=0.1,
                            callback_policy='mouseup',
                            width=200,
                            css_classes=['s_amp']))

widgets.add("b_test", Button(label="Press me!", css_classes=['b_test']))
widgets.add("toggle_1", Toggle(label="Toggle me!", css_classes=['toggle_1']))
widgets.add("dropdn_1", Dropdown(label="Menu",
                                 menu=[("First",  '0'),
                                       ("Second", '1'),
                                       None,
                                       ("End",    '2')],
                                 css_classes=['dropdn_1']))

widgets.add("sel_nexturl", Select(options=[('99', 'Select Next Page'),
                                           ('1', 'Ajax Stream Example'),
                                           ('2', 'Form Example'),
                                           ('3', 'Page C'),
                                           ('4', 'Page D')],
                                  value=None,
                                  title="Select URL",
                                  css_classes=['sel_nexturl']))

widgets.add("cbbg_music", CheckboxButtonGroup(labels=["Rock", "Country", "Classical"], active=[], css_classes=['cbbg_music']))
widgets.add("cbg_music", CheckboxGroup(labels=["Rock", "Country", "Classical"], active=[], css_classes=['cbg_music']))
widgets.add("rbg_music", RadioButtonGroup(labels=["Rock", "Country", "Classical"], active=None, css_classes=['rbg_music']))
widgets.add("rg_music", RadioGroup(labels=["Rock", "Country", "Classical"], active=None, css_classes=['rg_music']))

widgets.add("rslider_amp", RangeSlider(title='Amplitude',
                                       value=(0.5, 1.5),
                                       start=0,
                                       end=2,
                                       step=0.1,
                                       callback_policy='mouseup',
                                       width=200,
                                       css_classes=['rslider_amp']))


widgets.init()

