from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permite peticiones desde cualquier frontend

@app.route('/')
def home():
    return jsonify({"message": "¡Backend Flask funcionando correctamente!"})

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"greeting": "Hola desde Flask 🐍"})

@app.route('/api/echo', methods=['POST'])
def echo():
    data = request.json
    return jsonify({"you_sent": data})

if __name__ == '__main__':
    app.run(debug=True)
