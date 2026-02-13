from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask,render_template,redirect,jsonify,flash,request,session
from config import Config
from extensions import db
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFProtect




app = Flask(__name__)


from api.v1.auth import v1_auth
from api.v1.orders import v1_orders
from api.v1.update import v1_update




app.config.from_object(Config)
app.config.update(
    # SESSION (v1)
    SESSION_COOKIE_SECURE=False,   # 🔥 local
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    WTF_CSRF_ENABLED=True,
    SECRET_KEY = "something-secret"

)

csrf = CSRFProtect(app)
db.init_app(app)

app.register_blueprint(v1_auth,url_prefix="/api/v1")
app.register_blueprint(v1_orders,url_prefix="/api/v1")
app.register_blueprint(v1_update,url_prefix="/api/v1")


MAIL_SERVER = os.getenv("EMAIL_HOST")
MAIL_PORT = os.getenv("EMAIL_PORT")
MAIL_USERNAME = os.getenv("EMAIL_USER")
MAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
MAIL_USE_TLS = True




@app.route("/")
def home():
    return render_template("base.html")

@app.route("/test")
def test():
    return render_template("test.html")

@app.route("/signin")
def signin():
    return render_template("signin.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/addorder")
def add_order():
    return render_template("addorder.html")

@app.route("/addaccount")
def addaccount():
    return render_template("addaccount.html")

@app.route("/loginagain")
def log():
    return render_template("loginagain.html")

@app.route("/addamount")
def add_amount():
    return render_template("addbalance.html")

@app.route("/mybalanc")
def mybalanc():
    return render_template("mybalance.html")

@app.route("/setting")
def setting():
    return render_template("setting.html")

@app.route("/forget")
def forget():
    return render_template("forget.html")

@app.route("/makeadmin")
def make():
    return render_template("make-admin.html")

@app.route("/verify")
def very():
    return render_template("verify.html")

@app.route("/update_user")
def update_user():
    return render_template("update_user.html")

@app.route("/update_account")
def update_account():
    return render_template("update_account.html")

@app.route("/myorder")
def myord():
    return redirect("/api/v1/myorder")

@app.route("/delete")
def delete():
    return render_template("delete.html")

@app.route("/delete_ban")
def delete_ban():
    return render_template("delete_bank.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000,debug=False)
   
