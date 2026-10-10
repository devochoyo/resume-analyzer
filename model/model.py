# The database table. One row = one resume that was analysed.
import json
from datetime import datetime

from extension import db


class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    score = db.Column(db.Integer, nullable=False)
    field = db.Column(db.String(100), nullable=False)
    level = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # The full analysis is saved here as text, so the results page can show it.
    result_json = db.Column(db.Text, nullable=False)

    def result(self):
        return json.loads(self.result_json)
