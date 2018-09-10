import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    DEBUG = True
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_USE_TLS = True
    FLASKY_MAIL_SUBJECT_PREFIX = '[Ap-inventory]'
    MAIL_DEFAULT_SENDER = '632249494@qq.com'
    MAIL_USERNAME = '632249494@qq.com'
    MAIL_PASSWORD = 'atjfvchrtvejbfdj'
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_SERVER = 'smtp.qq.com'
    AP_ADMIN = 'eason_yansheng@163.com'
    FLASKY_POSTS_PER_PAGE = 50
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        # 把错误通过电子邮件发送给管理员
        import logging
        from logging.handlers import SMTPHandler,StreamHandler
        
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
            mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.MAIL_DEFAULT_SENDER,
            toaddrs=[cls.AP_ADMIN],
            subject=cls.FLASKY_MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            mail_handler.setLevel(logging.DEBUG)
            mail_handler.setFormatter(formatter)
            app.logger.addHandler(mail_handler)
            file_handler = StreamHandler()
            file_handler.setLevel(logging.WARNING)
            app.logger.addHandler(file_handler)



config = {
'development': DevelopmentConfig,
'testing': TestingConfig,
'production': ProductionConfig,
'default': DevelopmentConfig
}