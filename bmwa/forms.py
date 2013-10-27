from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import Required, ValidationError
from flask.ext.babel import gettext


BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def validate_bitmessage_address(form, field):
    address = field.data

    if address.lower().startswith('bm-'):
        address = address[3:]

    length = len(address)
    if length < 28:
        raise ValidationError("Length of address seems too short.")
    elif length > 36:
        raise ValidationError("Length of address seems too long.")

    for c in address:
        if c not in BASE58_ALPHABET:
            raise ValidationError("Invalid character in address.")


class SendForm(Form):
    to_address = SelectField(gettext('To'))
    from_address = SelectField(gettext('From'))
    subject = StringField(gettext('Subject'), validators=[Required()])
    message = TextAreaField(gettext('Message'), validators=[Required()])


class AddressbookForm(Form):
    new_address = StringField(gettext('Address'), validators=[Required(),validate_bitmessage_address])
    new_address_label = StringField(gettext('AddressLabel'), validators=[Required()])


class Addressbook_editForm(Form):
    old_label = StringField(gettext('Old Label'), validators=[Required()])
    new_label = StringField(gettext('New Label'), validators=[Required()])
    old_address = StringField(gettext('Old Address'), validators=[Required()])
    new_address = StringField(gettext('New Address'), validators=[Required()])


class Addressbook_deleteForm(Form):
    label = StringField(gettext('Do you want to delete this Address?: '), validators=[Required()])
    address = StringField(validators=[Required()])


class ViewForm(Form):
    test=1

