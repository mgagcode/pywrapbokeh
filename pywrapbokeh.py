#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from bokeh.embed import components
from bokeh.models.widgets.inputs import DatePicker, MultiSelect, TextInput, Select
from bokeh.models.widgets.buttons import Button
from bokeh.models import Slider
from bokeh.models.callbacks import CustomJS

from dominate.tags import *
import dominate
from dominate.util import raw


class WrapBokeh(object):
    """ A class to wrap interactive widegts from bokeh.

    Notes:
    - if the boken widget is not interactive, then you don't need to use this, for example
      panels with tabs are not strictly interactive, ie no callback is needed
    """
    class StubLogger(object):
        """ stubb out logger if none is provided"""
        def info(self, *args,**kwargs): pass
        def error(self, *args,**kwargs): pass
        def debug(self, *args, **kwargs): pass
        def warning(self, *args, **kwargs): pass
        def critical(self, *args, **kwargs): pass

    logger = StubLogger()

    def __init__(self, url, logger=None):
        self.url = url
        if logger: self.logger = logger

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

            script(src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.0/jquery.min.js")

            meta(charset="UTF-8")

        with d.body:
            js = """
            function postAndRedirect(url, postData, callerWidget) {
                var postFormStr = "<form id='virtualForm' method='POST' action='" + url + "'>";
            
                for (var key in postData) {
                    if (postData.hasOwnProperty(key)) {
                        postFormStr += "<input type='hidden' name='" + encodeURIComponent(key) + "' value='" + unescape(encodeURIComponent(postData[key])) + "'></input>";
                    }
                }
                // add the widget that triggers the post
                postFormStr += "<input type='hidden' name='callerWidget' value='" + callerWidget + "'></input>";
             
                postFormStr += "</form>";
                //alert(postFormStr);
                //alert(postAndRedirect.caller);  // probably not useful
                
                var formElement = $(postFormStr);
            
                $('body').append(formElement);
                $('#virtualForm').submit();
            }         
            """
            script(raw(js))

        self.logger.info("created dominate document")
        self.logger.debug(d)
        return d

    def _make_args_parms(self):
        _parms_all = "{"
        _args_all = {}
        for w_name, w_params in self.widgets.items():
            if w_params.get("obj", False):
                _parms_all += """'{name}':{name}.{value},""".format(name=w_params["arg_name"], value=w_params["value_field"])
                _args_all[w_params["arg_name"]] = w_params["obj"]
        _parms_all += "}"
        self.logger.debug(_parms_all)

        _code_all = """
               var params = {};
               postAndRedirect('{}', params, 'callerWidget');
        """.format(_parms_all, self.url)
        self.logger.debug(_code_all)
        return _args_all, _code_all

    def _set_all_callbacks(self):
        """ attach a bokeh CustomJS that will be called when a widget is changed, that puts the
        value of the widget in the URL, for ALL widget callbacks.
        """
        _args, _code = self._make_args_parms()

        for key in self.widgets:
            if self.widgets[key]["obj"] is not None:
                __code = _code.replace("callerWidget", key)
                self.widgets[key]["obj"].callback = CustomJS(args=_args, code=__code)

    def _start_end_datepicker_handler(self, args, start):
        """ Handler for a start/end DatePicker pair of widgets
        :param args: dict URL args
        :param start: start DatePicker widget
        """

        end = self.widgets[start["pair"]]

        # handle args related to which date picker the user last used
        if not start['arg_name'] in args:
            # the url did not have this value, assume first time being called
            curr_start_date = start["value"]
        elif args[start['arg_name']].split(".")[0].isdigit():
            # when the end DatePicker is used, start Datepicker time comes as a epoch with ms
            curr_start_date = datetime.fromtimestamp(int(args[start['arg_name']].split(".")[0]) / 1000)
            end["min_date"] = curr_start_date
        else:
            curr_start_date = datetime.strptime(args[start['arg_name']], "%a %b %d %Y")  # 'Mon Jun 18 2018'
            curr_start_date += timedelta(
                days=1)  # this fixes a bug where the date picked is one day behind the user selection
            end["min_date"] = curr_start_date

        if not end['arg_name'] in args:
            curr_end_date = datetime.today()
        elif args[end['arg_name']].split(".")[0].isdigit():
            curr_end_date = datetime.fromtimestamp(int(args[end['arg_name']].split(".")[0]) / 1000)
        else:
            curr_end_date = datetime.strptime(args[end['arg_name']], "%a %b %d %Y")  # 'Mon Jun 18 2018'
            curr_end_date += timedelta(
                days=1)  # this fixes a bug where the date picked is one day behind the user selection

        start["value"] = curr_start_date
        start['obj'] = DatePicker(title=start["title"],
                                  min_date=start["min_date"],
                                  max_date=start["max_date"],
                                  value=curr_start_date,
                                  width=start["width"])

        end["value"] = curr_end_date
        end['obj'] = DatePicker(title=end["title"],
                                min_date=end["min_date"],
                                max_date=end["max_date"],
                                value=curr_end_date,
                                width=end["width"])

    def add_datepicker_pair(self, start, end):
        """ Create a datepicker pair, like start and end
        :param start: dict of start date params
                        { "name": <string id of widget>
                          "title": <string>
                          "value": <datetime>
                          "min_date": <datetime>
                          "min_date": <datetime>
                          "width": <uint or None for auto>
        :param end: dict of end date params, see start
        :return: True on success, False otherwise
        """

        if start["name"] in self.widgets:
            self.logger.error("{} already defined".format(start["name"]))
            return False
        if end["name"] in self.widgets:
            self.logger.error("{} already defined".format(end["name"]))
            return False

        s_min_date = start.get("min_date", None)
        s_max_date = start.get("max_date", None)
        s_value = start.get("value", datetime.today())
        s_title = start.get("title", "Start Title")
        s_width = start.get("width", None)

        self.widgets[start["name"]] = {
            'obj': None,
            'value_field': 'value',
            'arg_name': '{}_date'.format(start["name"]),
            'value': s_value,
            'min_date': s_min_date,
            'max_date': s_max_date,
            'title': s_title,
            "width": s_width,
            "pair": end["name"],
            "handler": self._start_end_datepicker_handler
        }

        e_min_date = end.get("min_date", None)
        e_max_date = end.get("max_date", None)
        e_value = end.get("value", datetime.today())
        e_title = end.get("title", "End Title")
        e_width = end.get("width", None)

        self.widgets[end["name"]] = {
            'obj': None,
            'value_field': 'value',
            'arg_name': '{}_date'.format(end["name"]),
            'value': e_value,
            'min_date': e_min_date,
            'max_date': e_max_date,
            'title': e_title,
            "width": e_width,
            "handler": None
        }
        self._start_end_datepicker_handler({}, self.widgets[start["name"]])
        self._set_all_callbacks()
        self.logger.info("added {}, {}".format(start["name"], end["name"]))
        return True

    def _datepicker_handler(self, args, datep):
        """ Handler for a DatePicker
        :param args: dict URL args
        :param start: start DatePicker widget
        """

        # handle args related to which date picker the user last used
        if not datep['arg_name'] in args:
            # the url did not have this value, assume first time being called
            curr_date = datep["value"]
        elif args[datep['arg_name']].split(".")[0].isdigit():
            # when the end DatePicker is used, start Datepicker time comes as a epoch with ms
            curr_date = datetime.fromtimestamp(int(args[datep['arg_name']].split(".")[0]) / 1000)
        else:
            curr_date = datetime.strptime(args[datep['arg_name']], "%a %b %d %Y")  # 'Mon Jun 18 2018'
            curr_date += timedelta(days=1)  # this fixes a bug where the date picked is one day behind the user selection

        datep["value"] = curr_date
        datep['obj'] = DatePicker(title=datep["title"],
                                  min_date=datep["min_date"],
                                  max_date=datep["max_date"],
                                  value=curr_date,
                                  width=datep["width"])

    def add_datepicker(self, name, title="Title", value=datetime.today(), min_date=None, max_date=None, width=None):

        if name in self.widgets:
            self.logger.error("{} already defined".format(name))
            return False

        self.widgets[name] = {
            'obj': None,
            'value_field': 'value',
            'arg_name': '{}_date'.format(name),
            'value': value,
            'min_date': min_date,
            'max_date': max_date,
            'title': title,
            "width": width,
            "handler": self._datepicker_handler
        }

        self._datepicker_handler({}, self.widgets[name])
        self._set_all_callbacks()
        return True

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

        if name in self.widgets:
            self.logger.error("{} already defined".format(name))
            return False

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

    def _multi_select_handler(self, args, ms):
        """
        :param args: dict URL args
        :param ms: multiselect widget
        """
        selected = args.get(ms["arg_name"], "").split(",")
        ms["value"] = selected
        ms["obj"] = MultiSelect(options=ms["options"], value=selected, title=ms["title"])

    def add_multi_select(self, name, options, value=None, title=None, size=None, width=None):
        """ Create a multi select widget
        :param name:
        :param options: [ ( "<return_value>", "<display_value>"), ... ]
        :param value:
        :param title:
        :return: True on success, False otherwise
        """

        if name in self.widgets:
            self.logger.error("{} already defined".format(name))
            return False

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

    def _select_handler(self, args, s):
        """
        :param args: dict URL args
        :param s: select widget
        """
        selected = args.get(s["arg_name"], "")
        s["value"] = selected
        s["obj"] = Select(options=s["options"], value=selected, title=s["title"])

    def add_select(self, name, options, value=None, title=None, size=None, width=None):
        """ Create a (single) select widget
        :param name:
        :param options: [ ( "<return_value>", "<display_value>"), ... ]
        :param value:
        :param title:
        :return: True on success, False otherwise
        """

        if name in self.widgets:
            self.logger.error("{} already defined".format(name))
            return False

        self.widgets[name] = {
            'obj': None,
            'value_field': 'value',
            'arg_name': '{}'.format(name),
            'value': value,
            'title': title,
            'options': options,
            'width': width,
            'size': size,
            "handler": self._select_handler
        }
        self._select_handler({}, self.widgets[name])
        self._set_all_callbacks()
        return True

    def _button_handler(self, args, b):
        """
        :param args: dict URL args
        :param b: button widget
        """
        if args.get('callerWidget', False):
            if args['callerWidget'] == b['name']:
                b['value'] = True
                args[b['name']] = True
            else:
                b['value'] = False
                args[b['name']] = False

        b["obj"] = Button(label=b["label"])

    def add_button(self, name, label="label", icon=None, width=None):

        if name in self.widgets:
            self.logger.error("{} already defined".format(name))
            return False

        self.widgets[name] = {
            'obj': None,
            'name': name,
            'value_field': None,
            'value': False,
            'arg_name': '{}'.format(name),
            'label': label,
            'width': width,
            "has_bokeh_callback": False,
            "handler": self._button_handler
        }
        self._button_handler({}, self.widgets[name])
        self._set_all_callbacks()
        return True

    def process_req(self, req):
        """ Updates the state of every widget based on the values of each widget in args
        - sets the callback for each widget
        :param args: dict of every widget value by name
        """
        if req.method == "POST": args = req.form.to_dict()
        else: args = {}
        self.logger.info(args)

        for key, widget in self.widgets.items():
            if widget["obj"] is not None and widget["handler"] is not None:
                widget["handler"](args, widget)

        self._set_all_callbacks()

        return args

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
        """ render the layout in the current dominate document
        :param d: dominate document
        :param layout: bokeh layout object
        :return: dominate document
        """
        _script, _div = components(layout)
        d.body += raw(_script)
        d.body += raw(_div)
        return d



