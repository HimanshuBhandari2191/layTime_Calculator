from flask import Flask
from flask_cors import CORS


def create_app() -> Flask:
	app = Flask(__name__)

	# Configure CORS for API routes
	CORS(app, resources={r"/api/*": {"origins": "*"}})

	# Register blueprints
	from .routes import api_bp  # lazy import to avoid circular deps
	app.register_blueprint(api_bp, url_prefix="/api")

	# Health check
	@app.get("/api/health")
	def health():
		return {"status": "ok"}, 200

	return app


