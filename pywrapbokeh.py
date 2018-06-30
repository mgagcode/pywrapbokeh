#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from bokeh.embed import components
from bokeh.models.widgets.inputs import DatePicker, MultiSelect, TextInput
from bokeh.models import Slider
from bokeh.models.callbacks import CustomJS

from dominate.tags import *
import dominate
from dominate.util import raw


class WrapBokeh(object):
    """
    TODO....
    """

    def __init__(self):
        self.widgets = {}

    def dominate_document(self, bokeh_version='0.13.0'):
        d = dominate.document()
        with d.head:
            link(href="https://cdn.pydata.org/bokeh/release/bokeh-{bokeh_version}.min.css".format(bokeh_version=bokeh_version),
                 rel="stylesheet",
                 type="text/css")
            script(src="https://cdn.pydata.org/bokeh/release/bokeh-{bokeh_version}.min.js".format(bokeh_version=bokeh_version))
            link(href="https://cdn.pydata.org/bokeh/release/bokeh-widgets-{bokeh_version}.min.css".format(bokeh_version=bokeh_version),
                 rel="stylesheet",
                 type="text/css")
            script(src="https://cdn.pydata.org/bokeh/release/bokeh-widgets-{bokeh_version}.min.js".format(bokeh_version=bokeh_version))
            meta(charset="UTF-8")

        with d.body:
            js = """
            function encodeQueryData(data) {
                let ret = [];
                for (let d in data)
                    ret.push(encodeURIComponent(d) + '=' + encodeURIComponent(data[d]));
                return ret.join('&');
            }
            """
            script(raw(js))

        return d


    def _all_callback(self):
        """ a bokeh CustomJS that will be called when a widget is changed, that puts the
        value of the widget in the URL, for ALL widgets.
        :return: CustomJS
        """
        _parms = "{"
        _args = {}
        for w_name, w_params in self.widgets.items():
            if w_params.get("obj", False):
                _parms += """'{name}':{name}.{value},""".format(name=w_params["arg_name"], value=w_params["value_field"])
                _args[w_params["arg_name"]] = w_params["obj"]
        _parms += "}"
        # print(_parms)

        _code = """
                var params = {}
                var url = '/?' + encodeQueryData(params)
                window.location.replace(url);
            """.format(_parms)
        # print(_code)
        return CustomJS(args=_args, code=_code)

    def _start_end_datepicker_handler(self, args, start):
        """ Handler for a start/end DatePicker pair of widgets
        :param args: dict URL args
        :param start: start DatePicker widget
        :param end: end DatePicker widget
        """

        end = self.widgets[start["pair"]]

        d_yesterday = datetime.today() - timedelta(days=1)
        d_year_ago = datetime.today() - timedelta(days=365)

        # handle args related to which date picker the user last used
        if not start['arg_name'] in args:
            # the url did not have this value, assume first time being called
            min_end_date = datetime.today() - timedelta(days=1)
            curr_start_date = d_yesterday
        elif args[start['arg_name']].split(".")[0].isdigit():
            # when the end DatePicker is used, start Datepicker time comes as a epoch with ms
            curr_start_date = datetime.fromtimestamp(int(args[start['arg_name']].split(".")[0]) / 1000)
            min_end_date = curr_start_date
        else:
            curr_start_date = datetime.strptime(args[start['arg_name']], "%a %b %d %Y")  # 'Mon Jun 18 2018'
            curr_start_date += timedelta(
                days=1)  # this fixes a bug where the date picked is one day behind the user selection
            min_end_date = curr_start_date

        if not end['arg_name'] in args:
            curr_end_date = datetime.today()
        elif args[end['arg_name']].split(".")[0].isdigit():
            curr_end_date = datetime.fromtimestamp(int(args[end['arg_name']].split(".")[0]) / 1000)
        else:
            curr_end_date = datetime.strptime(args[end['arg_name']], "%a %b %d %Y")  # 'Mon Jun 18 2018'
            curr_end_date += timedelta(
                days=1)  # this fixes a bug where the date picked is one day behind the user selection

        start["value"] = curr_start_date
        start['obj'] = DatePicker(title=start["title"], min_date=d_year_ago, max_date=datetime.today(),
                                  value=curr_start_date, width=start["width"])

        end["value"] = curr_end_date
        end['obj'] = DatePicker(title=end["title"], min_date=min_end_date, max_date=datetime.today(),
                                value=curr_end_date, width=end["width"])

    def _multi_select_handler(self, args, ms):
        """ multi-select handler
        :param args: dict URL args
        :param ms: multiselect widget
        """
        selected = args.get(ms["arg_name"], "").split(",")
        ms["value"] = selected
        ms["obj"] = MultiSelect(options=ms["options"],
                                value=selected,
                                title=ms["title"],
                                width=ms["width"],
                                size=ms["size"])

    def _input_handler(self, args, input):
        """ INput text handler
        :param args: dict URL args
        :param input: input widget
        """
        input["value"] = args.get(input["arg_name"], input["value"])
        input["obj"] = TextInput(title=input["title"], value=input["value"])

    def _slider_handler(self, args, slider):
        """ Slider handler
        :param args: dict URL args
        :param input: input widget
        """
        _value = args.get(slider["arg_name"], slider["value"])
        if _value == 'NaN':
            _value = slider["value"]
        if isinstance(_value, str):
            slider["value"] = float(_value) if "." in _value else int(_value)
        slider["obj"] = Slider(title=slider["title"], value=slider["value"], start=slider["start"], end=slider["end"],
                               step=slider["step"], callback_policy='mouseup')

    def _multi_select_handler(self, args, ms):
        """
        :param args: dict URL args
        :param ms: multiselect widget
        """
        selected = args.get(ms["arg_name"], "").split(",")
        ms["value"] = selected
        ms["obj"] = MultiSelect(options=ms["options"], value=selected, title=ms["title"])

    def _set_all_callbacks(self):
        for key in self.widgets:
            if self.widgets[key]["obj"] is not None:
                self.widgets[key]["obj"].callback = self._all_callback()

    def add_datepicker_pair(self, start, end):
        """ Create a datepicker pair, like start and end
        :param start: dict of start date params
                        { "name": <string id of widget>
                          "title": <string>
                          "value": <datetime>
                          "width": <uint or None for auto>
        :param end: dict of end date params, see start
        :return: True on success, False otherwise
        """

        # TODO: determine dicts have proper params...
        if start["name"] in self.widgets: return False
        if end["name"] in self.widgets: return False

        self.widgets[start["name"]] = {
            'obj': None,
            'value_field': 'value',
            'arg_name': '{}_date'.format(start["name"]),
            'value': start["value"],
            'title': start["title"],
            "width": start["width"],
            "pair": end["name"],
            "handler": self._start_end_datepicker_handler
        }

        self.widgets[end["name"]] = {
            'obj': None,
            'value_field': 'value',
            'arg_name': '{}_date'.format(end["name"]),
            'value': end["value"],
            'title': end["title"],
            "width": end["width"],
            "handler": None
        }
        self._start_end_datepicker_handler({}, self.widgets[start["name"]])
        self._set_all_callbacks()
        return True

    def add_slider(self, name, title, value, start=0, end=10, step=1, width=None):
        """ Create a slider
        :param name:
        :param title:
        :param value:
        :param start:
        :param end:
        :param step:
        :param width:
        :return: True on success, False otherwise
        """

        if name in self.widgets: return False

        self.widgets[name] = {
            'obj': None,
            'value_field': 'value',
            'arg_name': '{}'.format(name),
            'value': value,
            'title': title,
            'start': start,
            'end': end,
            'step': step,
            "width": width,
            "handler": self._slider_handler
        }
        self._slider_handler({}, self.widgets[name])
        self._set_all_callbacks()
        return True

    def add_multi_select(self, name, options, value=None, title=None, size=None, width=None):
        """ Create a multi select widget
        :param name:
        :param options: [ ( "<return_value>", "<display_value>"), ... ]
        :param value:
        :param title:
        :return: True on success, False otherwise
        """

        if name in self.widgets: return False

        self.widgets[name] = {
            'obj': None,
            'value_field': 'value',
            'arg_name': '{}'.format(name),
            'value': value,
            'title': title,
            'options': options,
            'width': width,
            'size': size,
            "handler": self._multi_select_handler
        }
        self._multi_select_handler({}, self.widgets[name])
        self._set_all_callbacks()
        return True

    def process_url(self, args):
        for key, widget in self.widgets.items():
            if widget["obj"] is not None and widget["handler"] is not None:
                widget["handler"](args, widget)

        self._set_all_callbacks()

    def get_dom(self, name):
        return self.widgets[name]["obj"]

    def get_value(self, name):
        return self.widgets[name]["value"]

    def set_value(self, name, value):
        self.widgets[name]["value"] = value

    def get_value_all(self):
        result = {}
        for key, widget in self.widgets.items():
            if widget["obj"] is not None and widget["handler"] is not None:
                result[key] = widget["value"]
        return result

    def render(self, d, layout):
        _script, _div = components(layout)
        d.body += raw(_script)
        d.body += raw(_div)
        return d



