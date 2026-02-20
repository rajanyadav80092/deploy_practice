from flask import jsonify,render_template,redirect,url_for,session,flash,Blueprint,request,json
from models import User,Balance,Order
from extensions import db
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy import or_
import redis
import random
from utils.sms import send_sms
from utils.emailer import send_email


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
    
    
    if not all([name, email, mobile, password, age]):
        flash("All fields are required")
        return redirect("/signin")
    
    hashed=generate_password_hash(password)
    use=User.query.filter_by(email=email).first()
    if use:
        flash("duplcate email your put")
        return redirect("/signin")
    
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
        flash("user not found")
        return redirect("/login")
    if user and  check_password_hash(user.password,password):
        session["user_id"]=user.id
        session["user_role"]=user.role
        flash("user login successfull")
        return redirect("/addorder")
    flash("check your password")
    return redirect("/login")


@v1_auth.route("/logout")
def logout():
    if "user_id" not in session:
        return redirect("/login")
    session.clear()
    flash("logout successfullly")
    return redirect("/login")

@v1_auth.route("/make-admin/<int:id>")
def make_admin(id):
    if "user_id" not in session:
        return redirect("/login")
    if session["user_role"] != "admin":
        flash("only admin make admin")
        return redirect("/")
    user=User.query.get(id)
    if not user:
        flash("user not found put correct user id")
        return redirect("/")
    user.role="admin"
    db.session.commit()
    flash(f"{user.name} made by admin")
    return redirect("/")
    

@v1_auth.route("/admin-email",methods=["POST"])
def make_admin_email():
    if "user_id" not in session:
        return redirect("/login")
    if session["user_role"]=="admin":
        email=request.form.get("email")
        user=User.query.filter_by(email=email).first()
        user.role="admin"
        db.session.commit()
        flash(f"{user.name} made admin")
        return redirect("/")
    flash("only admin make admin")
    return redirect("/")

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
            # REAL DELIVERY START
            send_sms(user.mobile, otp)
            send_email(user.email, otp)
            # REAL DELIVERY END

            flash("OTP sent to your mobile and email")
            print("sent otp:",f"otp : {otp} phone : {user.mobile}")
            session["reset_user_id"]=user.id
            return redirect("/verify")
        flash("error user not found")
        return redirect("/forget")
    flash("first fill identity")
    return redirect("/forget")

@v1_auth.route("/verifyotp",methods=["POST"])
def verify_otp():
    id=session.get("reset_user_id")
    otp=request.form.get("otp")
    if not id:
        flash("phone not found")
        return redirect("/forget")
    user=User.query.get(id)
    
    redis_key=f"otp:{user.mobile}"
    saved_otp=current_redis.get(redis_key)
    
    if saved_otp is None:
        print(f"mobile : {saved_otp}")
        flash("OTP expired or invalid"), 400
        return redirect("/forget")
    
    if saved_otp == otp:
        current_redis.delete(redis_key)
        flash("correct otp")
        return redirect("/loginagain")
    flash("Incorrect OTP"),400
    return redirect("/verify")
    
    
@v1_auth.route("/loginagain",methods=["POST"])
def loginagain():
    password=request.form.get("password")
    id=session.get("reset_user_id")
    user=User.query.get(id)
    if not user:
        flash("user not found")
        return redirect("/signin")
    user.password=generate_password_hash(password)
    session["user_id"]=user.id
    session.pop("reset_user_id", None)
    session["user_role"]=user.role
    db.session.commit()
    flash("login successfull")
    return redirect("/addorder")
    
    
@v1_auth.route("/delete_user",methods=["DELETE"])
def delete_user():
    if "user_id" not in session:
        return redirect("/login")
    id=session["user_id"]
    user=User.query.get(id)
    if not user:
        flash("user not found")
        return redirect("/signin")
    password=request.form.get("password")
    if user and not check_password_hash(user.password,password):
        flash("incorrect password")
        return redirect("/delete")
    db.session.delete(user)
    db.session.commit()
    flash("your id deleted")
    return redirect("/signin")

@v1_auth.route("/delete_bank",methods=["POST"])
def delete_bank():
    if "user_id" not in session:
        return redirect("/login")
    id=session["user_id"]
    bal=Balance.query.filter_by(user_bal_id=id).first()
    if not  bal:
        flash("balance id not made")
        return redirect("/addaccount")
    password=request.form.get("password")
    if bal and check_password_hash(bal.password,password):
        db.session.delete(bal)
        db.session.commit()
        flash("your bank account deleted")
        return redirect("/addaccount")
    flash("incorrect password")
    return redirect("/delete_ban")


       
