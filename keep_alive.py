# set up a server for bot to run 24/7

from flask import Flask
from threading import Thread

app = Flask("")


@app.route("/")
def home():
    return "Hello I am still alive!"


def run():
    app.run(host="0.0.0.0", port=8080)


def keep_running():
    t = Thread(target=run)
    t.start()
