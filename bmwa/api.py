
import base64
from datetime import datetime
import json
import threading
from xmlrpc.client import ServerProxy

from .core import app


_thread_local = threading.local()

CONN_STRING = "http://%s:%s@%s:%d" % (app.config['API_USER'],
    app.config['API_PASSWD'], app.config['API_HOST'], app.config['API_PORT'])


def _get_proxy():
    """Returns a ServerProxy object for the current thread."""
    proxy = getattr(_thread_local, 'server_proxy', None)
    if proxy is None:
        proxy = _thread_local.server_proxy = ServerProxy(CONN_STRING)
    return proxy


def _b64decode(s):
    """Helper function to decode base64 unicode."""
    return base64.b64decode(s.encode('ascii')).decode('utf-8')


def get_inbox_messages():
    """
    Returns a list of inbox messages in descending date order with strings
    not yet decoded.
    """
    proxy = _get_proxy()
    messages = json.loads(proxy.getAllInboxMessages())['inboxMessages']
    return list(reversed(messages))  # API returns in ascending date


def get_address_dict():
    """Returns a lookup dictionary between BitMessage addresses and labels."""
    proxy = _get_proxy()
    addresses = json.loads(proxy.listAddressBookEntries())['addresses']
    address_dict = {}
    for a in addresses:
        address_dict[a['address']] = _b64decode(a['label'])
    return address_dict


def decode_and_format_messages(messages):
    """Decodes a sequence of messages."""
    address_dict = get_address_dict()
    for m in messages:
        decode_and_format_message(m, address_dict)


def decode_and_format_message(message, address_dict=None):
    """Decode text and assign address labels if found."""
    if address_dict is None:
        address_dict = get_address_dict()

    message['subject'] = _b64decode(message['subject'])
    message['message'] = _b64decode(message['message'])
    message['fromAddress'] = address_dict.get(
                            message['fromAddress'], message['fromAddress'])
    message['toAddress'] = address_dict.get(
                            message['toAddress'], message['toAddress'])
    message['received'] = datetime.fromtimestamp(
        int(message['receivedTime'])).strftime('%Y-%m-%d %H:%M:%S')


def get_inbox_message_by_id(msgid):
    """Retrieves and decodes a message."""
    proxy = _get_proxy()
    message = json.loads(  # boolean marks message as read
        proxy.getInboxMessageByID(msgid, True))['inboxMessage'][0]
    decode_and_format_message(message)
    return message
