from datetime import datetime

from flask import flash, redirect, render_template, url_for,current_app, request


from .forms import Login, SearchForm, TakeForm, LendForm
from . import main
from .. import db
from ..models import User, Item, Record, Customer

from sqlalchemy import or_, and_
from flask_login import login_user,login_required,logout_user, current_user