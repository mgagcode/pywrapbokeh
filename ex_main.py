#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask


app = Flask(__name__)

with app.app_context():
    from ex_utils import setup_logging
    setup_logging(log_file_name_prefix=__file__, addConsole=False)

    # pages
    from ex_index import ex_index
    from ex_a import ex_a
    from ex_b import ex_b

    app.register_blueprint(ex_index)
    app.register_blueprint(ex_a)
    app.register_blueprint(ex_b)

app.run(host="0.0.0.0", port=6800, debug=False)

# consider this first graph example, https://bokeh.pydata.org/en/latest/docs/user_guide/interaction/callbacks.html

