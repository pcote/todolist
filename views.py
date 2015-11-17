from flask import Flask, session, request, redirect, jsonify
from configparser import ConfigParser
from oauth2client import client
import httplib2
from apiclient import discovery
import logging

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
    scope =  "https://www.googleapis.com/auth/userinfo.email"
    redirect_uri = "http://{}/login".format(domain)
    flow = client.flow_from_clientsecrets(secrets_file, scope=scope, redirect_uri=redirect_uri)

    if "code" in request.args:
        creds = flow.step2_exchange(request.args["code"])
        http_auth = creds.authorize(httplib2.Http())
        service = discovery.build("plus", "v1", http_auth)
        res = service.people().get(userId="me").execute()
        email = res.get("emails")[0].get("value")
        display_name = res.get("displayName")
        session["email"] = email
        session["display_name"] = display_name
        return redirect("/static/main.html")
    else:
        auth_url = flow.step1_get_authorize_url()
        return redirect(auth_url)

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

if __name__ == '__main__':


    app.secret_key = parser["todolist"]["session_key"]
    app.run(debug=True)