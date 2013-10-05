from flask import Flask
from flask import render_template
import xmlrpc.client
import json
import base64

app = Flask(__name__)
app.config.from_object('config')


@app.route('/')
def index():
    api = xmlrpc.client.ServerProxy("http://matthias:password@192.168.178.5:8442/")
    inboxMessages = json.loads(api.getAllInboxMessages())

    data = 'Messages in inbox: ' + str(len(inboxMessages['inboxMessages']))
    for i in range(0,len(inboxMessages['inboxMessages'])):
        data+= ' ['+str(i)+'] '+base64.b64decode(inboxMessages['inboxMessages'][i]['message'].encode('ascii')).decode('utf-8')

    #data = base64.b64decode(inboxMessages['inboxMessages'][0]['message'].encode('ascii'))

    return render_template("index.html", title = 'BMWA-DEV', data = data)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0',port=5000)
    
