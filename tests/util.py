from exeris.core.main import create_app, db

__author__ = 'alek'


def set_up_app_with_database(self):
    global db
    app = create_app(config_object_module="config.TestingConfig", database=db)
    with app.app_context():
        db.create_all()

    return app


def tear_down_rollback(self):
    db.session.rollback()
