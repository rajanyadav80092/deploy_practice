from flask import jsonify,render_template,redirect,url_for,session,flash,Blueprint,request,json
from models import User,Balance,Order
from extensions import db
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy import or_
import redis
import random

current_redis=redis.Redis(
    host="localhost",
    port=6379,
    db=0,
    decode_responses=True
)

def generate_otp():
    return str(random.randint(100000,999999))


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
    flash("logout successfullly")
    return render_template("login.html")

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

@v1_auth.route("/forget",methods=["POST"])
def forget():
    identifier=request.form.get("identifier")
    if identifier:
        user=User.query.filter(or_(User.name==identifier,
                                       User.email==identifier,
                                       User.mobile==identifier)).first()
        if user:
            otp=generate_otp()
            redis_key=f"otp:{user.mobile}"
            current_redis.setex(redis_key,120,otp)
            print("sent otp:",f"otp : {otp} phone : {user.mobile}")
            flash("fill otp")
            session["reset_user_id"]=user.id
            return render_template("verify.html")
        return jsonify({"msg":"error user not found"})
    flash("first fill identity")
    return render_template("forget.html")

@v1_auth.route("/verifyotp",methods=["POST"])
def verify_otp():
    id=session.get("reset_user_id")
    otp=request.form.get("otp")
    if not id:
        return jsonify({"msg":"phone not found"})
    user=User.query.get(id)
    
    redis_key=f"otp:{user.mobile}"
    saved_otp=current_redis.get(redis_key)
    
    if saved_otp is None:
        print(f"mobile : {saved_otp}")
        return jsonify({"error": "OTP expired or invalid"}), 400
    
    if saved_otp == otp:
        current_redis.delete(redis_key)
        flash("correct otp")
        return render_template("loginagain.html")
    return jsonify({"error": "Incorrect OTP"}),400
    
    
@v1_auth.route("/loginagain",methods=["POST"])
def loginagain():
    password=request.form.get("password")
    id=session.get("reset_user_id")
    user=User.query.get(id)
    if not user:
        return jsonify({"msg":"user not found"})
    user.password=generate_password_hash(password)
    session["user_id"]=user.id
    session.pop("reset_user_id", None)
    session["user_role"]=user.role
    db.session.commit()
    flash("login successfull")
    return render_template("addorder.html")
    
    
    
    
