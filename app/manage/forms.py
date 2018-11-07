from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    BooleanField,
    PasswordField,
    IntegerField,
    RadioField,
)
from wtforms.validators import Required, Email, Length, EqualTo, Regexp, NumberRange


class SignIn(FlaskForm):#register a new account
    email = StringField("Email", validators=[Email()])
    password = PasswordField(
        "Password",
        validators=[Required(), EqualTo("password2", message="Passwords must match.")],
    )
    password2 = PasswordField("Confirm password", validators=[Required()])
    role = RadioField('Role', choices=[('Checker', 'Primary'), ('User', 'AP member'), \
    ('Borrower', 'AP borrower'),('Asist','Admin')],validators=[Required()])
    submit = SubmitField("注册")


class SearchForm(FlaskForm):
    keyword = StringField(
        "",
        render_kw={
            "placeholder": "搜索关键字(PN或Spec)",
            "style": "margin:0px 10px 0px 15px; \
                                         display:inline;color:blue; text-align:center; width:20%",
        },
    )
    submit = SubmitField("提交")


class BuyForm(FlaskForm):
    qty = IntegerField(
        "入库数量",
        validators=[NumberRange(min=1, max=100, message="Only accept number 1~100")],
    )
    submit = SubmitField("提交")


class ItemForm(FlaskForm):
    pn = StringField("PN", validators=[Required()])
    spec = StringField("Spec", validators=[Required()])
    size = StringField("Size", validators=[Required()])
    stock = IntegerField(
        "数量",
        validators=[NumberRange(min=1, max=100, message="Only accept number 1~100")],
    )
    warn_stock = IntegerField(
        "报警阀值", validators=[NumberRange(min=1, message="must >0")]
    )
    in_store = BooleanField("是否常备")
    shelf_life = StringField(
        "输入日期格式例如2010-10-10",
        validators=[
            Required(),
            Regexp(
                """((^((1[8-9]\d{2})|([2-9]\d{3}))([-\/\._])(10|12|0?[13578])([-\/\._])(3[01]|[12][0-9]|0?[1-9])$)|(^((1[8-9]\d{2})|([2-9]\d{3}))([-\/\.
                _])(11|0?[469])([-\/\._])(30|[12][0-9]|0?[1-9])$)|(^((1[8-9]\d{2})|([2-9]\d{3}))([-\/\._])(0?2)([-\/\._])(2[0-8]|1[0-9]|0?[1-9])$)|(^([2
                468][048]00)([-\/\._])(0?2)([-\/\._])(29)$)|(^([3579][26]00)([-\/\._])(0?2)([-\/\._])(29)$)|(^([1][89][0][48])([-\/\._])(0?2)([-\/\._])(
                29)$)|(^([2-9][0-9][0][48])([-\/\._])(0?2)([-\/\._])(29)$)|(^([1][89][2468][048])([-\/\._])(0?2)([-\/\._])(29)$)|(^([2-9][0-9][2468]
                [048])([-\/\._])(0?2)([-\/\._])(29)$)|(^([1][89][13579][26])([-\/\._])(0?2)([-\/\._])(29)$)|(^([2-9][0-9][13579][26])([-\/\._])(0?2)([-\
                /\._])(29)$))""",
                0,
                message="您输入的日期应该是错误或不符合格式要求的！",
            ),
        ],
    )
    submit = SubmitField("提交")


class ExportForm(FlaskForm):
    table = RadioField(
        "请选择要导出的数据表",
        validators=[Required()],
        choices=[("Item", "库存表"), ("Record", "库存操作记录表")],
    )
    submit = SubmitField("导出")
