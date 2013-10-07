#!/usr/bin/env python3

from flask import Flask, render_template, request
import xmlrpc.client
import json
import base64

app = Flask(__name__)
app.config.from_object('config')

CONN_STRING = "http://%s:%s@%s:%d" % (app.config['API_USER'],
    app.config['API_PASSWD'], app.config['API_HOST'], app.config['API_PORT'])


def _b64decode(s):
    """Helper function to decode base64 unicode."""
    return base64.b64decode(s.encode('ascii')).decode('utf-8')


@app.route('/')
def index():
    api = xmlrpc.client.ServerProxy(CONN_STRING)
    messages = json.loads(api.getAllInboxMessages())['inboxMessages']
    for m in messages:
        m['subject'] = _b64decode(m['subject'])
    return render_template("index.html", messages=messages)


@app.route('/view/<msgid>')
def view(msgid):
    api = xmlrpc.client.ServerProxy(CONN_STRING)
    message = json.loads(api.getInboxMessageByID(msgid))
    return render_template("view.html", data=message)



@app.route('/inbox_show')
def index_show():
    api = xmlrpc.client.ServerProxy(CONN_STRING)
    inboxMessages = json.loads(api.getAllInboxMessages())
    messageid = None
    if 'messageid' in request.args:
        messageid = request.args.get('messageid')

    if messageid is not None:
        return _b64decode(
            inboxMessages['inboxMessages'][int(messageid)]['message'])

    data = 'Messages in inbox: ' + str(len(inboxMessages['inboxMessages']))
    for i in range(0,len(inboxMessages['inboxMessages'])):
        data+= '<br><a href=inbox_show?messageid='+str(i)+'>['+str(i)+'] '+base64.b64decode(inboxMessages['inboxMessages'][i]['subject'].encode('ascii')).decode('utf-8')+'</a>'
    return render_template("inbox_show.html", data = data)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=5000)

