from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,IntegerField, BooleanField
from wtforms.validators import Required

class Login(FlaskForm):
    username = StringField('Username', validators=[Required()])
    password = PasswordField('Password',validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    keyword = StringField('Keyword')
    submit = SubmitField('Submit')

class TakeForm(FlaskForm):
    nums = IntegerField('Keyword')
    submit = SubmitField('Submit')
