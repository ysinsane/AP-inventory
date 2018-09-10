from datetime import datetime

from flask import flash, redirect, render_template, url_for, current_app, request,session

from .forms import Login, SearchForm, TakeForm, LendForm
from ..manage.forms import SignIn
from . import main
from .. import db, mail
from ..models import User, Item, Record
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired

from sqlalchemy import or_, and_
from flask_login import login_user, login_required, logout_user, current_user

from flask_mail import Message

@main.route("/login", methods=["GET", "POST"])
def login():
    form = Login()
    name = "Stranger"
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is not None:
            if user.verify_password(form.password.data):
                login_user(user, form.remember_me.data)
                return redirect(request.args.get("next") or url_for(".index"))
            else:
                flash("Password is wrong!")
        else:
            flash("No such user!")
    return render_template("login.html", name=name, form=form)


@main.route("/sign_in", methods=["GET", "POST"])
def sign_in():
    form = SignIn()
    if form.validate_on_submit() and form.email.data.endswith('@discosha.com'):
        userinfo=[form.username.data,
        form.password.data,
        form.email.data]
        s = Serializer(current_app.config['SECRET_KEY'], expires_in = 60)
        session['serializer']=True
        token = s.dumps(userinfo)
        msg = Message(subject='确认账户',
              recipients=["eason_yan@discosha.com"])
        msg.body = url_for('.confirm',token=token,_external=True)
        mail.send(msg)
        return '申请提交成功，我们给您发送了一封邮件来确认账户，请检查自己邮箱完成账号注册，有效期1小时。'
    return render_template('sign_in.html',form=form)
 
@main.route("/confirm/<token>", methods=["GET", "POST"])
def confirm(token):
    if session['serializer']:
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            datas = s.loads(token)
        except SignatureExpired:
            return '确认邮件已经过期，请重新注册，有效期1小时。'
        try:
            u=User(username=datas[0],password=datas[1],email=datas[2])
        except:
            return '怎么肥4，你确定username,password,email都好好填了吗!'
        try:
            db.session.add(u)
            db.session.commit()
        except:
            db.session.rollback()
        session['serializer']=False
        flash('该账户已经确认，请登录！')
        return redirect(url_for('.login'))
    flash('请勿重复提交，先注册再从邮件确认！')    
    return redirect(url_for('.sign_in'))

@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for(".login"))


@main.route("/", methods=["GET", "POST"])
@login_required
def index():
    form = SearchForm()
    page = request.args.get("page", 1, type=int)
    pagination = (
        Item.query.filter(or_(Item.stock > 0, Item.in_store))
        .order_by(Item.in_store.desc(), (Item.warn_stock - Item.stock).desc())
        .paginate(
            page, per_page=current_app.config["FLASKY_POSTS_PER_PAGE"], error_out=False
        )
    )#筛选库存大于0或者长期备库的品种，排序优先级为：长期备库〉库存跟报警阀值之差。然后分页

    keyword = request.form.get("keyword") or request.args.get('keyword','',type=str)
    if keyword:
        pagination = (
            Item.query.filter(
                and_(
                    or_(Item.stock > 0, Item.in_store),
                    or_(
                        Item.spec.like("%" + keyword + "%"),
                        Item.pn.like("%" + keyword + "%"),
                        Item.size.like("%" + keyword + "%")
                    ),#增加了搜索关键字作为筛选条件
                )
            )
            .order_by(Item.in_store.desc(), (Item.warn_stock - Item.stock).desc())#排序规则不变
            .paginate(
                page,
                per_page=current_app.config["FLASKY_POSTS_PER_PAGE"],
                error_out=False,
            )#分页方式不变
        )
    items = pagination.items
    return render_template(
        "index.html", pagination=pagination, form=form, items=items, keyword=keyword
    )


@main.route("/item/<pn>", methods=["GET", "POST"])
@login_required
def item(pn):
    form = TakeForm()
    item = Item.query.filter_by(pn=pn).first()

    if form.validate_on_submit():
        if item.stock < 1:
            flash("拿什么拿！没库存了！！")
        elif item.stock < form.qty.data:
            flash("库存没这么多给你拿啊！")
        else:
            item.stock -= form.qty.data
            db.session.add(item)
            db.session.commit()

            r = Record(
                pn=item.pn,
                spec=item.spec,
                size=item.size,
                qty=form.qty.data,
                customer=form.customer.data,
                ap_pic=current_user.username,
                returned=False,
                time=datetime.utcnow(),
            )

            db.session.add(r)
            db.session.commit()
            return redirect(url_for(".record"))
    return render_template("item.html", form=form, item=item)


@main.route("/record", methods=["GET", "POST"])
def record():
    form = SearchForm()
    page = request.args.get("page", 1, type=int)
    pagination = Record.query.order_by(Record.time.desc()).paginate(
        page, per_page=current_app.config["FLASKY_POSTS_PER_PAGE"], error_out=False
    )
    records = pagination.items
    now = datetime.utcnow()
    if request.method == "POST":
        keyword = request.form.to_dict()["keyword"]

        pagination = (
            Record.query.filter(
                or_(
                    Record.pn.like("%" + keyword + "%"),
                    Record.spec.like("%" + keyword + "%"),
                    Record.size.like("%" + keyword + "%"),
                    Record.ap_pic.like("%" + keyword + "%"),
                    Record.lend_pic.like("%" + keyword + "%"),
                    Record.customer.like("%" + keyword + "%"),
                )
            )
            .order_by(Record.time.desc())
            .paginate(
                page,
                per_page=current_app.config["FLASKY_POSTS_PER_PAGE"],
                error_out=False,
            )
        )

        records = pagination.items
    return render_template(
        "record.html", form=form, records=records, pagination=pagination,
        now = now
    )


@main.route("/lend/<pn>", methods=["GET", "POST"])
def lend(pn):
    form = LendForm()
    item = Item.query.filter_by(pn=pn).first()

    if request.method == "POST":
        if item.stock < 1:
            flash("拿什么拿！没库存了！！")
        elif item.stock < form.qty.data:
            flash("库存没这么多给你拿啊！")
        else:
            data = request.form.to_dict()
            r = Record(
                pn=item.pn,
                spec=item.spec,
                size=item.size,
                qty=data["qty"],
                customer=data["customer"],
                lend_pic=data["lend_pic"],
                time=datetime.utcnow(),
                days=data['days'],
                ap_pic=current_user.username,
                returned=False,
            )
            item.stock-=request.form.get('qty',type=int)
            db.session.add(r)
            db.session.add(item)
            db.session.commit()
            return redirect(url_for(".record"))
    return render_template("lend.html", form=form, item=item)


@main.route("/return/<id>")
def Return(id):
    r = Record.query.filter_by(id=id).first()
    r.returned = True
    db.session.add(r)
    i = Item.query.filter_by(pn=r.pn).first()
    i.stock += int(r.qty)
    db.session.add(i)
    db.session.commit()
    return redirect(url_for(".record"))
