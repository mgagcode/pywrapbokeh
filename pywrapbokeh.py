#!/usr/bin/python
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from bokeh.embed import components
from bokeh.models.callbacks import CustomJS
from bokeh.models import Slider
from bokeh.models.widgets.inputs import DatePicker, MultiSelect, TextInput, Select
from bokeh.models.widgets.buttons import Button, Toggle, Dropdown

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
                _parms_all += """'{name}':{name}.{value},""".format(name=w_name, value=w_params["value_field"])
                _args_all[w_name] = w_params["obj"]
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

    def _set_slider(self, slider, name, value, args):
        """ Slider, value is a string of an integer, set int
        :param name:
        :param value:
        """
        if value == 'NaN':
            _value = slider.value
        if isinstance(value, str):
            _value = float(value) if "." in value else int(value)
        slider.value = _value
        return args

    def _set_datep(self, datep, name, value, args):
        # the datepicker will return an epoch if it wasn't the callback trigger
        # and it returns a 'Mon Jun 18 2018' format if it was the trigger, handle both...
        # And note there is a one day off bug that is also handled.
        if value.split(".")[0].isdigit():  # epoch
            date = datetime.fromtimestamp(int(value.split(".")[0]) / 1000)
            # TODO: set hours and minutes to 0:0
            args[name] = date
        else:  # string date 'Mon Jun 18 2018'
            date = datetime.strptime(value, "%a %b %d %Y")
            args[name] = date
            date += timedelta(days=1)  # this fixes a bug where the date picked is one day behind the user selection

        datep.value = date
        self.widgets[name]["value"] = date
        return args

    def _set_multisel(self, multisel, name, value, args):
        cache = multisel.value

        if value in cache: cache.remove(value)
        else: cache.append(value)

        args[name] = cache
        self.widgets[name]["value"] = cache
        multisel.value = cache
        return args

    def _set_button(self, b, name, value, args):
        """ Button handler
        - Button doesn't have an value attribute, but we create one.
        - args["button_name"] is set to True if the user pressed the button
        :param b:
        :param name:
        :param value:
        :param args:
        :return: args
        """
        value = False
        if args.get('callerWidget', False):
            if args['callerWidget'] == name:
                value = True

        self.widgets[name]["value"] = value
        args[name] = value
        return args

    def _set_toggle(self, toggle, name, value, args):
        value = False
        if args.get('callerWidget', False):
            if args['callerWidget'] == name:
                if not self.widgets[name]["value"]:
                    value = True

        toggle.active = value
        self.widgets[name]["value"] = value
        args[name] = value
        return args

    def _set_dropdown(self, dropdown, name, value, args):
        dropdown.value = value
        self.widgets[name]["value"] = value
        return args

    def _set_select(self, sel, name, value, args):
        self.widgets[name]["value"] = value
        sel.value = value
        return args

    def add(self, name, widget):

        if isinstance(widget, (Slider, )):
            value_field = 'value'
            setter = self._set_slider
            value = widget.value
        elif isinstance(widget, (DatePicker, )):
            value_field = 'value'
            setter = self._set_datep
            value = widget.value
        elif isinstance(widget, (MultiSelect, )):
            value_field = 'value'
            setter = self._set_multisel
            value = widget.value
        elif isinstance(widget, (Button, )):
            value_field = None
            setter = self._set_button
            value = None
        elif isinstance(widget, (Toggle, )):
            value_field = "active"
            setter = self._set_toggle
            value = widget.active
        elif isinstance(widget, (Dropdown, )):
            value_field = 'value'
            setter = self._set_dropdown
            value = widget.value
        elif isinstance(widget, (Select, )):
            value_field = 'value'
            setter = self._set_select
            value = widget.value
        else:
            self.logger.error("4Unsupported widget class of name {}".format(name))
            return False

        self.widgets[name] = {
            'obj': widget,
            'value': value,
            'value_field': value_field,
            'setter': setter,
        }
        return True

    def process_req(self, req):
        """ Updates the state of every widget based on the values of each widget in args
        - sets the callback for each widget
        :param args: dict of every widget value by name
        """
        if req.method == "POST": args = req.form.to_dict()
        else: args = {}
        self.logger.info("--> {}".format(args))

        w_name = args.get('callerWidget', None)
        if w_name:
            w_value = args.get(w_name, None)
            w = self.widgets[w_name]
            args = w["setter"](w["obj"], w_name, w_value, args)

        self.logger.info("<-- {}".format(args))
        return args

    def init(self):
        self._set_all_callbacks()

    def get(self, name):
        return self.widgets[name]["obj"]

    def get_value(self, name):
        if isinstance(self.widgets[name], (Slider, DatePicker, MultiSelect, Dropdown, Select, )):
            return self.widgets[name]["obj"].value
        elif isinstance(self.widgets[name], (Button, )):
            # use cached value
            return self.widgets[name]["value"]
        elif isinstance(self.widgets[name], (Toggle, )):
            return self.widgets[name]["obj"].active
        else:
            self.logger.error("2Unsupported widget class of name {}".format(name))

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



