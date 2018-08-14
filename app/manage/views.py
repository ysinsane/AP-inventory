from datetime import datetime

import csv
import os

from config import basedir

from flask import (
    flash,
    redirect,
    render_template,
    url_for,
    current_app,
    request,
    abort,
    send_file,
)

from .forms import SignIn, ItemForm, SearchForm, BuyForm, ExportForm


from . import manage
from .. import db
from ..models import User, Item, Record

from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from flask_login import login_required, current_user


@manage.route("/mark", methods=["GET", "POST"])
@login_required
def mark():
    if current_user.role_id != 2:
        abort(403)
    keyword = request.args.get("keyword", "")
    page = request.args.get("page", 1, type=int)
    pagination = (
        Item.query.filter(
            or_(
                Item.pn.like("%" + keyword + "%"),
                Item.spec.like("%" + keyword + "%"),
                Item.size.like("%" + keyword + "%"),
            )
        )
        .order_by((Item.warn_stock - Item.stock).desc())
        .paginate(
            page, per_page=current_app.config["FLASKY_POSTS_PER_PAGE"], error_out=False
        )
    )
    # print(request.form.to_dict())
    if request.method == "POST":
        if request.form.get("search") is not None:
            keyword = request.form.get("keyword")
            print(keyword)
            pagination = (
                Item.query.filter(
                    or_(
                        Item.pn.like("%" + keyword + "%"),
                        Item.spec.like("%" + keyword + "%"),
                        Item.size.like("%" + keyword + "%"),
                    )
                )
                .order_by((Item.warn_stock - Item.stock).desc())
                .paginate(
                    page,
                    per_page=current_app.config["FLASKY_POSTS_PER_PAGE"],
                    error_out=False,
                )
            )
        if request.form.get("modify") is not None:
            print("modify")
            form_data = request.form.to_dict()
            for v in form_data.keys():
                if v.endswith("-check"):
                    print(v)
                    pn = v[:-6]
                    item = Item.query.filter_by(pn=pn).first()
                    item.in_store = not item.in_store
                    db.session.add(item)
                    db.session.commit()
                    print(item.spec + ":")
                    print(item.in_store)
                if v.endswith("-text"):
                    print(bool(form_data[v]))
                    pn = v[:-5]
                    item = Item.query.filter_by(pn=pn).first()
                    warn_stock = form_data[v]
                    if warn_stock:
                        item.warn_stock = int(form_data[v])
                        db.session.add(item)
                        db.session.commit()
                        print(pn + " now is:" + form_data[v])
    args = {"keyword": keyword}
    items = pagination.items
    print(len(items))
    return render_template(
        "manage/mark.html", pagination=pagination, items=items, args=args
    )


@manage.route("/_import", methods=["GET", "POST"])
@login_required
def _import():
    fails = []
    if current_user.role_id != 2:
        abort(403)
    if request.method == "POST":
        print("post")
        if request.files["file"]:
            print("get file")
            file_name = os.path.join(basedir, "temp", request.files["file"].filename)
            request.files["file"].save(file_name)
            Item.query.delete()
            with open(file_name, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = [row for row in reader]
                try:
                    for row in rows:
                        if (
                            row[0] != ""
                            and row[0] != "pn"
                            and row[1] != ""
                            and row[2] != ""
                            and row[3] != ""
                        ):
                            warn_stock = 9999
                            shelf_life = None
                            in_store = False
                            if len(row) > 4:
                                in_store = row[4] == "TRUE"
                            if len(row) > 5:
                                warn_stock = int(row[5])
                            if len(row) > 6:
                                shelf_life = datetime.strptime(row[6], "%Y-%m-%d")
                            item = Item(
                                pn=row[0],
                                spec=row[1],
                                size=row[2],
                                stock=int(row[3]),
                                in_store=in_store,
                                warn_stock=warn_stock,
                                shelf_life=shelf_life,
                            )
                            db.session.add(item)
                            try:
                                db.session.commit()
                            except IntegrityError:
                                fails += row
                                db.session.rollback()
                except IndexError:
                    flash("数据残缺！第1，2，3，4列必须有数据，且分别应该是pn，spec，size，stock")
                flash(
                    "Inventory has been reset,if no error showed on this page,it success!"
                )
        else:
            flash("No file!")
    return render_template("/manage/import_items.html", fails=fails)


@manage.route("/export", methods=["GET", "POST"])
@login_required
def export():
    form = ExportForm()
    if form.validate_on_submit():
        with open(
            os.path.join(basedir, "temp", "temp.csv"), "w", encoding="UTF-8", newline=""
        ) as csvfile:
            csvwriter = csv.writer(
                csvfile, delimiter=",", quotechar="|", quoting=csv.QUOTE_MINIMAL
            )
            if form.table.data == "Item":
                items = Item.query.all()
                csvwriter.writerow(
                    [
                        "pn",
                        "spec",
                        "size",
                        "stock",
                        "in_store",
                        "warn_stock",
                        "shelf_life",
                    ]
                )  # 7 col
                for i in items:
                    csvwriter.writerow(
                        [i.pn]
                        + [i.spec]
                        + [i.size]
                        + [i.stock]
                        + [i.in_store]
                        + [i.warn_stock]
                        + [i.shelf_life]
                    )
            if form.table.data == "Record":
                records = Record.query.all()
                csvwriter.writerow(
                    [
                        "pn",
                        "spec",
                        "size",
                        "qty",
                        "time",
                        "ap_pic",
                        "customer",
                        "lend_pic",
                        "returned",
                    ]
                )
                for r in records:
                    csvwriter.writerow(
                        [r.pn]
                        + [r.spec]
                        + [r.size]
                        + [r.qty]
                        + [r.time]
                        + [r.ap_pic]
                        + [r.customer]
                        + [r.lend_pic]
                        + [r.returned]
                    )
        return send_file(os.path.join(basedir, "temp", "temp.csv"), as_attachment=True)
    return render_template("/manage/export.html", form=form)


@manage.route("/add_account", methods=["GET", "POST"])
def add_account():
    if current_user.role_id != 2:
        abort(403)
    form = SignIn()
    print(request.form.to_dict())
    if form.validate_on_submit():
        role_id = 1
        if form.admin_or_not.data is True:
            role_id = 2
        u = User(
            username=form.username.data, password=form.password.data, role_id=role_id
        )
        db.session.add(u)
        db.session.commit()
        flash("成功添加用户：{0}".format(form.username.data))
    return render_template("/manage/add_account.html", form=form)


@manage.route("/index", methods=["GET", "POST"])
@login_required
def index():
    if current_user.role_id != 2:
        abort(403)
    form = SearchForm()
    page = request.args.get("page", 1, type=int)
    pagination = Item.query.order_by(
        Item.in_store.desc(), (Item.warn_stock - Item.stock).desc()
    ).paginate(
        page, per_page=current_app.config["FLASKY_POSTS_PER_PAGE"], error_out=False
    )

    keyword = request.form.get("keyword")
    if keyword:
        pagination = (
            Item.query.filter(
                or_(
                    Item.spec.like("%" + keyword + "%"),
                    Item.pn.like("%" + keyword + "%"),
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
        "/manage/index.html",
        pagination=pagination,
        form=form,
        items=items,
        keyword=keyword,
    )


@manage.route("/buy/<pn>", methods=["GET", "POST"])
@login_required
def buy(pn):
    if current_user.role_id != 2:
        abort(403)
    form = BuyForm()
    item = Item.query.filter_by(pn=pn).first()

    if form.validate_on_submit():
        item.stock += form.qty.data
        db.session.add(item)
        db.session.commit()

        r = Record(
            pn=item.pn,
            spec=item.spec,
            size=item.size,
            qty=form.qty.data,
            customer="入库",
            ap_pic=current_user.username,
            returned=False,
            time=datetime.utcnow(),
        )

        db.session.add(r)
        db.session.commit()
        return redirect(url_for("main.record"))
    return render_template("/manage/buy.html", form=form, item=item)


@manage.route("/account", methods=["GET", "POST"])
@login_required
def account():
    if current_user.role_id != 2:
        abort(403)
    users = User.query.all()
    return render_template("/manage/account.html", users=users)


@manage.route("/delete_user/<id>", methods=["GET"])
@login_required
def delete_user(id):
    if current_user.role_id != 2:
        abort(403)
    if int(id) != current_user.id:
        user = User.query.filter_by(id=id).first()
        db.session.delete(user)
        db.session.commit()
    else:
        flash("当前账户不能删除")
    return redirect(url_for(".account"))


@manage.route("/add", methods=["GET", "POST"])
@login_required
def add():
    form = ItemForm()
    items = Item.query.order_by(Item.id.desc()).limit(6)
    if form.validate_on_submit():
        shelf_life = datetime.strptime(form.shelf_life.data, "%Y-%m-%d")
        print(shelf_life)
        print(form.in_store.data)
        i = Item(
            pn=form.pn.data,
            spec=form.spec.data,
            size=form.size.data,
            stock=form.stock.data,
            warn_stock=form.warn_stock.data,
            in_store=form.in_store.data,
            shelf_life=shelf_life,
        )
        db.session.add(i)
        db.session.commit()
        items = Item.query.order_by(Item.id.desc()).limit(6)
    return render_template("/manage/add_item.html", form=form, items=items)


@manage.route("/delete_item/<id>", methods=["GET"])
@login_required
def delete_item(id):
    i = Item.query.get_or_404(id)
    db.session.delete(i)
    db.session.commit()
    return redirect(url_for(".index"))
