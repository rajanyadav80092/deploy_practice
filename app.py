from flask import Flask,render_template,redirect,jsonify,flash,request,session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from werkzeug.security import check_password_hash,generate_password_hash

app = Flask(__name__)
app.secret_key="my-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
db=SQLAlchemy(app)

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(200),nullable=False)
    email=db.Column(db.String(200),unique=True, nullable=False)
    password=db.Column(db.String(200),nullable=False)
    mobile=db.Column(db.String(20),nullable=False)
    orders=db.relationship("Order",backref="user",lazy=True,cascade="all,delete-orphan")

class Order(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    product=db.Column(db.String(200),nullable=False)
    amount=db.Column(db.String(10),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
    
with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("signin.html")

@app.route("/signin", methods=["GET","POST"])
def signin():
    if request.method=="POST":
        name=request.form.get("name")
        email=request.form.get("email")
        mobile=request.form.get("mobile")
        password=request.form.get("password")
        hashed=generate_password_hash(password)
        
        user=User(name=name,password=hashed,email=email,mobile=mobile)
        
        db.session.add(user)
        db.session.commit()
        flash("user signin successfull then login")
        return redirect("/login")
    return render_template("/signin.html")

@app.route("/login" , methods=["POST","GET"])
def login():
    if request.method=="POST":
        identifier=request.form.get("identifier")
        password=request.form.get("password")
        
        user=User.query.filter(or_(identifier==User.name,
                                   identifier==User.email,
                                   identifier==User.mobile,
                                   )).first()
        if not user:
            flash("user not found please try again ")
            return redirect("/login")
        if user and check_password_hash(user.password,password):
            session["user_id"]=user.id
            flash("user login successfull")
            return redirect("/addorder")
        return jsonify({"error":"password incorrect"})
    return render_template("/login.html")

@app.route("/addorder",methods=["POST","GET"])
def add_order():
    if "user_id" not in session:
        return redirect("/login")
    if not request.method=="POST":
        return render_template("addorder.html")
    product=request.form.get("product")
    try:
        amount=request.form.get("amount")
        amount=int(amount)
    except(TypeError,ValueError):
        db.session.rollback()
        flash("invalid amount")
        return redirect("/addorder")
    order=Order(product=product,amount=amount,user_id=session["user_id"])
    db.session.add(order)
    db.session.commit()
    return jsonify({"msg":"order commit successfull"})
@app.route("/allorder")
def all_order():
    if "user_id" not in session:
        return redirect("/login")
    id=session["user_id"]
    user=Order.query.all()
    row=[]
    for i in user:
        row.append({
            "product":i.product,
            "amount":i.amount,
            "oder_id":i.id
        })
    return jsonify({
        "user_id":i.user_id,
        "order":row
    })
    
        

@app.route("/alluser")
def alluser():
    user=User.query.all()
    row=[]
    for u in user:
        row.append({
            "name":u.name,
            "email":u.email,
            "password":u.password,
            "mobile":u.mobile
       } )
    return jsonify({
        "user":row
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000,debug=True)
   
