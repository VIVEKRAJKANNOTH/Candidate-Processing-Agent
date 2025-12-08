"""
Flask Backend API for TraqCheck CandidateVerify

Main application file that registers blueprints and configures the app.
All routes are organized in the routes/ directory.
"""
from flask import Flask
from flask_cors import CORS
from flasgger import Swagger
import os

# Create Flask app
app = Flask(__name__)
CORS(app)

# Swagger configuration
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/",
}

swagger_template = {
    "info": {
        "title": "TraqCheck API",
        "description": "API for resume processing and candidate verification",
        "version": "1.0.0"
    },
    "tags": [
        {"name": "Health", "description": "API health checks"},
        {"name": "Candidates", "description": "Candidate management endpoints"},
        {"name": "Documents", "description": "Document upload, download, and verification"},
        {"name": "Public", "description": "Public-facing endpoints for candidate portal"}
    ]
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

# Register Blueprints
from routes import candidates_bp, documents_bp, public_bp

app.register_blueprint(candidates_bp)
app.register_blueprint(documents_bp)
app.register_blueprint(public_bp)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
