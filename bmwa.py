#!/usr/bin/env python3

import base64
from datetime import datetime
import json
import xmlrpc.client

from flask import abort, Flask, make_response, render_template, redirect


app = Flask(__name__)
app.config.from_object('config')

CONN_STRING = "http://%s:%s@%s:%d" % (app.config['API_USER'],
    app.config['API_PASSWD'], app.config['API_HOST'], app.config['API_PORT'])
MSGS_PER_PAGE = 20


def _b64decode(s):
    """Helper function to decode base64 unicode."""
    return base64.b64decode(s.encode('ascii')).decode('utf-8')


@app.route('/')
def index():
    return redirect('/inbox')


@app.route('/inbox/', defaults={'page': 1})
@app.route('/inbox/page/<int:page>')
def inbox(page):
    """View for inbox messages."""
    api = xmlrpc.client.ServerProxy(CONN_STRING)
    messages = json.loads(api.getAllInboxMessages())['inboxMessages']
    messages = list(reversed(messages))  # API returns in ascending date
    mtotal = len(messages)

    page_count = 1 + mtotal // MSGS_PER_PAGE
    if page < 1 or page > page_count:
        abort(404)  # return not found for pages outside range

    mstart, mstop = (page - 1) * MSGS_PER_PAGE, page * MSGS_PER_PAGE
    mstop = min(mstop, mtotal)
    msgs_slice = messages[mstart: mstop]

    addresses = json.loads(api.listAddressBookEntries())['addresses']
    address_dict = {}  # create lookup for bitmessage address labels
    for a in addresses:
        address_dict[a['address']] = _b64decode(a['label'])

    for m in msgs_slice:  # decode text and assign address labels if found
        m['subject'] = _b64decode(m['subject'])
        m['fromAddress'] = address_dict.get(m['fromAddress'], m['fromAddress'])
        m['toAddress'] = address_dict.get(m['toAddress'], m['toAddress'])
        m['received'] = datetime.fromtimestamp(
            int(m['receivedTime'])).strftime('%Y-%m-%d %H:%M:%S')

    response = make_response(render_template("inbox.html",
            messages=msgs_slice, page=page, page_count=page_count,
            mstart=mstart, mstop=mstop, mtotal=mtotal))

    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = 0  # force reload so messages marked read
    response.headers['Pragma'] = 'no-cache'

    return response


@app.route('/view/<msgid>')
def view(msgid):
    """View to display an inbox message."""
    api = xmlrpc.client.ServerProxy(CONN_STRING)
    message = json.loads(  # boolean marks message as read
        api.getInboxMessageByID(msgid, True))['inboxMessage'][0]
    message['subject'] = _b64decode(message['subject'])
    message['message'] = _b64decode(message['message'])

    return render_template("view.html", message=message)


#@app.route('/inbox_show')
#def index_show():
    #api = xmlrpc.client.ServerProxy(CONN_STRING)
    #inboxMessages = json.loads(api.getAllInboxMessages())
    #messageid = None
    #if 'messageid' in request.args:
        #messageid = request.args.get('messageid')

    #if messageid is not None:
        #return _b64decode(
            #inboxMessages['inboxMessages'][int(messageid)]['message'])

    #data = 'Messages in inbox: ' + str(len(inboxMessages['inboxMessages']))
    #for i in range(0,len(inboxMessages['inboxMessages'])):
        #data+= ('<br><a href=inbox_show?messageid='+str(i)+'>['+str(i)+'] '+
        #base64.b64decode(inboxMessages['inboxMessages'][i]
        #['subject'].encode('ascii')).decode('utf-8')+'</a>')
    #return render_template("inbox_show.html", data = data)


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
