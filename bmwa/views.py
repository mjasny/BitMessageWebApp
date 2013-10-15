from flask import abort, make_response, render_template, redirect

from . import api
from .core import app
from .forms import SendForm, AddressbookForm, Addressbook_editForm, Addressbook_deleteForm
from .pagination import Pagination


MSGS_PER_PAGE = 20
ADDRS_PER_PAGE = 30


def _no_cache(response):
    """Mark a response to never be cached by browser and return it."""
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Expires'] = 0
    response.headers['Pragma'] = 'no-cache'

    return response


@app.route('/')
def index():
    return redirect('/inbox')


@app.route('/inbox/', defaults={'page': 1})
@app.route('/inbox/page/<int:page>')
def inbox(page):
    """View for inbox messages."""
    messages = api.get_inbox_messages()

    try:
        pagination = Pagination(page, messages, MSGS_PER_PAGE)
    except IndexError:
        abort(404)  # return not found for pages outside range

    msgs_slice = pagination.get_slice()
    api.decode_and_format_messages(msgs_slice)

    return _no_cache(make_response(render_template("inbox.html",
            messages=msgs_slice, pagination=pagination)))


@app.route('/outbox/', defaults={'page': 1})
@app.route('/outbox/page/<int:page>')
def outbox(page):
    messages = api.get_outbox_messages()

    try:
        pagination = Pagination(page, messages, MSGS_PER_PAGE)
    except IndexError:
        abort(404)  # return not found for pages outside range

    msgs_slice = pagination.get_slice()

    api.decode_and_format_outbox_messages(msgs_slice)

    return _no_cache(make_response(render_template("outbox.html",
            messages=msgs_slice, pagination=pagination)))


@app.route('/viewinbox/<msgid>')
def viewinbox(msgid):
    """View to display an inbox message."""
    message = api.get_inbox_message_by_id(msgid)

    return render_template("view.html", message=message)


@app.route('/viewoutbox/<msgid>')
def viewoutbox(msgid):
    """View to display an outbox message."""
    message = api.get_outbox_message_by_id(msgid)

    return render_template("view.html", message=message)


@app.route('/send', methods=['GET', 'POST'])
def send():
    form = SendForm()
    # Have to get addresses again because form validates against them.
    form.from_address.choices = [(k, v) for
                (k, v) in sorted(api.get_identity_dict().items())]
    form.to_address.choices = [(k, v) for
                (k, v) in sorted(api.get_address_dict().items())]

    if form.validate_on_submit():
        api.send_message(form.to_address.data, form.from_address.data,
                    form.subject.data, form.message.data)
        return redirect('/inbox')

    return render_template('send.html', form=form)


@app.route('/addressbook', defaults={'page': 1}, methods=['GET', 'POST'])
@app.route('/addressbook/page/<int:page>')
def addressbook(page):
    """View for Addressbook."""
    addresses = api.get_addressbook_addresses()

    form = AddressbookForm()

    if form.validate_on_submit():
        api.add_addressbookentry(form.new_address.data, form.new_address_label.data)
        return redirect('/addressbook')


    try:
        pagination = Pagination(page, addresses, ADDRS_PER_PAGE)
    except IndexError:
        abort(404)  # return not found for pages outside range

    addrs_slice = pagination.get_slice()


    return _no_cache(make_response(render_template("addressbook.html",
            addresses=addrs_slice, pagination=pagination, form=form)))


@app.route('/addressbook_edit/<address>', methods=['GET', 'POST'])
def addressbook_edit(address):
    form = Addressbook_editForm()
    
    addresses = api.get_addressbook_addresses()

    for a in addresses:
        if a['address'] == address:
            label = a['label']
            break   #if we have luck, we will save some time:)

    form.old_label.data = label
    form.new_label.data = label

    form.old_address.data = address
    form.new_address.data = address

    if form.validate_on_submit():
        form = Addressbook_editForm()
        api.edit_addressbookentry(address_old=address, address_new=form.new_address.data, label_new=form.new_label.data)
        return redirect('/addressbook')
    
    return render_template("addressbook_edit.html", form=form)


@app.route('/addressbook_remove/<address>', methods=['GET', 'POST'])
def addressbook_remove(address):
    form = Addressbook_deleteForm()
    
    addresses = api.get_addressbook_addresses()

    for a in addresses:
        if a['address'] == address:
            label = a['label']
            break   #if we have luck, we will save some time:)

    form.label.data = label
    form.address.data = address

    if form.validate_on_submit():
        api.delete_addressbookentry(address=address)
        return redirect('/addressbook')
    
    return render_template("addressbook_remove.html", form=form, label=label, address=address)
