from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/health")
def health():
    return jsonify({"status": "flask_regime running"})

if __name__ == "__main__":
    app.run(port=8002)
