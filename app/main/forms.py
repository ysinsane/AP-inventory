from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,IntegerField, BooleanField
from wtforms.validators import Required

class Login(FlaskForm):
    username = StringField('Username', validators=[Required()],
    render_kw={"placeholder":"中文",
    "style":"margin:0px 10px 0px 15px;display:inline;color:blue; text-align:center; width:20%"})
    password = PasswordField('Password',validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    keyword = StringField('',render_kw={"placeholder":"搜索关键字(PN或Spec)",
    "style":"margin:0px 10px 0px 15px;display:inline;color:blue; text-align:center; width:20%"})
    submit = SubmitField('Submit')

class TakeForm(FlaskForm):
    qty = IntegerField('Keyword',render_kw={"placeholder":123})
    submit_take = SubmitField('take')

class LendForm(FlaskForm):
    lent_pic=StringField('pic', validators=[Required()])
    qty = IntegerField('Keyword',render_kw={"placeholder":"数量","style": \
    "display:inline"})
    customer_name = StringField('customer_name', validators=[Required()],
    render_kw={"placeholder":"客户名","style":"margin:0px 10px 0px 10px; \
    display:inline;text-align:center"})
    lend_pic = StringField('lend_pic', validators=[Required()], \
    render_kw={"placeholder":"借出PIC","style":"margin:0px 10px 0px 10px; \
    display:inline;text-align:center"})
    submit_take = SubmitField('lend')
    
    