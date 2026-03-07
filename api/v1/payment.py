from flask import Flask,Blueprint,request,jsonify
from models import Payment
from extensions import db

v1_payment=Blueprint("payment",__name__)

@v1_payment.route("/pay",methods=["POST"])
def pay():
    idempotency_key=request.headers.get("idempotency_key")
    data=request.get_json()
    
    if not idempotency_key:
        return jsonify({"error":"Idempotency_key required"}),400
    
    #check if already exist
    existing_payment=Payment.query.filter_by(idempotency_key=idempotency_key).first()
    
    if existing_payment:
        return jsonify({json.loads(existing_payment.response_data)}),200
    
    payment=Payment(
        idempotency_key=idempotency_key,
        user_id=data["user_id"],
        amount=data[amount],
        status="pending",
    )
    db.session.add(payment)
    db.session.commit()
    
    payment.status="success"
    response={
        "message":"payment successfull",
        "payment_id":pament.id,
        "amount":payment.amount
        
    }
    
    payment.response_data=json.dumps(response)
    db.session.commit()
    return jsonify(response),200