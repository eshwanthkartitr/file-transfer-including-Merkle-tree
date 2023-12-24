from flask import Flask, jsonify, render_template, request
import threading
from client import main_pgm
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route("/client-query", methods=["POST"])
def use_client():
    data = request.json
    file_name = data["FileName"]
    main_pgm(file_name, 1)
    return jsonify({'status': 'success', 'FileName': file_name})


@app.route('/client-request', methods=["POST"])
def client_req():
    data = request.json
    file_req = data['filename_req']
    print("file_req", file_req)
    main_pgm(file_req, 2)
    return jsonify({'status': 'success', 'filename_req': file_req})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=12345, debug=True)
