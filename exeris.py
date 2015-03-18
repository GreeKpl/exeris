from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:root@localhost/exeris111"
db = SQLAlchemy(app)
db.create_all()

@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
