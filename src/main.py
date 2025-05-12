from flask import Flask, request, jsonify, render_template
import os
import conversation
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    query = data.get('query')
    if query:
        response = conversation.conv_manager.process_user_query('user_123', query)
        return jsonify({"message": response, "data": {"message": response}})
    return jsonify({"error": "No query provided"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5003))
    app.run(host='0.0.0.0', port=port, debug=True)
