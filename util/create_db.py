from exeris.app import db, create_app


from exeris.config import Config


def create_db(db_uri_base=Config.SQLALCHEMY_DATABASE_URI_BASE, db_name=Config.SQLALCHEMY_DATABASE_NAME):
    app = create_app()
    db.init_app(app)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri_base + db_name

    with app.app_context():
        db.create_all()

if __name__ == "__main__":
    create_db()