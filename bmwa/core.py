from flask import Flask
from flask.ext.babel import Babel
from . import config

app = Flask(__name__.split('.')[0])
app.config.from_object(config.__name__)
app.config.from_envvar('BMWA_SETTINGS', silent=True)
babel = Babel(app)
