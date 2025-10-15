import os
from flask import Flask, request, jsonify
from flask_cors import CORS

# Import your 5 dummy agent classes
from agents.precedent_agent import precedent_agent
from agents.compliance_agent import compliance_agent
from agents.drafting_agent import drafting_agent
from agents.risk_agent import risk_agent
from agents.language_quality_agent import language_quality_agent

app = Flask(__name__)
CORS(app)

@app.route("/api/check-consistency", methods=["POST"])
def check_consistency():
    """Simulate running all agents on a given clause."""
    data = request.get_json()
    clause = data.get("clause", "")

    if not clause:
        return jsonify({"error": "Missing 'clause' in request"}), 400

    try:
        # Instantiate all agents
        agents = [
            precedent_agent(),
            compliance_agent(),
            drafting_agent(),
            risk_agent(),
            language_quality_agent()
        ]

        # Each agent produces a response
        outputs = []
        for agent in agents:
            outputs.append(agent.run(clause))

        # Simple consistency logic (mock)
        consistent = "CONSISTENT" if "risk" not in clause.lower() else "INCONSISTENT"
        confidence = round(0.8, 2)

        return jsonify({
            "clause": clause,
            "responses": outputs,
            "consistency_label": consistent,
            "confidence": confidence
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    print(" Simulated backend running at http://127.0.0.1:8000")
    app.run(host="127.0.0.1", port=8000, debug=True)
