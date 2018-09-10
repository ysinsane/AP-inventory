from flask import render_template
from . import main
import traceback
from sqlalchemy.exc import InvalidRequestError

@main.app_errorhandler(404)
def page_not_found(e):
    msg = traceback.format_exc()+'404'
    return render_template('404.html',error=msg), 404

@main.app_errorhandler(500)
def internal_server_error(e):
    msg = traceback.format_exc()+'500'
    return render_template('500.html',error=msg), 500

@main.app_errorhandler(TypeError)
def type_error(e):
    msg = traceback.format_exc()+'Tips: 可能是数据类型不对，比如本来应该是数字的地方，填入了字母或其他字符'
    return render_template('500.html',error=msg), 500
    
@main.app_errorhandler(BaseException)
def other_error(e):
    msg = traceback.format_exc()+'No special errorhandler matches, this was handled by other_error'
    return render_template('500.html',error=msg), 500

@main.app_errorhandler(InvalidRequestError)
def sql_error(e):
    msg = traceback.format_exc()+'Tips: something wrong with SQLalchemy!'
    return render_template('500.html',error=msg), 500