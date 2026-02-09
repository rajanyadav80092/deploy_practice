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

def allord():
    time.sleep(4)
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

@v1_orders.route("/totalbalance")
def all_balance():
    if "user_id" not in session:
        return redirect("/login")
    # if request.form.get("csrf_token") != session.get("csrf_token"):
        
    if session["user_role"] != "admin":
        flash("your are not visit this page")
        return redirect("/")
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
@v1_orders.route("/mybalance",methods=["POST","GET"])
def balance_detail():
    if "user_id" not in session:
        return redirect("/login")
    id=session["user_id"]
    bank=Balance.query.filter_by(user_bal_id=id).first()
    if not bank:
        return redirect("/addamount")
    password=request.form.get("password")
    if bank and check_password_hash(bank.password,password):
        return jsonify({"your balance": bank.balance})
    flash("please check your password")
    return redirect("/mybalanc")

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
    return redirect("/addorder")
    


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
        return redirect("/addamount")
    bal.balance-=amount
    order=Order(amount=amount,product=product,user_id=session["user_id"])
    db.session.add(order)
    db.session.commit()
    flash("order added successfully")
    return redirect("/addorder")




@v1_orders.route("/allorder")
def allorder():
    if "user_id" not in session:
        return redirect("/login")
    if session["user_role"]!="admin":
        flash("only admin axis this site")
        return redirect("/")
    cache_key="product"
    cache_data=current_redis.get(cache_key)
    if cache_data:
        return jsonify({
            "source":"cache",
            "allorder":json.loads(cache_data)
        })
    product=allord()
    if not product:
        flash("not order please buy something")
        return redirect("/addorder")
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
    return redirect("/addorder")

@v1_orders.route("/addbalance",methods=["POST"])
def add_balance():
    if "user_id" not in session:
        return redirect("/login")
    user_id=session["user_id"]
    bal=Balance.query.filter_by(user_bal_id=user_id).first()
    if not bal:
        return jsonify({"msg":"bank account not found"})
    password=request.form.get("password")
    if bal and not check_password_hash(bal.password,password):
        return jsonify({"msg":"please put correct password"})
    try:
        amount=int(request.form.get("amount"))
    except(ValueError,TypeError):
        db.session.rollback()
        flash("invalid amount")
        return redirect("/addaccount")
    bal.balance+=amount
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
    if not user:
        flash("empty file")
        return redirect("/signin")
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
        flash("order not found")
        return redirect("/addorder")
    return jsonify({
        "product":order.product,
        "amount":order.amount,
        "order_id":order.id,
        "user_name":order.user.name,
        "user_id":order.user_id
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
        flash("User not found")
        return redirect("/")
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
    
@v1_orders.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    total_orders = Order.query.filter_by(user_id=user_id).count()

    balance = Balance.query.filter_by(user_bal_id=user_id).first()

    return render_template("dashboard.html",
        total_orders=total_orders,
        balance=balance.balance if balance else 0
    )

@v1_orders.route("/admin-dashboard")
def admin_dashboard():
    if session.get("user_role") != "admin":
        flash("only admin allowed")
        return redirect("/")

    total_users = User.query.count()
    total_orders = Order.query.count()
    total_balance = db.session.query(db.func.sum(Balance.balance)).scalar()

    return render_template("admin_dashboard.html",
        total_users=total_users,
        total_orders=total_orders,
        total_balance=total_balance
    )
