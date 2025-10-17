# agents/explainability/backend_api.py

import sys, os
# Force Python to treat 'LegisAI' as the project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from flask import Flask, request, jsonify
from flask_cors import CORS

# ✅ Import your consistency logic
from agents.explainability.cross_consistency import run_cross_consistency



from flask import Flask, request, jsonify
from flask_cors import CORS
from agents.explainability.cross_consistency import run_cross_consistency

app = Flask(__name__)
CORS(app)

@app.route("/api/check-consistency", methods=["POST"])
def check_consistency():
    data = request.get_json()
    clause = data.get("clause", "")
    results = run_cross_consistency(clause)
    return jsonify(results)

if __name__ == "__main__":
    print("✅ Flask backend running for Reasoning & Self-Consistency module...")
    app.run(debug=True)
