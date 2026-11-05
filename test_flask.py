from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to my first Flask application!"

@app.route("/about")
def about():
    return "This is my first backend learning project!"

@app.route("/user/<name>")
def user(name):
    return f"Hello, {name}! Welcome to Flask."

if __name__ == "__main__":
    app.run(debug=True)