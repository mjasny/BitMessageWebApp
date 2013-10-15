from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import Required, ValidationError


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
    to_address = SelectField('To')
    from_address = SelectField('From')
    subject = StringField('Subject', validators=[Required()])
    message = TextAreaField('Message', validators=[Required()])


class AddressbookForm(Form):
    new_address = StringField('Address', validators=[Required(),
                                            validate_bitmessage_address])
    new_address_label = StringField('AddressLabel', validators=[Required()])
