from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/scanfunction', methods=['POST'])
def scan_function():
    data = request.get_json()  # Read the request body as JSON
    print("Request body:", data)
    # Perform actions with the request body data
    # ...
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
