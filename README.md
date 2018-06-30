pywrapbokeh

A python class for wrapping bokeh widgets in a Flask app so that all callbacks can be in python rather than in javascript, because I just don't want to learn javascript.

Every bokeh widget callback is assigned a bit of (common) javascript that causes a web refresh with all the widget parameters in the URL. In this way the Flask route can scrape the USl and get all widget parameters and handle them in python.

LOOK Ma! No HTML!