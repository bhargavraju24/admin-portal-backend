from flask import Flask
from config import Config
from models import db
from routes import register_routes
import os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

register_routes(app)



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))