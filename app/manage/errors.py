from flask import render_template, current_app
from . import manage
from sqlite3 import IntegrityError
import traceback


@manage.errorhandler(ValueError)
def special_exception_handler(e):
    current_app.logger.exception(e)
    msg = traceback.format_exc()
    return msg, 500
	
@manage.errorhandler(IntegrityError)
def special_exception_handler(e):
    current_app.logger.exception(e)
    msg = traceback.format_exc()
    return msg+'检查一下是不是有重复的PN没合并', 500
