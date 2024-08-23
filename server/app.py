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

class Restaurants(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [restaurant.to_dict(['address', 'id', 'name']) for restaurant in restaurants]
    
class RestaurantById(Resource):
    def get(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            return {'error': 'Restaurant not found'}, 404
        return restaurant.to_dict(), 200
    
    def delete(self, id):
        restaurant = Restaurant.query.filter_by(id=id).first()
        if not restaurant:
            return {'error': 'Restaurant not found'}, 404
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204

class Pizzas(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [pizza.to_dict(['id', 'ingredients', 'name']) for pizza in pizzas]
    
class RestaurantPizzas(Resource):
    def post(self):
        data = request.json
        try:
            new_pizza = RestaurantPizza(pizza_id = data.get('pizza_id'), restaurant_id = data.get('restaurant_id'), price = data.get('price'))
        except ValueError:
            return make_response({'errors': ['validation errors']}, 400)
        
        db.session.add(new_pizza)
        db.session.commit()
        return new_pizza.to_dict(), 201

api.add_resource(Restaurants, '/restaurants')
api.add_resource(RestaurantById, '/restaurants/<int:id>')
api.add_resource(Pizzas, '/pizzas')
api.add_resource(RestaurantPizzas, '/restaurant_pizzas')

if __name__ == "__main__":
    app.run(port=5555, debug=True)
