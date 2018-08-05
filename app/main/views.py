from datetime import datetime

from flask import flash, redirect, render_template, url_for,current_app, request


from .forms import Login, SearchForm, TakeForm, LendForm
from . import main
from .. import db
from ..models import User, Item, Record, Customer

from sqlalchemy import or_, and_
from flask_login import login_user,login_required,logout_user, current_user

@main.route('/login', methods=['GET', 'POST'])
def login():    
    form=Login()
    name='Stranger'
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user != None:
            if user.verify_password(form.password.data):
                login_user(user, form.remember_me.data)
                return redirect(request.args.get('next') or url_for('.index'))
            else:
                flash('Password is wrong!')
        else:
            flash('No such user!')
    return render_template('login.html',name="eason",form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('.index'))


@main.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = SearchForm()
    page = request.args.get('page',1,type=int)
    pagination = Item.query.order_by((Item.warn_stock-Item.stock).desc()).paginate(page,
    per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
    items=pagination.items
    keyword = request.form.get('keyword')
    if keyword:
        items=Item.query.filter(or_(Item.spec.like("%"+keyword+"%"), 
        Item.pn.like("%"+keyword+"%"))).order_by((Item.warn_stock-Item.stock).desc()).all()
    return render_template('index.html', pagination=pagination, form=form, items=items)


@main.route('/item/<pn>', methods=['GET', 'POST'])
@login_required
def item(pn):
    form=TakeForm()
    item=Item.query.filter_by(pn=pn).first()
    if form.submit_take.data and form.validate_on_submit():
        item.stock-=int(form.qty.data)
        db.session.add(item)
        db.session.commit()
        
        r=Record(qty=form.qty.data, item=item, user=current_user)
        db.session.add(r)
        db.session.commit()
        return redirect(url_for('.record'))
    return render_template('item.html',form=form,item=item)

@main.route('/record', methods=['GET', 'POST'])
def record():
    form=SearchForm()
    page = request.args.get('page',1,type=int)
    pagination = Record.query.order_by(Record.time.desc()).paginate(page,per_page=
    current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)
    records = pagination.items
    if request.method=='POST':
        keyword=request.form.to_dict()['keyword']

        pagination=Record.query.filter(and_(Record.item_id==Item.id,
        or_(Item.pn.like('%'+keyword+'%'),
        Item.spec.like('%'+keyword+'%'),
        Item.size.like('%'+keyword+'%'),
        Record.lend_pic.like('%'+keyword+'%')
        ))).order_by(Record.time.desc()). \
        paginate(page,per_page=
        current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False)

        records=pagination.items
    return render_template('record.html', form=form, records=records,
    pagination=pagination)

@main.route('/lend/<pn>', methods=['GET', 'POST'])
def lend(pn):
    form=LendForm()
    item=Item.query.filter_by(pn=pn).first()

    print(request.form.to_dict())
    if request.method=='POST':
        data=request.form.to_dict()
        c=Customer.query.filter_by(short_name=data['customer_name']).first()
        if not c:
            c=Customer(short_name=data['customer_name'])
            db.session.add(c)
            db.session.commit()
        r=Record(item=item,qty=data['qty'],customer=c,lend_pic=data['lend_pic']
        ,user=current_user,returned=False)
        db.session.add(r)
        db.session.commit()
        return redirect(url_for('.record'))
    return render_template('lend.html',form=form,item=item)
    