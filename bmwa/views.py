from flask import abort, make_response, render_template, redirect

from . import api
from .core import app


MSGS_PER_PAGE = 20


@app.route('/')
def index():
    return redirect('/inbox')


@app.route('/inbox/', defaults={'page': 1})
@app.route('/inbox/page/<int:page>')
def inbox(page):
    """View for inbox messages."""
    messages = api.get_inbox_messages()
    mtotal = len(messages)

    page_count = 1 + mtotal // MSGS_PER_PAGE
    if page < 1 or page > page_count:
        abort(404)  # return not found for pages outside range

    mstart, mstop = (page - 1) * MSGS_PER_PAGE, page * MSGS_PER_PAGE
    mstop = min(mstop, mtotal)
    msgs_slice = messages[mstart: mstop]

    api.decode_and_format_messages(msgs_slice)

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
    message = api.get_inbox_message_by_id(msgid)

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
