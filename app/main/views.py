from datetime import datetime

from flask import flash, redirect, render_template, session, url_for


from .forms import Login, SearchForm, TakeForm
from . import main
from .. import db
from ..models import User,Item


@main.route('/login', methods=['GET', 'POST'])
def login():
    form=Login()
    name='Stranger'
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
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
    items=None
    if form.validate_on_submit():
        items=Item.query.order_by((Item.warn_stock-Item.stock).desc()).all()
    return render_template('index.html',form=form,items=items)

@main.route('/item/<pn>', methods=['GET', 'POST'])
def item(pn):
    form=TakeForm()
    item=Item.query.filter_by(PN=pn).first()
    if form.validate_on_submit():
        item.stock-=int(form.num.data)
        db.session.add(item)
        db.session.commit()
        redirect(url_for('.taked'))
    return render_template('item.html',form=form,item=item)

@main.route('/taked', methods=['GET', 'POST'])
def taked():
    
    return "hello"