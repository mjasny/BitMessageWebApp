from flask.ext.wtf import Form
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import Required


class SendForm(Form):
    to_address = SelectField('To')
    from_address = SelectField('From')
    subject = StringField('Subject', validators=[Required()])
    message = TextAreaField('Message', validators=[Required()])
