from flask import Flask,render_template,redirect,jsonify,flash,request,session
from config import Config
from extensions import db
from flask_wtf import CSRFProtect
from flask_wtf.csrf import CSRFProtect




app = Flask(__name__)


from api.v1.auth import v1_auth
from api.v1.orders import v1_orders
# from api.v1.update import v1_update


csrf = CSRFProtect()
app.config.from_object(Config)
app.config.update(
    # SESSION (v1)
    SESSION_COOKIE_SECURE=False,   # 🔥 local
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    WTF_CSRF_ENABLED=True,
)

db.init_app(app)


app.register_blueprint(v1_auth,url_prefix="/api/v1")
app.register_blueprint(v1_orders,url_prefix="/api/v1")
# app.register_blueprint(v1_update,url_prefix="/api/v1")



@app.route("/")
def home():
    return render_template("base.html")

@app.route("/signin")
def signin():
    return render_template("/signin.html")

@app.route("/login")
def login():
    return render_template("/login.html")

@app.route("/addorder")
def add_order():
    return render_template("addorder.html")

@app.route("/addaccount")
def addaccount():
    return render_template("addaccount.html")

@app.route("/mybalance")
def mybalance():
    return render_template("mybalance.html")

@app.route("/setting")
def setting():
    return render_template("setting.html")

@app.route("/makeadmin")
def make():
    return render_template("make-admin.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000,debug=False)
   
