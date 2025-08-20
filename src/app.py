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

@app.route('/items', methods=['GET'])
def get_items():
    try:
        items = Item.query.all()
        if items:
            return jsonify([item.serialize() for item in items]), 200
        else:
            return jsonify({"error": "No items found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400
    try:
        user = User.query.get(user_id)
        if user:
            favorites = user.favorites
            return jsonify([user.first_name, [favorite.item_id for favorite in favorites]]), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Only one method for favorite due to the polimorphy on Item so you can save as favorite any type of item with this method
@app.route('/users/favorites/', methods=['POST'])
def add_favorite_item():
    data = request.get_json()
    item_id = data.get('item_id')
    user_id = data.get('user_id')

    if not user_id or not item_id:
        return jsonify({"error": "user_id and item_id are required"}), 400
    try:
        user = User.query.get(user_id)
        item = Item.query.get(item_id)
        if not user or not item:
            return jsonify({"error": "User or item not found"}), 404

        existing_favorite = Favorite.query.filter_by(user_id=user.id, item_id=item.id).first()
        if existing_favorite:
            return jsonify({"error": "Item is already a favorite"}), 400
        
        favorite = Favorite(user_id=user.id, item_id=item.id)
        db.session.add(favorite)
        db.session.commit()
        return jsonify({"message": "Favorite item added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#Only one method for favorite due to the polimorphy on Item so you can delete as favorite any type of item with this method
@app.route('/users/favorites/', methods=['DELETE'])
def remove_favorite_item():
    data = request.get_json()
    user_id = data.get('user_id')
    item_id = data.get('item_id')

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

#Endpoint to create a new item
@app.route('/items', methods=['POST'])
def create_item():
    data = request.get_json()
    name = data.get('name')
    item_type = data.get('type')

    if item_type not in ['character', 'vehicle', 'planet']:
        return jsonify({"error": "Invalid item type"}), 400

    if not name or not item_type:
        return jsonify({"error": "Name and type are required"}), 400

    import uuid
    item_id = str(uuid.uuid4())

    if item_type == 'character':
        gender = data.get('gender')
        birth_year = data.get('birth_year')
        hair_color = data.get('hair_color')
        eye_color = data.get('eye_color')

        if not gender or not birth_year or not hair_color or not eye_color:
            return jsonify({"error": "Gender, birth year, hair color, and eye color are required for characters"}), 400
        item = Character(id=item_id, name=name, type='character', gender=gender, birth_year=birth_year, hair_color=hair_color, eye_color=eye_color)

    elif item_type == 'vehicle':
        passengers = data.get('passengers')
        cost_in_credits = data.get('cost_in_credits')
        max_atmosphering_speed = data.get('max_atmosphering_speed')
        crew = data.get('crew')

        if passengers is None or cost_in_credits is None or max_atmosphering_speed is None or crew is None:
            return jsonify({"error": "Passengers, cost in credits, max atmosphering speed, and crew are required for vehicles"}), 400
        item = Vehicle(id=item_id, name=name, type='vehicle', passengers=passengers, cost_in_credits=cost_in_credits, max_atmosphering_speed=max_atmosphering_speed, crew=crew)

    elif item_type == 'planet':
        population = data.get('population')
        climate = data.get('climate')
        terrain = data.get('terrain')
        orbital_period = data.get('orbital_period')
        rotation_period = data.get('rotation_period')
        if not climate or not terrain or population is None or not orbital_period or not rotation_period:
            return jsonify({"error": "Climate, terrain, population, orbital_period, and rotation_period are required for planets"}), 400
        item = Planet(id=item_id, name=name, type='planet', climate=climate, terrain=terrain, population=population, orbital_period=orbital_period, rotation_period=rotation_period)

    try:
        db.session.add(item)
        db.session.commit()
        return jsonify({"message": "Item created successfully", "item": item.serialize()}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/items', methods=['PUT'])
def edit_item():
    data = request.get_json()
    item_id = data.get('id')
    name = data.get('name')

    if not item_id or not name:
        return jsonify({"error": "ID and name are required"}), 400

    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    item.name = name

    if item.type == 'character':
        gender = data.get('gender')
        birth_year = data.get('birth_year')
        hair_color = data.get('hair_color')
        eye_color = data.get('eye_color')

        if not gender or not birth_year or not hair_color or not eye_color:
            return jsonify({"error": "Gender, birth year, hair color, and eye color are required for characters"}), 400
        item.gender = gender
        item.birth_year = birth_year
        item.hair_color = hair_color
        item.eye_color = eye_color

    elif item.type == 'vehicle':
        passengers = data.get('passengers')
        cost_in_credits = data.get('cost_in_credits')
        max_atmosphering_speed = data.get('max_atmosphering_speed')
        crew = data.get('crew')

        if passengers is None or cost_in_credits is None or max_atmosphering_speed is None or crew is None:
            return jsonify({"error": "Passengers, cost in credits, max atmosphering speed, and crew are required for vehicles"}), 400
        item.passengers = passengers
        item.cost_in_credits = cost_in_credits
        item.max_atmosphering_speed = max_atmosphering_speed
        item.crew = crew

    elif item.type == 'planet':
        population = data.get('population')
        climate = data.get('climate')
        terrain = data.get('terrain')
        orbital_period = data.get('orbital_period')
        rotation_period = data.get('rotation_period')
        if not climate or not terrain or population is None or not orbital_period or not rotation_period:
            return jsonify({"error": "Climate, terrain, population, orbital_period, and rotation_period are required for planets"}), 400
        item.climate = climate
        item.terrain = terrain
        item.population = population
        item.orbital_period = orbital_period
        item.rotation_period = rotation_period

    try:
        db.session.commit()
        return jsonify({"message": "Item updated successfully", "item": item.serialize()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/items', methods=['DELETE'])
def remove_item():
    data = request.get_json()
    item_id = data.get('id')

    if not item_id:
        return jsonify({"error": "ID is required"}), 400

    item = Item.query.get(item_id)
    if not item:
        return jsonify({"error": "Item not found"}), 404

    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Item deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
