"""Support ticket Flask app backed by Lakebase via SQLAlchemy ORM."""

import logging
import os
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template
from controllers.ticket_controller import bp as ticket_bp

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("support-tickets-app")

app = Flask(__name__)
app.register_blueprint(ticket_bp)


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"})


@app.route("/")
def index():
    return render_template("index.html")


@app.errorhandler(Exception)
def handle_exception(err):
    logger.exception("Unhandled exception while processing request")
    status_code = getattr(err, "code", 500)
    if not isinstance(status_code, int):
        status_code = 500
    return jsonify({"error": str(err)}), status_code


if __name__ == "__main__":
    app.run(host="0.0.0.0",
            port=int(os.environ.get("PORT", "8080")),
            debug=True)
