from models import Order,User,Balance
from flask import session,request,flash,redirect,render_template,jsonify,url_for,json
from flask import jsonify,Blueprint
from extensions import db
from werkzeug.security import generate_password_hash,check_password_hash
from functools import wraps
import redis
import time

v1_orders=Blueprint("v1_orders",__name__)

current_redis=redis.Redis(
    host="localhost",
    db=0,
    port=6379,
    decode_responses=True
)

@v1_orders.route("/totalbalance")
def all_balance():
    if "user_id" not in session:
        return redirect("/login")
    # if request.form.get("csrf_token") != session.get("csrf_token"):
        
    if session["user_role"] != "admin":
        return jsonify({"msg":"your are not visit this page"})
    Acc=Balance.query.all()
    row=[]
    for a in Acc:
        row.append({
            "Account_holder_name":a.Acc_holder_name,
            "Acc_name":a.Acc_name,
            "Acc_num":a.account,
            "balance":a.balance,
            "Password":a.password,
            "id":a.id,
            "balance user id":a.user_bal_id
        })
    return jsonify({
        "Account detail":row
    })
@v1_orders.route("/mybalance",methods=["POST"])
def balance_detail():
    if "user_id" not in session:
        return redirect("/login")
    id=session["user_id"]
    bank=Balance.query.filter_by(user_bal_id=id).first()
    if not bank:
        return render_template("addaccount.html")
    password=request.form.get("password")
    if bank and check_password_hash(bank.password,password):
        return jsonify({"your balance": bank.balance})
    return jsonify({"msg":"please check your password"})

@v1_orders.route("/balancedetail/<int:id>")
def my_balance(id):
    if "user_id" not in session:
        return redirect("/login")
    if session["user_id"] != id:
        return redirect(url_for("v1_orders.my_balance",id=session["user_id"]))
    
    bal=Balance.query.filter_by(user_bal_id=id).first()
    row=[]
    if bal:
        row.append({
            "Acc Id":bal.id,
            "Name":bal.Acc_holder_name,
            "Bank name":bal.Acc_name,
            "User id":bal.user_bal_id,
            "Acc Num":bal.account,
            "balance":bal.balance,
            "Acc password":bal.password
        })
        return jsonify({
        "Acc detail":row
        })
    return render_template("addaccount.html")
    


@v1_orders.route("/addorder",methods=["POST"])
def add_order():
    if "user_id" not in session:
        return redirect("/login")
    product=request.form.get("product")
    try:
       amount=int(request.form.get("amount"))
    except(ValueError,TypeError):
        db.session.rollback()
        flash("invalid amount")
        return redirect("/addorder")
    id=session["user_id"]
    bal=Balance.query.filter_by(user_bal_id=id).first()
    if not bal:
        flash("add your account details")
        return redirect("/addaccount")
    if bal.balance<=amount:
        flash("your bank balance low add amount")
        return render_template("addbalance.html")
    bal.balance-=amount
    order=Order(amount=amount,product=product,user_id=session["user_id"])
    db.session.add(order)
    db.session.commit()
    flash("order added successfully")
    return render_template("addorder.html")

@v1_orders.route("/allord")
def allord():
    time.sleep(4)
    if "user_id" not in session:
        return redirect("/login")
    if session["user_role"] != "admin":
        return jsonify({"msg":"your are not visit this route"})
    order=Order.query.all()
    row=[]
    for o in order:
        row.append({
            "order":o.id,
            "amount":o.amount,
            "product":o.product,
            "user_id":o.user_id
        })
    return row

@v1_orders.route("/allorder")
def allorder():
    cache_key="product"
    cache_data=current_redis.get(cache_key)
    if cache_data:
        return jsonify({
            "source":"cache",
            "allorder":json.loads(cache_data)
        })
    product=allord()
    if not product:
        return jsonify({"msg":"not order please buy something"})
    current_redis.setex(cache_key,200,json.dumps(product))
    return jsonify({
        "source":"database",
        "allorder":product
    })
        
@v1_orders.route("/addaccount",methods=["POST"])
def add_account():
    if "user_id" not in session:
        return redirect("/login")
    name=request.form.get("Acc_holder_name")
    balance=request.form.get("balance")
    Acc_name=request.form.get("Acc_name")
    password=request.form.get("password")
    hashed=generate_password_hash(password)
    Acc_num=request.form.get("Acc_num")
    bala=Balance(Acc_holder_name=name,password=hashed,Acc_name=Acc_name,account=Acc_num,user_bal_id=session["user_id"],balance=balance)
    db.session.add(bala)
    db.session.commit()
    flash("balance added successfully buy order")
    return render_template("addorder.html")

@v1_orders.route("/addbalance",methods=["POST"])
def add_balance():
    if "user_id" not in session:
        return redirect("/login")
    user_id=session["user_id"]
    bal=Balance.query.filter_by(user_bal_id=user_id).first()
    if not bal:
        return jsonify({"msg":"bank account not found"})
    password=generate_password_hash(request.form.get("password"))
    try:
        amount=int(request.form.get("amount"))
    except(ValueError,TypeError):
        db.session.rollback()
        flash("invalid amount")
        return render_template("addbalance.html")
    bal.balance+=amount
    bal.password=password
    db.session.commit()
    flash("balance add successfull")
    return redirect("/addorder")    

@v1_orders.route("/alluser")
def all_user():
    if "user_id" not in session:
        return redirect("/login")
    if session["user_role"]!="admin":
        return jsonify({"msg":"your are not visit this route sorry"})
    user=User.query.all()
    row=[]
    for u in user:
        row.append({
            "id":u.id,
            "role":u.role,
            "name":u.name,
            "mobile":u.mobile,
            "email":u.email,
            "age":u.age
            
        })
    return jsonify({
        "user":row
    })


@v1_orders.route("/order/<int:id>/user")
def order_user(id):
    if "user_id" not in session:
        return redirect("/login")
    order=Order.query.get(id)
    if not order:
        return jsonify({"msg":"order not found"})
    row=[]
    if order:
        row.append({
            "product":o.product,
            "amount":o.amount,
            "order_id":o.id
        })
    return jsonify({
        "order":row,
        "user_name":o.user.name,
        "user_id":o.user_id
    })

@v1_orders.route("/order/user/<int:id>")
def user_order(id):
    if "user_id" not in session:
        return redirect("/login")
    if session["user_id"] != id:
        return redirect("v1_orders.user_order",id=session["user_id"])
    user=User.query.get(id)
    row=[]
    if not user:
        return jsonify({"msg":"User not found"})
    for o in user.orders:
        row.append({
            "user_id":o.id,
            "amount":o.amount,
            "product":o.product
        })
    return jsonify({
        "order":row,
        "user_name":user.name,
        "user_id":o.user_id
    })