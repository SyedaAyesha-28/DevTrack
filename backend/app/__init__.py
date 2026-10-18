
import os
from flask_cors import CORS
from dotenv import load_dotenv
from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

load_dotenv()

# Initialize extensions before importing models.
db = SQLAlchemy()
migrate = Migrate()


def create_app(test_config=None):
    app = Flask(__name__)
    CORS(
    app,
    resources={r"/api/*": {"origins": "http://localhost:5173"}},
    )
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY", "dev-only-change-this"
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL", "sqlite:///devtrack.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    if test_config:
        app.config.update(test_config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models after db has been initialized.
    from app.models import Issue

    # Register API routes.
    from app.routes.health import health_bp
    app.register_blueprint(health_bp, url_prefix="/api")

    from app.routes.issues import issues_bp
    app.register_blueprint(issues_bp, url_prefix="/api")
    return app
