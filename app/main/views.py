from datetime import datetime

from flask import flash, redirect, render_template, url_for, current_app, request

from .forms import Login, SearchForm, TakeForm, LendForm
from . import main
from .. import db
from ..models import User, Item, Record

from sqlalchemy import or_, and_
from flask_login import login_user, login_required, logout_user, current_user


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
    )

    keyword = request.form.get("keyword")
    if keyword:
        pagination = (
            Item.query.filter(
                and_(
                    or_(Item.stock > 0, Item.in_store),
                    or_(
                        Item.spec.like("%" + keyword + "%"),
                        Item.pn.like("%" + keyword + "%"),
                    ),
                )
            )
            .order_by(Item.in_store.desc(), (Item.warn_stock - Item.stock).desc())
            .paginate(
                page,
                per_page=current_app.config["FLASKY_POSTS_PER_PAGE"],
                error_out=False,
            )
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
        "record.html", form=form, records=records, pagination=pagination
    )


@main.route("/lend/<pn>", methods=["GET", "POST"])
def lend(pn):
    form = LendForm()
    item = Item.query.filter_by(pn=pn).first()

    print(request.form.to_dict())
    if request.method == "POST":
        data = request.form.to_dict()
        r = Record(
            pn=item.pn,
            spec=item.spec,
            size=item.size,
            qty=data["qty"],
            customer=data["customer"],
            lend_pic=data["lend_pic"],
            ap_pic=current_user.username,
            returned=False,
        )
        db.session.add(r)
        db.session.commit()
        return redirect(url_for(".record"))
    return render_template("lend.html", form=form, item=item)


@main.route("/return/<id>")
def Return(id):
    r = Record.query.filter_by(id=id).first()
    r.returned = True
    db.session.add(r)
    i = Item.query.filter_by(pn=r.pn).first()
    i.stock -= r.qty
    db.session.add(i)
    db.session.commit()
    return redirect(url_for(".record"))
