from datetime import datetime

from flask import flash, redirect, render_template, url_for,current_app, request


from .forms import Login, SearchForm, TakeForm
from . import main
from .. import db
from ..models import User, Item, Record
from sqlalchemy import or_


@main.route('/login', methods=['GET', 'POST'])
def login():
    form=Login()
    name='Stranger'
    if form.validate_on_submit():
        user = User.query.filter(username = form.username.data).first()
        if user != None:
            if user.verify_password(form.password.data):
                pass
            else:
                flash('Password is wrong!')
        else:
            flash('No such user!')
    return render_template('login.html',name="eason",form=form)

@main.route('/', methods=['GET', 'POST'])
def index():
    form = SearchForm()
    page = request.args.get('page',1,type=int)
    pagination = Item.query.order_by((Item.warn_stock-Item.stock).desc()).paginate(page,per_page=
    current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
    items=pagination.items
    if form.validate_on_submit():
        keyword=form.keyword.data
        items=Item.query.filter(or_(Item.spec.like("%"+keyword+"%"), Item.pn.like("%"+keyword+"%"))).order_by((Item.warn_stock-Item.stock).desc()).all()
    return render_template('index.html', pagination=pagination, form=form, items=items)

@main.route('/item/<pn>', methods=['GET', 'POST'])
def item(pn):
    form=TakeForm()
    item=Item.query.filter_by(pn=pn).first()
    if form.validate_on_submit():
        item.stock-=int(form.num.data)
        db.session.add(item)
        db.session.commit()
        redirect(url_for('.taked'))
    return render_template('item.html',form=form,item=item)

@main.route('/taked', methods=['GET', 'POST'])
def taked():
    form=SearchForm()
    page = request.args.get('page',1,type=int)
    pagination = Record.query.order_by(Record.time.desc()).paginate(page,per_page=
    current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
    records = pagination.items
    if form.validate_on_submit():
        pagination = Record.query.filter(or_(Record.user.username==
        form.username.data,Record.item.spec.like("%"+form.spec.data+"%"))).order_by(Record.time.desc()).paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False
        )
    return render_template('record.html', form=form, records=records,
    pagination=pagination)

@main.route('/lend', methods=['GET', 'POST'])
def take():
    form=SearchForm()

    