from extensions import db



class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(200),nullable=False)
    email=db.Column(db.String(200),unique=True,nullable=False)
    age=db.Column(db.Integer,nullable=False,default=18)
    mobile=db.Column(db.Integer,nullable=False)
    password=db.Column(db.String(200),nullable=False)
    role=db.Column(db.String(200),default="user",nullable=False)
    orders=db.relationship("Order",backref="user",lazy=True,cascade="all,delete-orphan")
    balance=db.relationship("Balance",backref="user",lazy=True,cascade="all,delete-orphan")
    # payment=db.relationship("Payment",backref="user",lazy=True,cascade="all,delete-orphan")
    
class Order(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    amount=db.Column(db.Integer,nullable=False,default=0)
    product=db.Column(db.String(200),nullable=False)
    user_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)

class Balance(db.Model):
    id=db.Column(db.Integer,primary_key=True ,nullable=False)
    Acc_name=db.Column(db.String(200),nullable=False)
    Acc_holder_name=db.Column(db.String(200),nullable=False)
    balance=db.Column(db.Integer,nullable=False,default=0)
    password=db.Column(db.String(200),nullable=False)
    account=db.Column(db.Integer,nullable=False)
    user_bal_id=db.Column(db.Integer,db.ForeignKey("user.id"),nullable=False)
    
# class Payment(db.Model):
#     id=db.Column(db.Integer,primary_key=True)
#     idempotency_key=db.Column(db.String(255),unique=True,nullable=False)
#     amount=db.Column(db.Float,nullable=False)
#     status=db.Column(db.String(50),default="pending")
#     response_data=db.Column(db.Text)
#     created_at=db.Column(db.datetime,default=datatime.utcnow)
#     payment_id=db.column(db.Integer,db.ForeignKey("user.id",nullable=False))