#!/usr/bin/env python3

from flask import Flask
from flask import render_template, request
import xmlrpc.client
import json
import base64

app = Flask(__name__)
app.config.from_object('config')


@app.route('/')
def index():
    data = 'Click on Inbox Show'
    return render_template("index.html", data = data)

@app.route('/inbox_show')
def index_show():
    api = xmlrpc.client.ServerProxy("http://matthias:password@192.168.178.5:8442/")
    inboxMessages = json.loads(api.getAllInboxMessages())
    messageid = None
    if 'messageid' in request.args:
        messageid = request.args.get('messageid')   

    if messageid is not None:   
        return base64.b64decode(inboxMessages['inboxMessages'][int(messageid)]['message'].encode('ascii')).decode('utf-8')

    data = 'Messages in inbox: ' + str(len(inboxMessages['inboxMessages']))
    for i in range(0,len(inboxMessages['inboxMessages'])):
        data+= '<br><a href=inbox_show?messageid='+str(i)+'>['+str(i)+'] '+base64.b64decode(inboxMessages['inboxMessages'][i]['subject'].encode('ascii')).decode('utf-8')+'</a>'
    return render_template("inbox_show.html", data = data)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=5000)

