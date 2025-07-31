from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/test')
def test():
    return jsonify({"message": "Server is working!"})

if __name__ == '__main__':
    print("Starting test server...")
    app.run(host='localhost', port=5000, debug=False)
    print("Server started!") 