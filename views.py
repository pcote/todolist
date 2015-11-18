from flask import Flask, session, request, redirect, jsonify
from configparser import ConfigParser
import logging
from login import LoginHandler
import models


parser = ConfigParser()
parser.read("config.ini")


logger = logging.root

logger.setLevel(logging.INFO)

nudir = lambda mod: [x for x in dir(mod) if not x.startswith("_")]
app = Flask(__name__)


@app.route("/")
def index():
    if session and "userid" in session:
        return redirect("/static/main.html")
    else:
        return redirect("/static/login.html")


@app.route("/login")
def login():
    domain = parser["todolist"]["domain"]
    secrets_file = "client_secret.json"
    scope = "https://www.googleapis.com/auth/userinfo.email"
    redirect_uri = "http://{}/login".format(domain)
    login_handler = LoginHandler(secrets_file, scope, redirect_uri)

    if "code" in request.args:
        login_handler.setup_user_info(request.args["code"])
        session["email"] = login_handler.email
        session["display_name"] = login_handler.display_name
        return redirect("/static/main.html")
    else:
        return redirect(login_handler.auth_url)


@app.route("/userinfo")
def get_user_info():
    if session and session.get("email") and session.get("display_name"):
        email = session.get("email")
        display_name = session.get("display_name")
        data = dict(email=email, display_name=display_name)
        logger.info("Success in getting log information on user: {} at email: {}".format(display_name, email))
        return jsonify(data)
    else:
        return jsonify(dict(email="error", display_name="Could not get info for this user"))


@app.route("/todolist")
def get_todo_list():
    email = session.get("email")
    todo_list = models.get_user_todo_list(email)
    return jsonify(dict(todo_list=todo_list))


if __name__ == '__main__':
    app.secret_key = parser["todolist"]["session_key"]
    app.run(debug=True)