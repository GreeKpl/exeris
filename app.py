from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from exeris.core.main import app, db, create_app


app = create_app()


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
