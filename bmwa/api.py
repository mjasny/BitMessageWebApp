
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


def _b64encode(s):
    """Helper function to encode base64 unicode."""
    return base64.b64encode(s.encode('utf-8')).decode('ascii')


def get_inbox_messages():
    """
    Returns a list of inbox messages in descending date order with strings
    not yet decoded.
    """
    proxy = _get_proxy()
    messages = json.loads(proxy.getAllInboxMessages())['inboxMessages']
    return list(reversed(messages))  # API returns in ascending date

def get_outbox_messages():
    """
    Returns a list of inbox messages in descending date order with strings
    not yet decoded.
    """
    proxy = _get_proxy()
    messages = json.loads(proxy.getAllSentMessages())['sentMessages']
    return list(reversed(messages))  # API returns in ascending date

def get_addressbook_addresses():
    """
    Returns a list of inbox messages in descending date order with strings
    not yet decoded.
    """
    proxy = _get_proxy()
    addresses = json.loads(proxy.listAddressBookEntries())['addresses']
    return list(reversed(addresses))  # API returns in ascending date

def _make_lookup(addresses):
    dct = {}
    for a in addresses:
        dct[a['address']] = _b64decode(a['label'])
    return dct


def get_address_dict():
    """Returns a lookup dictionary between BitMessage addresses and labels."""
    proxy = _get_proxy()
    addresses = json.loads(proxy.listAddressBookEntries())['addresses']
    return _make_lookup(addresses)


def get_identity_dict():
    """Returns a lookup dictionary between BitMessage addresses and labels."""
    proxy = _get_proxy()
    addresses = json.loads(proxy.listAddresses2())['addresses']
    return _make_lookup(addresses)


def decode_and_format_messages(messages):
    """Decodes a sequence of messages."""
    address_dict = get_address_dict()
    for m in messages:
        decode_and_format_message(m, address_dict)

def decode_and_format_outbox_messages(messages):
    """Decodes a sequence of messages."""
    address_dict = get_address_dict()
    for m in messages:
        decode_and_format_outbox_message(m, address_dict)

def decode_and_format_addresses(addresses):
    """Decodes a sequence of addresses."""
    address_dict = get_address_dict()
    for a in addresses:
        decode_and_format_addressbook_addresses(a, address_dict)


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

def decode_and_format_outbox_message(message, address_dict=None):
    """Decode text and assign address labels if found."""
    if address_dict is None:
        address_dict = get_address_dict()

    message['subject'] = _b64decode(message['subject'])
    message['message'] = _b64decode(message['message'])
    message['fromAddress'] = address_dict.get(
                            message['fromAddress'], message['fromAddress'])
    message['toAddress'] = address_dict.get(
                            message['toAddress'], message['toAddress'])
    message['lastActionTime'] = datetime.fromtimestamp(
        int(message['lastActionTime'])).strftime('%Y-%m-%d %H:%M:%S')
    message['status'] = address_dict.get(
                            message['status'], message['status'])

def decode_and_format_addressbook_addresses(address, address_dict=None):
    """Decode text and assign address labels if found."""
    if address_dict is None:
        address_dict = get_address_dict()

    #address['address'] = address_dict.get(address['address'], address['address'])
    address['label'] = _b64decode(address['label'])

def get_inbox_message_by_id(msgid):
    """Retrieves and decodes a message."""
    proxy = _get_proxy()
    message = json.loads(  # boolean marks message as read
        proxy.getInboxMessageByID(msgid, True))['inboxMessage'][0]
    decode_and_format_message(message)
    return message

def get_outbox_message_by_id(msgid):
    """Retrieves and decodes a message."""
    proxy = _get_proxy()
    message = json.loads(  # boolean marks message as read
        proxy.getSentMessageByID(msgid, True))['sentMessage'][0]
    decode_and_format_outbox_message(message)
    return message

def send_message(to_address, from_address, subject, message):
    proxy = _get_proxy()
    ackdata = proxy.sendMessage(to_address, from_address,
                _b64encode(subject), _b64encode(message))
    print(("ackdata: {}".format(ackdata)))
