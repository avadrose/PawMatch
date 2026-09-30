import os

from dotenv import load_dotenv
from flask import Flask

from models import db

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

db.init_app(app)


@app.route("/")
def homepage():
    return "<h1>PawMatch</h1><p>Flask is running!</p>"


if __name__ == "__main__":
    app.run(debug=True)