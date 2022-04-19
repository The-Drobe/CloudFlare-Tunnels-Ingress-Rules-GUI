from flask import Flask, request, render_template, redirect, url_for, session, g
import os
import csv
import re
import ipaddress
import threading
from time import sleep, time
from subprocess import Popen, DEVNULL, STDOUT
from passlib.hash import sha256_crypt
from datetime import datetime, timedelta
from flask_socketio import SocketIO
import CreateTunnel
import DeleteDnsEntryCloudFlare
import RemoveTunnel
import CloudFlaredTaskManger
RemoveDnsEntry = DeleteDnsEntryCloudFlare.main()
Createtunnel = CreateTunnel.main()
DeleteTunnel = RemoveTunnel.main()
CloudFlaredTaskmanger = CloudFlaredTaskManger.main()

# class for user handling
class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'

# import data from Login.txt
def PasswordImport():
    global users
    if os.path.exists("data/Login.txt") is True:
        with open("data/Login.txt") as file:
            users = []
            out = file.read()
            out = out.split(";")
            UserName = out[0]
            PassWordHash = out[1]
    else:
        users = []
        UserName = "FirstSetup"
        PassWord = "FirstSetup"
        PassWordHash = sha256_crypt.hash(PassWord)
    users.append(User(id=1, username=UserName, password=PassWordHash))


# Imports that are needed for the app to work

app = Flask(__name__)
socketio = SocketIO(app,)
app.secret_key = 'WhyAreYouGayWhoSaidIAmGay?'
app.permanent_session_lifetime = timedelta(minutes=10)
LastTimeRestarted = 0

@app.before_request
def before_request():
    g.user = None
# https://github.com/PrettyPrinted/youtube_video_code/blob/master/2020/02/10/Creating%20a%20Login%20Page%20in%20Flask%20Using%20Sessions/flask_session_example/app.py
    if 'user_id' in session:
        user = [x for x in users if x.id == session['user_id']][0]
        g.user = user

def ImportEnvVars():
    # import envirment vars:
    if os.path.exists("data/Setup.txt") is True:
        with open("data/Setup.txt") as file:
            global RootDomain
            global ApiKey
            global PathToCloudFlared
            out = file.read()
            out = out.split(";")
            ApiKey = out[0]
            RootDomain = []
            RootDomainTemp = out[1]
            RootDomainTemp = RootDomainTemp.split(",")
            # print(RootDomainTemp)
            for item in RootDomainTemp:
                RootDomain.append(item)
            PathToCloudFlared = out[2]

def GetTunnelsDisplay():
    # read csv document into 2d list
    data = []
    items = []
    if os.path.exists("data/tunnels.csv") is True:
        with open("data/tunnels.csv", errors='ignore') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            for row in spamreader:
                data.append(row)
    elif os.path.exists("data/tunnels.csv") is False:
        an_item = dict(domain="No tunnels created head over to Create tunnel to create your first tunnel", service="")
        items.append(an_item)
        return items

    if data == []:
        an_item = dict(domain="No tunnels created head over to Create tunnel to create your first tunnel", service="")
        items.append(an_item)
        return items

    for row in data:
        # print(row)
        an_item = dict(domain=row[0], service=row[2])
        items.append(an_item)

    return items


def CreateLogin(PassWord, UserName):
    hashedPassword = sha256_crypt.hash(PassWord)
    with open("data/Login.txt", "w") as file:
        file.write(UserName + ";" + hashedPassword)


@app.route('/', methods=["POST", "GET"])
def index():
    if not g.user:
        return redirect(url_for('login'))
    if os.path.exists("data/Setup.txt") is False:
        return redirect("/SetUp", code=301)
    if request.method == "GET":
        return render_template("index.html", items=GetTunnelsDisplay())


@app.route('/CreateTunnel', methods=["POST", "GET"])
def CreateTunnel():
    if not g.user:
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("CreateTunnel.html", Protocols=["http://", "https://"],
                               RootDomain=RootDomain, items=GetTunnelsDisplay())

@app.route('/CreatedTunnel', methods=["POST"])
def CreatedTunnel():
    if not g.user:
        return redirect(url_for('login'))
    Subdomain = request.form['subdomain'].lower()
    Rootdomain = request.form["RootDomains"].lower()
    ProtocolSelect = request.form["ProtocolSelect"].lower()
    application = request.form["application"].lower()
    Port = request.form["Port"].lower()
    Tls = request.form.get("Disable TLS Verify")

    # set Tls to true of false:
    if Tls is None:
        TlsTrueOrFalse = True
    elif Tls is not None and ProtocolSelect == "https://":
        TlsTrueOrFalse = False
    elif Tls is not None and ProtocolSelect == "http://":
        return "Disable TLS Verify is only for https:// services"

    # check that there is something in domain name
    if not re.match("^[A-Za-z0-9_-]*$", Subdomain):
        return """Subdomain is not valid: <a href="/CreateTunnel">Go back?</a>"""
    elif Subdomain == "":
        return """Subdomain is not valid: <a href="/CreateTunnel">Go back?</a>"""

        # check if Port is a port:
    if Port == "":
        return """Port Left Blank: <a href="/CreateTunnel">Go back?</a>"""
    if int(Port) > 65535:
        return """invalid port number: <a href="/CreateTunnel">Go back?</a>"""
    if int(Port) < 0:
        return """invalid port number: <a href="/CreateTunnel">Go back?</a>"""

    # check if the ip inputed is private
    if application == "localhost":
        application = "127.0.0.1"

    ipsplit = application.split('.')

    if len(ipsplit) != 4:
        return """Invalid Ip address please choose a private address: <a href="/CreateTunnel">Go back?</a>"""
    if len(ipsplit) == 4:
        for i in ipsplit:
            if i.isdigit() is False:
                return """Invalid Ip address please choose a private address: <a href="/CreateTunnel">Go back?</a>"""

    if ipaddress.ip_address(application).is_private is False:
        return """Invalid Ip address please choose a private address: <a href="/CreateTunnel">Go back?</a>"""

    FullApplication = ProtocolSelect + application + ":" + Port

    CheckIfTunnelExistsQA = Createtunnel.CheckIfTunnelExists(Subdomain, FullApplication, Rootdomain)

    if CheckIfTunnelExistsQA is True:
        return """That tunnel is taken please choose another: <a href="/CreateTunnel">Go back?</a>"""
    else:
        Createtunnel.CreateTunnel(Subdomain, FullApplication, Rootdomain, TlsTrueOrFalse, PathToCloudFlared)
        return redirect("/", code=302)


@app.route('/RemoveTunnel', methods=["POST", "GET"])
def RemoveTunnel():
    if not g.user:
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("RemoveTunnel.html", items=GetTunnelsDisplay())
    if request.method == "POST":
        checkbox = request.form.getlist('checkbox')
        for i in checkbox:
            DeleteTunnelOut = DeleteTunnel.RemoveTunnel(i, PathToCloudFlared)
            if DeleteTunnelOut == "StopCloudFlared":
                CloudFlaredTaskmanger.CloudFlaredTaskMangerStop()
        RemoveDnsEntry.main(checkbox, ApiKey)
        if os.path.exists("data/config.yml") is False:
            global CloudFlaredStop
            CloudFlaredStop = True
            # sleep(1)
            CloudFlaredStop = False
        return redirect("/RemoveTunnel", code=302)

@app.route('/SetUp', methods=["POST", "GET"])
def SetUp():
    if not g.user:
        return redirect(url_for('login'))
    if request.method == "GET":
        return render_template("SetUp.html")

@app.route('/SetUpConfirm', methods=["POST"])
def SetUpConfirm():
    if not g.user:
        return redirect(url_for('login'))
    global ApiKey
    global RootDomain
    global PathToCloudFlared
    global UserName
    global PassWord
    ApiKey = request.form['ApiKey']
    RootDomain = request.form['RootDomain'].lower()
    PathToCloudFlared = request.form['PathToCloudFlared']
    UserName = request.form['UserName']
    PassWord = request.form['PassWord']
    return render_template("SetUpConfirm.html", ApiKey=ApiKey, RootDomain=RootDomain,
                           PathToCloudFlared=PathToCloudFlared, UserName=UserName, PassWord=PassWord)

@app.route('/SetUpComplete', methods=["POST"])
def SetUpComplete():
    if not g.user:
        return redirect(url_for('login'))
    with open("data/Setup.txt", "w") as file:
        out = ApiKey + ";" + RootDomain + ";" + PathToCloudFlared
        file.write(out)
    CreateLogin(PassWord, UserName)
    PasswordImport()
    ImportEnvVars()
    return redirect("/", code=302)

@app.route('/CloudFlaredRestart', methods=["POST", "GET"])
def CloudFlaredRestart():
    if not g.user:
        return redirect(url_for('login'))
    global LastTimeRestarted
    if os.path.exists("data/config.yml") is False:
        return """There are currently no tunnels created please create one: <a href="/CreateTunnel">here</a>"""
    if time() >= LastTimeRestarted + 5:
        CloudFlaredTaskmanger.CloudFlaredTaskMangerStop()
        sleep(1)
        CloudFlaredTaskmanger.CloudFlaredTaskMangerStart()
        return redirect("/", code=303)
    else:
        return redirect("/", code=303)

@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == 'POST':
        session.pop('user_id', None)

        username = request.form['UserName']
        password = request.form['PassWord']

        user = [x for x in users if x.username == username]
        if user == []:
            return redirect(url_for('login'))
        else:
            user = user[0]
        if user and sha256_crypt.verify(password, user.password) is True:
            session['user_id'] = user.id
            return redirect(url_for('index'))

        return redirect(url_for('login'))

if __name__ == "__main__":
    # start Password import
    PasswordImport()
    ImportEnvVars()
    CloudFlaredTaskmanger.CloudFlaredTaskMangerStart()
    # app.run(debug=True, host="0.0.0.0", port=5000)
    socketio.run(app, debug=False, use_reloader=False, host='0.0.0.0', port=5000)
    # threading.Thread(target=web).start()
else:
    CloudFlaredTaskmanger.CloudFlaredTaskMangerStop()

# Copyright Giles Wardrobe 2022
