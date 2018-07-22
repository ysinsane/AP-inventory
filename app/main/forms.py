from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,IntegerField
from wtforms.validators import Required

class Login(FlaskForm):
    username = StringField('Username', validators=[Required()])
    password = PasswordField('Password',validators=[Required()])
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    keyword = StringField('Keyword')
    submit = SubmitField('Submit')

class TakeForm(FlaskForm):
    nums = IntegerField('Keyword')
    submit = SubmitField('Submit')
