from flask import Flask, request, jsonify
from backend import routes

app = Flask(__name__)

app.register_blueprint(routes.bp)

if __name__ == "__main__":
    app.run(debug=True)
