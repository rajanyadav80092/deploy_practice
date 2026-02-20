from flask import Blueprint,session,redirect,jsonify,render_template,request,flash
from werkzeug.security import generate_password_hash,check_password_hash
from models import User,Order,Balance
from extensions import db
from sqlalchemy import or_

v1_update=Blueprint("v1_update",__name__)

@v1_update.route("/user_update",methods=["PUT"])
def user_update():
    if "user_id" not in session:
        return redirect("/login")
    id=session["user_id"]
    user=User.query.get(id)
    user.name=request.form.get("name")
    user.password=generate_password_hash(request.form.get("password"))
    user.mobile=request.form.get("mobile")
    user.age=request.form.get("age")
    email=request.form.get("email")
    existing_user = User.query.filter(
        or_(User.email == email)).first()
    if existing_user and user.email!=email:
        flash("email already exist")
        return redirect(url_for("v1_update.user_update"))
    user.email=email
    db.session.commit()
    flash("your id update successfully")
    return redirect("/addorder")

@v1_update.route("/update_account" , methods=["PUT"])
def update_account():
    if "user_id" not in session:
        return redirect("/login")
    id=session["user_id"]
    bal=Balance.query.filter_by(user_bal_id=id).first()
    bal.name=request.form.get("Acc_holder_name")
    bal.balance=request.form.get("balance")
    bal.Acc_name=request.form.get("Acc_name")
    password=request.form.get("password")
    bal.hashed=generate_password_hash(password)
    bal.Acc_num=request.form.get("Acc_num")
    db.session.commit()
    flash("Your account updated")
    return render_template("addorder.html")