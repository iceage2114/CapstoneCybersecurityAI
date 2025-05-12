from flask import Flask, request, jsonify
import os
from ai_service import get_model_status, download_and_extract_model, load_model

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, Flask Server is running!"

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    return jsonify({"message": "Processing request", "data": data})

@app.route('/model/status', methods=['GET'])
def model_status():
    """Returns the current status of the model loading process"""
    return jsonify(get_model_status())

@app.route('/model/init', methods=['POST'])
def init_model():
    """Initializes the model download and loading process"""
    try:
        # Start the model download and loading in a non-blocking way
        # In a production app, this would be done in a separate thread or process
        download_and_extract_model()
        model = load_model()
        return jsonify({"message": "Model initialization completed", "status": get_model_status()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5003))
    app.run(host='0.0.0.0', port=port, debug=True)
