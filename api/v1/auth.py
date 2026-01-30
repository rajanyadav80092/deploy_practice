from flask import jsonify,render_template,redirect,url_for,session,flash,Blueprint,request
from models import User,Balance,Order
from extensions import db
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy import or_
import redis

current_redis=redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)



v1_auth=Blueprint("v1_auth",__name__)

@v1_auth.route("/signin",methods=["POST"])
def signin():
    name=request.form.get("name")
    email=request.form.get("email")
    age=request.form.get("age")
    mobile=request.form.get("mobile")
    password=request.form.get("password")
    is_first_user=User.query.count()==0
    
    
    hashed=generate_password_hash(password)
    
    user=User(name=name,email=email,age=age,mobile=mobile,password=hashed,role="admin" if is_first_user else "user")
    db.session.add(user)
    db.session.commit()
    flash("your id signin successfull")
    return redirect("/login")
    
@v1_auth.route("/login",methods=["POST"])
def login():
    identifier=request.form.get("identifier")
    password=request.form.get("password")
    user=User.query.filter(or_(User.name==identifier,
                         User.email==identifier,
                         User.mobile==identifier)).first()
    if not user:
        return jsonify({"msg":"user not found"})
    
    if user and  check_password_hash(user.password,password):
        session["user_id"]=user.id
        session["user_role"]=user.role
        flash("user login successfull")
        return redirect("/addorder")
    return jsonify({"msg":"check your password"})


@v1_auth.route("/logout")
def logout():
    if "user_id" not in session:
        return redirect("/login")
    session.clear()
    return jsonify({"msg":"logout successfullly"})

@v1_auth.route("/make-admin/<int:id>")
def make_admin(id):
    if "user_id" not in session:
        return redirect("/login")
    if session["user_role"] != "admin":
        return jsonify({"msg":"only admin make admin"})
    user=User.query.get(id)
    if not user:
        return jsonify({"msg":"user not found"})
    user.role="admin"
    db.session.commit()
    return jsonify({"msg":f"{user.name} made by admin"})

@v1_auth.route("/admin-email",methods=["POST"])
def make_admin_email():
    if "user_id" not in session:
        return redirect("/login")
    if session["user_role"]=="admin":
        email=request.form.get("email")
        user=User.query.filter_by(email=email).first()
        user.role="admin"
        db.session.commit()
        return jsonify({"msg":f"{user.name} made admin"})
    return jsonify({"msg":"only admin make admin"})
