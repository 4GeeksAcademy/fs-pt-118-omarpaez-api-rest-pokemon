from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, date
db = SQLAlchemy()

class User(db.Model):
    __tablename__ ='user'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(120), nullable=False)
    firstname: Mapped[str] = mapped_column(String(120), nullable=False)
    lastname: Mapped[str] = mapped_column(String(120), nullable= False)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    favoritespokemon: Mapped[list["FavoritesPokemon"]] = relationship(back_populates='user', uselist=True)
    favoritesitems: Mapped[list["FavoritesItems"]] = relationship(back_populates='user', uselist=True)


    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "favorites_items": [fav.serialize() for fav in self.favoritesitems]

            # do not serialize the password, its a security breach
        }


class Pokemon(db.Model):
    __tablename__ ='pokemon'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    url_img: Mapped[str] = mapped_column(String(150), nullable=False)
    favoritespokemon: Mapped[list["FavoritesPokemon"]] = relationship(back_populates='pokemon', uselist=True)
    types: Mapped[list["PokemonType"]] = relationship(back_populates='pokemon', uselist=True)

    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "url_img": self.url_img
        }

class Type(db.Model):
    __tablename__ ='type'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    pokemontype: Mapped["PokemonType"] = relationship(back_populates='type', uselist=False)

class PokemonType(db.Model):
    __tablename__ ='pokemontype'
    id: Mapped[int] = mapped_column(primary_key=True)
    pokemon_id: Mapped[int]= mapped_column(ForeignKey('pokemon.id'))
    pokemon: Mapped["Pokemon"] = relationship(back_populates='types', uselist=False)
    type_id: Mapped[int]= mapped_column(ForeignKey('type.id'))
    type: Mapped["Type"] = relationship(back_populates='pokemontype', uselist=False)
    

    
class Items(db.Model):
    __tablename__ ='items'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    url_img: Mapped[str] = mapped_column(String(150), nullable=False)
    favoritesitems: Mapped[list["FavoritesItems"]] = relationship(back_populates='items', uselist=True)
    
    def serialize(self):
        return{
            "id": self.id,
            "name": self.name,
            "url_img": self.url_img
        }
    
class FavoritesItems(db.Model):
    __tablename__ ='favoritesitems'
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user:Mapped["User"] = relationship(back_populates='favoritesitems', uselist=False)
    item_id: Mapped[int] = mapped_column(ForeignKey('items.id'))
    items:Mapped["Items"] = relationship(back_populates='favoritesitems')
   
    # Evitamos que se pueda agregar dos veces como favorito
    __table_args__ = (UniqueConstraint('user_id', 'item_id', name='_user_item_uc'),)

    def serialize(self):
        return{
            "id": self.id,
            "user":{"username": self.user.username} if self.user else None,
           # "items":{"id": self.items.id, "name": self.items.name}
            "item": self.items.serialize() if self.items else None
        }




class FavoritesPokemon(db.Model):
    __tablename__ ='favoritespokemon'
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user:Mapped["User"] = relationship(back_populates='favoritespokemon', uselist=False)
    pokemon_id: Mapped[int] = mapped_column(ForeignKey('pokemon.id'))
    pokemon:Mapped["Pokemon"] = relationship(back_populates='favoritespokemon', uselist=False)

    # Evitamos que se pueda agregar dos veces como favorito
    __table_args__ = (UniqueConstraint('user_id', 'pokemon_id', name='_user_pokemon_uc'),)

    def serialize(self):
        return{
            "id": self.id,
            "user":{"username": self.user.username} if self.user else None,
            "pokemons":{"id": self.pokemon.id, "name": self.pokemon.name}
        }



