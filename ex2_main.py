#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask


#app = Flask(__name__, static_folder='./media')
app = Flask(__name__, static_url_path='/media')

with app.app_context():
    from ex_utils import setup_logging
    setup_logging(log_file_name_prefix=__file__, addConsole=False)

    # pages
    from ex2_index import ex2_index
    from ex2_login import ex2_login
    from ex2_login_signup import ex2_login_signup

    app.register_blueprint(ex2_index)
    app.register_blueprint(ex2_login)
    app.register_blueprint(ex2_login_signup)

app.run(host="0.0.0.0", port=6800, debug=False)

# consider this first graph example, https://bokeh.pydata.org/en/latest/docs/user_guide/interaction/callbacks.html

