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
from models import db, User, Pokemon, Items, FavoritesPokemon, FavoritesItems
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

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



# ------------------------
# Helpers
# ------------------------
def commit_and_serialize(obj):
    db.session.add(obj)
    db.session.commit()
    return jsonify(obj.serialize()), 201


# ------------------------
# USERS
# ------------------------

@app.route('/user', methods=['GET'])
def get_users():
    users = User.query.all()
   
    return jsonify([u.serialize() for u in users])

@app.route('/user/<int:id>', methods=["GET"])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.serialize())


# ------------------------
# POKEMONS
# ------------------------
@app.route('/pokemons', methods=['GET'])
def get_pokemons():
    pokemons = Pokemon.query.all()
    return jsonify([p.serialize() for p in pokemons])

@app.route('/pokemon/<name>', methods=["GET"])
def get_pokemon(name):
    query = select(Pokemon).where(Pokemon.name == name)
    pokemon = db.session.execute(query).scalar_one()
  
    return jsonify(pokemon.serialize())



# ------------------------
# ITEMS
# ------------------------

@app.route('/items', methods=['GET'])
def get_items():
    items = Items.query.all()
    return jsonify([i.serialize() for i in items])

@app.route('/item/<name>', methods=["GET"])
def get_item(name):
    query = select(Items).where(Items.name == name)
    item = db.session.execute(query).scalar_one()
    
    return jsonify(item.serialize())


# ------------------------
#  FAVORITESPOKEMONS
# ------------------------

## se agrega un pokemon a favoritos con el Id del usuario
@app.route('/favorite/pokemon/<int:id>', methods=['POST'])
def add_favorite_pokemon(id):
    data = request.json
    pokemonfavorite = FavoritesPokemon(user_id = id, pokemon_id = data["pokemon_id"])
    try:
        return commit_and_serialize(pokemonfavorite)
    except IntegrityError:  ## captura el error en caso de querer agregar dos veces el mismo pokemon como favorito
        db.session.rollback()
        return jsonify({"error": "Error al agregar el Pokemon a favoritos"}), 400
    

##se obtiene los pokemons favoritos del usuario (id)
@app.route('/user/<int:id>/favorites/pokemons', methods=["GET"])
def get_favorites_pokemon(id):
    query = select(FavoritesPokemon).where(FavoritesPokemon.user_id == id)
    favorites = db.session.execute(query).scalars().all()
    return jsonify([fav.pokemon.serialize() for fav in favorites])

##eliminamos de favoritos un pokemon por id de user y id de pokemon
@app.route('/user/<int:user_id>/favorites/pokemon/<int:pokemon_id>', methods=["DELETE"] )
def delete_favorite_pokemon(user_id, pokemon_id):
    query = select(FavoritesPokemon).where(
        FavoritesPokemon.user_id == user_id,
        FavoritesPokemon.pokemon_id == pokemon_id
    )
    favorite = db.session.execute(query).scalars().first()

    if not favorite:
        return jsonify({"error": "Favorito no encontrado"}), 404
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"success": "Pokemon eliminado de favoritos"}),200

# ------------------------
#  FAVORITESITEMS
# ------------------------
## se agrega un item a favoritos con el Id del usuario
@app.route('/favorite/item/<int:id>', methods=['POST'])
def add_favorite_item(id):
    data = request.json
    itemfavorite = FavoritesItems(user_id = id, item_id = data["item_id"])
    try:
       return commit_and_serialize(itemfavorite)
    except IntegrityError:  ## captura el error en caso de querer agregar dos veces el mismo item como favorito
        db.session.rollback()
        return jsonify({"error": "Error al agregar el Item a favoritos"}), 400
    
##se obtiene los items favoritos del usuario (id)
@app.route('/user/<int:id>/favorites/items', methods=["GET"])
def get_favorites_items(id):
    query = select(FavoritesItems).where(FavoritesItems.user_id == id)
    favorites = db.session.execute(query).scalars().all()
    return jsonify([fav.items.serialize() for fav in favorites])


##eliminamos de favoritos un item por id de user y id de pokemon
@app.route('/user/<int:user_id>/favorites/item/<int:item_id>', methods=["DELETE"] )
def delete_favorite_item(user_id, item_id):
    query = select(FavoritesItems).where(
        FavoritesItems.user_id == user_id,
        FavoritesItems.item_id == item_id
    )
    favorite = db.session.execute(query).scalars().first()

    if not favorite:
        return jsonify({"error": "Favorito no encontrado"}), 404
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({"success": "Item eliminado de favoritos"}),200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
