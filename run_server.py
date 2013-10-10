#!/usr/bin/env python3

from bmwa import app

app.run(host=app.config['APP_HOST'], port=app.config['APP_PORT'])
