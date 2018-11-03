from flask import render_template, current_app
from . import manage
from sqlalchemy.exc import IntegrityError
import traceback


@manage.errorhandler(ValueError)
def special_exception_handler(error):
    current_app.logger.exception(error)
    msg = traceback.format_exc()
    return render_template('500.html',error=msg), 500
	
@manage.errorhandler(IntegrityError)
def special_exception_handler(error):
    current_app.logger.exception(error)
    msg = traceback.format_exc()
    return render_template('500.html',error=msg+'检查一下是不是有重复的PN没合并'), 500
    
@manage.app_errorhandler(BaseException)
def other_error(e):
    msg = traceback.format_exc()+'No special errorhandler matches, this was handled by other_error'
    return render_template('500.html',error=msg), 500