# backend_api.py
import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

# ✅ Dynamically add project root to sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
if project_root not in sys.path:
    sys.path.append(project_root)
print(f"🔧 Project root added: {project_root}")

# ✅ Import dummy agents and consistency function
from agents.explainability.agents.precedent_agent import precedent_agent
from agents.explainability.agents.compliance_agent import compliance_agent
from agents.explainability.agents.drafting_agent import drafting_agent
from agents.explainability.agents.risk_agent import risk_agent
from agents.explainability.agents.language_quality_agent import language_quality_agent
from agents.explainability.explainability.cross_consistency import run_cross_consistency

# ✅ Initialize Flask app
app = Flask(__name__)
CORS(app)
print("✅ Flask backend running for Reasoning & Self-Consistency module...")

# ✅ Health check route
@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Backend is running"}), 200


# ✅ Main API route
@app.route("/api/check-consistency", methods=["POST"])
def check_consistency():
    """
    Endpoint: /api/check-consistency
    Body: { "clause": "some legal text" }
    Returns JSON with results from all 5 agents
    """
    data = request.get_json()
    clause = data.get("clause", "")

    results = run_cross_consistency(clause)
    return jsonify(results)


if __name__ == "__main__":
    app.run(debug=True)
