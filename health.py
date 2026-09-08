from flask import Flask, jsonify
import os
import sys
import requests

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    })

@app.route('/')
def index():
    return jsonify({
        "status": "CorectBet Bot is running",
        "version": "1.0.0"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
