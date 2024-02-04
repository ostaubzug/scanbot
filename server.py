from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scanfunction', methods=['POST'])
def scan_function():
    data = request.get_json()  # Read the request body as JSON

    return data

if __name__ == '__main__':
     app.run(host='0.0.0.0', port=5400, debug=True)
