from flask import Flask, jsonify, render_template, request
import threading
from server import main_pgm
app = Flask(__name__)

# Global variable to keep track of client threads
client_threads = []

@app.route('/')
def index():
    # Renders the index.html template
    return render_template('index.html')

@app.route('/start-server', methods=['POST'])
def start_server():
    if not client_threads:
        return "Server started!"
    else:
        return "Server is already running."
@app.route('/set-clients',methods=["POST"])
def set_clients():
    data = request.json
    nums_clients = data['numClients']
    print(nums_clients)
    thread = threading.Thread(target=main_pgm,args=(int(nums_clients),))
    thread.start()
    client_threads.append(thread)
    return jsonify({'status': 'success', 'numClients': nums_clients})
    

if __name__ == '__main__':
    app.run(debug=True)
