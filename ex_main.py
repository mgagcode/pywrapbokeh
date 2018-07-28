#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys
import logging
import logging.handlers as handlers
from flask import Flask


def setup_logging(log_file_name_prefix=__file__, path=".\log", level=logging.INFO):

    # FIXME: logs are coming out "twice", once with the format from flask, and again from
    #        the format from consoleHandler.  app.logger level and the console handler
    #        level seem to be linked
    app.logger.setLevel(level)

    log_file_name_prefix = os.path.basename(log_file_name_prefix)

    # Here we define our formatter
    FORMAT = "%(relativeCreated)6d %(threadName)15s %(filename)25s:%(lineno)4s - %(name)30s:%(funcName)20s() %(levelname)-5.5s : %(message)s"
    formatter = logging.Formatter(FORMAT)

    if not os.path.exists(path): os.makedirs(path)

    allLogHandler_filename = os.path.join(path, "".join([log_file_name_prefix, ".log"]))
    allLogHandler = handlers.RotatingFileHandler(allLogHandler_filename, maxBytes=1024 * 1024, backupCount=4)
    allLogHandler.setLevel(logging.INFO)
    allLogHandler.setFormatter(formatter)

    errorLogHandler_filename = os.path.join(path, "".join([log_file_name_prefix, "-error", ".log"]))
    errorLogHandler = handlers.RotatingFileHandler(errorLogHandler_filename, maxBytes=128 * 1024, backupCount=4)
    errorLogHandler.setLevel(logging.ERROR)
    errorLogHandler.setFormatter(formatter)

    consoleHandler = logging.StreamHandler(stream=sys.stdout)
    consoleHandler.setFormatter(formatter)
    consoleHandler.setLevel(level)

    app.logger.addHandler(allLogHandler)
    app.logger.addHandler(errorLogHandler)
    #app.logger.addHandler(consoleHandler)  # FIXME: reinstate when above fixme is fixed

    # this did not work :(
    # https://stackoverflow.com/questions/27775026/provide-extra-information-to-flasks-app-logger

    # this looks interesting
    # https://stackoverflow.com/questions/45775367/log-messages-not-printed-by-flask-in-my-custom-flask-extension


app = Flask(__name__)

with app.app_context():
    setup_logging(log_file_name_prefix=__file__)

    # import blueprint pages
    from ex_index import ex_index
    from ex_a import ex_a, ex_get_new_data
    from ex_b import ex_b

    app.register_blueprint(ex_index)
    app.register_blueprint(ex_a)
    app.register_blueprint(ex_get_new_data)
    app.register_blueprint(ex_b)

app.run(host="0.0.0.0", port=6800, debug=False)

