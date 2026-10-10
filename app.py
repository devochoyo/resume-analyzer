# Start here. This file creates the app, connects the database and
# registers the pages. Render runs it with:  gunicorn app:app
import os

from dotenv import load_dotenv
from flask import Flask

from extension import db
from route import main

load_dotenv()

app = Flask(__name__)

# ---- Settings ----
app.secret_key = os.getenv("SECRET")
if not app.secret_key:
    raise RuntimeError("SECRET is missing. Add it to your .env file or your Render environment.")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///resume.db"
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # uploads up to 5 MB
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# ---- Connect everything ----
db.init_app(app)
app.register_blueprint(main)

with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
