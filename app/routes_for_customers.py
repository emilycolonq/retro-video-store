from flask import Blueprint, json, jsonify, request, make_response
from app.models.customer import Customer
from app.models.video import Video
from app.models.rental import Rental
from app import db
from flask_sqlalchemy import model
from sqlalchemy import func
import requests
from datetime import timedelta, datetime

from tests.test_wave_02 import CUSTOMER_ID

customers_bp = Blueprint("customers", __name__, url_prefix="/customers")

@customers_bp.route("", methods=["GET", "POST"])
def handle_cusomters():
    if request.method == "GET":
        customers = Customer.query.all()
        customers_response = []
        for customer in customers:
            customers_response.append(customer.create_customer_dict())
        return jsonify(customers_response)

    elif request.method == "POST":
        request_body = request.get_json()
        if not request_body.get("postal_code"):
            return make_response({"details":"Request body must include postal_code."}, 400) 
        
        elif not request_body.get("name"):
            return make_response({"details":"Request body must include name."}, 400) 

        elif not request_body.get("phone"):
            return make_response({"details":"Request body must include phone."}, 400) 
        
        new_customer = Customer(
            name=request_body["name"],
            postal_code=request_body["postal_code"],
            phone=request_body["phone"]
        )
        db.session.add(new_customer)
        db.session.commit()

        return make_response(new_customer.create_customer_dict(), 201)



@customers_bp.route("/<customer_id>", methods=["GET", "DELETE", "PUT"])
def handle_customer_by_id(customer_id):
    try:
        int(customer_id)
    except:
        return_message = {"message": f"Customer {customer_id} was not found"}
        return make_response(return_message, 400)

    customer= Customer.query.get(customer_id)
    if customer == None:
        return_message = {"message": f"Customer {customer_id} was not found"}
        return make_response(return_message, 404)

    elif request.method == "GET":
        return make_response(customer.create_customer_dict(), 200)
    
    elif request.method =="DELETE":
        db.session.delete(customer)
        db.session.commit()
        
        return make_response({"id":customer.id}, 200)

    elif request.method == "PUT":
        form_data = request.get_json()
        try:
            form_data["name"]
            form_data["postal_code"]
            form_data["phone"]
        except:
            return make_response("OOPs try again.", 400)
            
        customer.name = form_data["name"]
        customer.postal_code = form_data["postal_code"]
        customer.phone = form_data["phone"]

        db.session.commit()

        return make_response(customer.create_customer_dict(), 200)


@customers_bp.route("/<customer_id>/rentals", methods=["GET"])
def customers_current_rentals(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer: 
        return_message = {"message": f"Customer {customer_id} was not found"}
        return make_response(return_message, 404)

    videos_checked_out =[]
    rentals =Rental.query.filter_by(customer_id = customer.id).all()
    for rental in rentals: 
        videos_checked_out.append(rental.create_dict())
    return jsonify(videos_checked_out), 200