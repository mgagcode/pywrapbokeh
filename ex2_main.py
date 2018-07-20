#!/usr/bin/python
# -*- coding: utf-8 -*-

from flask import Flask
from flask_security import Security, login_required, SQLAlchemySessionUserDatastore
from database import db_session, init_db
from models import User, Role

app = Flask(__name__, static_url_path='/media')
app.config['SECRET_KEY'] = 'super-secret'

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db_session, User, Role)
security = Security(app, user_datastore)


# Create a user to test with
@app.before_first_request
def create_user():
    init_db()
    user_datastore.create_user(email='matt@nobien.net', password='password')
    db_session.commit()


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


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=6800, debug=False)

# consider this first graph example, https://bokeh.pydata.org/en/latest/docs/user_guide/interaction/callbacks.html

