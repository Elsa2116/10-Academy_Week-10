"""
app.py – Flask application entry point
Birhan Energies – Brent Oil Price Analysis API
"""

from flask import Flask
from flask_cors import CORS
from api.routes import api_bp


def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.route("/")
    def index():
        return {
            "service": "Birhan Energies – Brent Oil Analysis API",
            "version": "1.0.0",
            "docs": "/api/",
        }

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
