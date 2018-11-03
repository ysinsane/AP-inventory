from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField,IntegerField, BooleanField
from wtforms.validators import Required,NumberRange,EqualTo

class Login(FlaskForm):
    username = StringField('Username', validators=[Required()])
    password = PasswordField('Password',validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Login')

class SearchForm(FlaskForm):
    keyword = StringField('',render_kw={"placeholder":"搜索关键字(PN,Spec,size)",
    "style":"margin:0px 10px 0px 15px;display:inline;color:blue; text-align:center; width:20%"})
    submit = SubmitField('Submit')

class TakeForm(FlaskForm):
    qty = IntegerField("取用数量",
    validators=[NumberRange(min=1,max=100,message='Only accept number 1~100')])
    customer = StringField('Customer name',validators=[Required()])
    submit = SubmitField('拿走')

class LendForm(FlaskForm):
    lent_pic=StringField('pic', validators=[Required()])
    qty = IntegerField('Keyword',render_kw={"placeholder":"数量","style": \
    "display:inline"})
    customer = StringField('customer', validators=[Required()],
    render_kw={"placeholder":"客户名","style": \
    "display:inline;text-align:center"})
    lend_pic = StringField('lend_pic', validators=[Required()], \
    render_kw={"placeholder":"借出PIC","style": \
    "display:inline;text-align:center"})
    days = IntegerField('days',validators=[Required()], \
    render_kw={"placeholder":"借出天数","style":" \
    display:inline;text-align:center"})
    submit_take = SubmitField('lend')
    
class ProfileForm(FlaskForm):
    password = PasswordField(
        "New password",
        validators=[Required(), EqualTo("password2", message="Passwords must match.")],
    )
    password2 = PasswordField("Confirm password", validators=[Required()])  
    submit = SubmitField('修改')