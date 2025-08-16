#!/usr/bin/env python3
"""
Minimal Web UI for Employee_Engagement_Pulse
Provides health and a simple feedback API.
"""
import os
from flask import Flask, request, jsonify

app = Flask(__name__)

_FEEDBACK = {}

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/api/feedback', methods=['POST'])
def post_feedback():
    data = request.get_json() or {}
    user = data.get('user')
    text = data.get('text')
    if not user or not text:
        return jsonify({"error": "user and text required"}), 400
    _FEEDBACK.setdefault(user, []).append(text)
    return jsonify({"status": "ok"}), 200

@app.route('/api/feedback/<user>', methods=['GET'])
def get_feedback(user):
    return jsonify(_FEEDBACK.get(user, [])), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5004))
    print(f"Starting Employee_Engagement_Pulse web UI on port {port}")
    app.run(host='127.0.0.1', port=port, debug=True)
