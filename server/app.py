#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants')
def get_restaurants():
    restaurants=Restaurant.query.all()
    restaurant_dict=[restaurant.to_dict() for restaurant in restaurants]
    response=make_response(restaurant_dict,200)
    return response

@app.route('/restaurants/<int:id>',methods=['GET','DELETE'])
def get_by_id(id):
    restaurant=Restaurant.query.filter(Restaurant.id == id).first()
    if restaurant and request.method =='GET':
        restaurant_dict=restaurant.to_dict(only=('id','name','address','restaurant_pizzas'))
        response=make_response(restaurant_dict,200)
        return response
    elif request.method == 'DELETE':
        db.session.delete(restaurant)
        db.session.commit()
        response_body={
            'deleted_successfuly':True,
            'message':'restaurant deleted successfully'
            
        }
        response = make_response(response_body,204)
        return response
        
    else:
        response=make_response({'error':'Restaurant not found'},404)
        return response
    
@app.route('/pizzas')
def get_pizzas():
    pizzas=Pizza.query.all()
    pizzas_dict=[pizza.to_dict(rules=('-restaurant_pizzas',)) for pizza in pizzas]
    response=make_response(pizzas_dict,200)
    return response

@app.route('/restaurant_pizzas',methods=['GET','POST'])
def restraunt_pizza():
    restaurants=RestaurantPizza.query.all()
    if restaurants and request.method == 'GET':
        restaurant_dict=[restaurant.to_dict() for restaurant in restaurants]
        response=make_response(restaurant_dict,200)
        return response
    elif request.method == 'POST':
        data=request.get_json()
        price=data.get('price')
        restaurant_id=data.get('restaurant_id')
        pizza_id=data.get('pizza_id')

        if not (1 <= price <= 30):
            response=make_response({'errors':['validation errors']},400)
            return response

        
        if not price or not restaurant_id or not pizza_id:
            response=make_response({'errors':['validation errors']},400)
            return response
        new_request=RestaurantPizza(
            price=price,
            restaurant_id=restaurant_id,
            pizza_id=pizza_id
        )
        
        db.session.add(new_request)
        db.session.commit()

        request_dict=new_request.to_dict()
        response=make_response(request_dict,201)
        return response




    



if __name__ == "__main__":
    app.run(port=5555, debug=True)
