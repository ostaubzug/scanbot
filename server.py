from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

@app.route('/frontend')
def home():
    return render_template('index.html')

@app.route('/trigger_function', methods=['POST'])
def trigger_function():
    # This is where you can perform actions when the button is clicked.
    print("Function triggered!")
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(debug=True)
