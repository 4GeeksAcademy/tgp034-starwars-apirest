from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from typing import List

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'
    email: Mapped[str] = mapped_column(String(120), unique=True, primary_key=True)
    password: Mapped[str] = mapped_column(String(120), nullable=False)
    sub_date: Mapped[str] = mapped_column(String(50), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    favorites: Mapped[List["Favorite"]] = relationship("Favorite", back_populates="user")

    def serialize(self):
        return {
            'email': self.email,
            'sub_date': self.sub_date,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'favorites': [fav.item_uid for fav in self.favorites]
        }

class Item(db.Model):
    __tablename__ = 'item'
    uid: Mapped[str] = mapped_column(String(100), primary_key=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    favorites: Mapped[List["Favorite"]] = relationship("Favorite", back_populates="item")
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    __mapper_args__ = {
        'polymorphic_identity': 'item',
        'polymorphic_on': type
    }

    def serialize(self):
        return {
            'uid': self.uid,
            'type': self.type
        }

class Character(db.Model):
    __tablename__ = 'character'
    uid: Mapped[str] = mapped_column(db.ForeignKey('item.uid'), primary_key=True)
    id: Mapped[int] = mapped_column(db.Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    birth_year: Mapped[str] = mapped_column(String(50), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    hair_color: Mapped[str] = mapped_column(String(50), nullable=False)
    eye_color: Mapped[str] = mapped_column(String(50), nullable=False)
    __mapper_args__ = {
        'polymorphic_identity': 'character',
    }

    def serialize(self):
        return {
            'uid': self.uid,
            'id': self.id,
            'name': self.name,
            'birth_year': self.birth_year,
            'gender': self.gender,
            'hair_color': self.hair_color,
            'eye_color': self.eye_color,
        }

class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    uid: Mapped[str] = mapped_column(db.ForeignKey('item.uid'), primary_key=True)
    id: Mapped[int] = mapped_column(db.Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    passengers: Mapped[int] = mapped_column(db.Integer, nullable=False)
    cost_in_credits: Mapped[int] = mapped_column(db.Integer, nullable=False)
    max_atmosphering_speed: Mapped[int] = mapped_column(db.Integer, nullable=False)
    crew: Mapped[int] = mapped_column(db.Integer, nullable=False)
    __mapper_args__ = {
        'polymorphic_identity': 'vehicle',
    }

    def serialize(self):
        return {
            'uid': self.uid,
            'id': self.id,
            'name': self.name,
            'passengers': self.passengers,
            'cost_in_credits': self.cost_in_credits,
            'max_atmosphering_speed': self.max_atmosphering_speed,
            'crew': self.crew,
        }

class Planet(db.Model):
    __tablename__ = 'planet'
    uid: Mapped[str] = mapped_column(db.ForeignKey('item.uid'), primary_key=True)
    id: Mapped[int] = mapped_column(db.Integer, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    population: Mapped[int] = mapped_column(db.Integer, nullable=False)
    climate: Mapped[str] = mapped_column(String(50), nullable=False)
    terrain: Mapped[str] = mapped_column(String(50), nullable=False)
    orbital_period: Mapped[int] = mapped_column(db.Integer, nullable=False)
    rotation_period: Mapped[int] = mapped_column(db.Integer, nullable=False)
    __mapper_args__ = {
        'polymorphic_identity': 'planet',
    }

    def serialize(self):
        return {
            'uid': self.uid,
            'id': self.id,
            'name': self.name,
            'population': self.population,
            'climate': self.climate,
            'terrain': self.terrain,
            'orbital_period': self.orbital_period,
            'rotation_period': self.rotation_period,
        }

class Favorite(db.Model):
    item_uid: Mapped[str] = mapped_column(db.ForeignKey('item.uid'), primary_key=True)
    user_email: Mapped[str] = mapped_column(db.ForeignKey('user.email'), primary_key=True)
    user: Mapped["User"] = relationship("User", back_populates="favorites")
    item: Mapped["Item"] = relationship("Item", back_populates="favorites")
    
    def serialize(self):
        return {
            'item_uid': self.item_uid,
            'user_email': self.user_email
        }
