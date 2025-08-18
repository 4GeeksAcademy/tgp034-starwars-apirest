"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Item, Favorite, Character, Vehicle, Planet
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/people', methods=['GET'])
def get_people():
    try:
        people = Character.query.all()
        if people:
            return jsonify([character.serialize() for character in people]), 200
        else:
            return jsonify({"error": "No people found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/people/<int:character_uid>', methods=['GET'])
def get_character(character_uid):
    try:
        character = Character.query.get(character_uid)
        if character:
            return jsonify(character.serialize()), 200
        else:
            return jsonify({"error": "Character not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/planets', methods=['GET'])
def get_planets():
    try:
        planets = Planet.query.all()
        if planets:
            return jsonify([planet.serialize() for planet in planets]), 200
        else:
            return jsonify({"error": "No planets found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/planets/<int:planet_uid>', methods=['GET'])
def get_planet(planet_uid):
    try:
        planet = Planet.query.get(planet_uid)
        if planet:
            return jsonify(planet.serialize()), 200
        else:
            return jsonify({"error": "Planet not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/vehicles', methods=['GET'])
def get_vehicles():
    try:
        vehicles = Vehicle.query.all()
        if vehicles:
            return jsonify([vehicle.serialize() for vehicle in vehicles]), 200
        else:
            return jsonify({"error": "No vehicles found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/vehicles/<int:vehicle_uid>', methods=['GET'])
def get_vehicle(vehicle_uid):
    try:
        vehicle = Vehicle.query.get(vehicle_uid)
        if vehicle:
            return jsonify(vehicle.serialize()), 200
        else:
            return jsonify({"error": "Vehicle not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()
        if users:
            return jsonify([user.serialize() for user in users]), 200
        else:
            return jsonify({"error": "No users found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#No autentication at this point so you need to send user_id of the user you want to see favorite list in the request body
@app.route('/users/favorites', methods=['GET'])
def get_favorites():
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    try:
        user = User.query.get(user_id)
        if user:
            favorites = user.favorites
            return jsonify([[favorite.serialize(), Item.query.get(favorite.item_id).name] for favorite in favorites]), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Only one method for favorite due to the polimorphy on Item so you can save as favorite any type of item with this method
@app.route('/users/favorites/<int:item_id>', methods=['POST'])
def add_favorite_item(item_id):
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id or not item_id:
        return jsonify({"error": "user_id and item_id are required"}), 400
    try:
        user = User.query.get(user_id)
        item = Item.query.get(item_id)
        if user and item:
            favorite = Favorite(user_id=user.id, item_id=item.id)
            db.session.add(favorite)
            db.session.commit()
            return jsonify({"message": "Favorite item added successfully"}), 201
        else:
            return jsonify({"error": "User or item not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Only one method for favorite due to the polimorphy on Item so you can delete as favorite any type of item with this method
@app.route('/users/favorites/<int:item_id>', methods=['DELETE'])
def remove_favorite_item(item_id):
    data = request.get_json()
    user_id = data.get('user_id')

    if not user_id or not item_id:
        return jsonify({"error": "user_id and item_id are required"}), 400
    try:
        user = User.query.get(user_id)
        item = Item.query.get(item_id)
        if user and item:
            favorite = Favorite.query.filter_by(user_id=user.id, item_id=item.id).first()
            if favorite:
                db.session.delete(favorite)
                db.session.commit()
                return jsonify({"message": "Favorite item removed successfully"}), 200
            else:
                return jsonify({"error": "Favorite not found"}), 404
        else:
            return jsonify({"error": "User or item not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
