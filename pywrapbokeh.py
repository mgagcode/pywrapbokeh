#!/usr/bin/python
# -*- coding: utf-8 -*-

from bokeh.embed import components
from bokeh.models.callbacks import CustomJS
from bokeh.models import Slider

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

    def add(self, name, widget):

        if isinstance(widget, (Slider, )):
            value_field = 'value'

        self.widgets[name] = {
            'obj': widget,
            'value': widget.value,
            'value_field': value_field,
        }

    def init(self):
        self._set_all_callbacks()

    def process_req(self, req):
        """ Updates the state of every widget based on the values of each widget in args
        - sets the callback for each widget
        :param args: dict of every widget value by name
        """
        if req.method == "POST": args = req.form.to_dict()
        else: args = {}
        self.logger.info(args)

        for w_name, w_value in args.items():
            if w_name == 'callerWidget': continue
            if isinstance(self.widgets[w_name], (Slider,)):
                self.set_value(w_name, int(w_value))
            else:
                self.logger.error("Unsupported widget class of name {}".format(w_name))

        return args

    def get(self, name):
        return self.widgets[name]["obj"]

    def get_value(self, name):
        if isinstance(self.widgets[name], (Slider,)):
            return self.widgets[name]["obj"].value
        else:
            self.logger.error("Unsupported widget class of name {}".format(name))

    def set_value(self, name, value):
        if isinstance(self.widgets[name], (Slider,)):
            if isinstance(value, str): value = int(value)
            self.widgets[name]["obj"].value = value
        else:
            self.logger.error("Unsupported widget class of name {}".format(name))

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



