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
    """
    Log in the user to the system using Google oauth login.
    Note: What gets done here depends on what phase of the login process we are in.
    If this is the INITIAL PHASE, then send the user to the Google login.
    If we are COMING BACK from a Google login, use the code to get the email and display name set up for the user.
    :return: An appropriate redirect (depending on what step of the login process this is.
    """
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
    """
    Grab user info and send it back as json.
    :return: Json data about the user or else an error message if the info isn't available.
    """
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
    """
    Get the todo list of not-yet-done todo items for a given user.
    :return: JSON list of todo info.
    """
    email = session.get("email")
    todo_list = models.get_user_todo_list(email)
    return jsonify(dict(todo_list=todo_list))


@app.route("/completed", methods=["PUT"])
def completed_item():
    """
    Update to mark a JSON specified TODO item as completed.
    :return: A refreshed TODO list for the user excluding the completed item.
    """
    json_data = request.get_json()
    item_id = json_data.get("item_id")
    models.declare_item_done(item_id)

    email = session.get("email")
    todo_list = models.get_user_todo_list(email)
    return jsonify(dict(todo_list=todo_list))


@app.route("/addtodo", methods=["POST"])
def add_todo():
    """
    Add a todo item to the database.
    :return: An updated todo item list including the newly added todo item.
    """
    json_data= request.get_json()
    description = json_data.get("description")
    models.add_todo(session["email"], description)
    todo_list = models.get_user_todo_list(session["email"])
    return jsonify(dict(todo_list=todo_list))


if __name__ == '__main__':
    app.secret_key = parser["todolist"]["session_key"]
    app.run(debug=True)


