from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from typing import List

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(120), nullable=False)
    sub_date: Mapped[str] = mapped_column(String(50), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    favorites: Mapped[List["Favorite"]] = relationship(
        "Favorite", back_populates="user")

    def serialize(self):
        return {
            'id': self.id,
            'email': self.email,
            'sub_date': self.sub_date,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'favorites': [fav.item_id for fav in self.favorites]
        }


class Item(db.Model):
    __tablename__ = 'item'
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    favorites: Mapped[List["Favorite"]] = relationship(
        "Favorite", back_populates="item",
        cascade="all, delete-orphan")
    is_favorite: Mapped[bool] = mapped_column(Boolean, default=False)
    __mapper_args__ = {
        'polymorphic_identity': 'item',
        'polymorphic_on': type
    }

    def serialize(self):
        return {
            'id': self.id,
            'type': self.type,
            'name': self.name,
        }


class Character(Item):
    __tablename__ = 'character'
    id: Mapped[str] = mapped_column(
        String(100), db.ForeignKey('item.id'), primary_key=True)
    birth_year: Mapped[str] = mapped_column(String(50), nullable=False)
    gender: Mapped[str] = mapped_column(String(10), nullable=False)
    hair_color: Mapped[str] = mapped_column(String(50), nullable=False)
    eye_color: Mapped[str] = mapped_column(String(50), nullable=False)
    __mapper_args__ = {
        'polymorphic_identity': 'character',
    }

    def serialize(self):
        data = super().serialize()
        data.update({
            'birth_year': self.birth_year,
            'gender': self.gender,
            'hair_color': self.hair_color,
            'eye_color': self.eye_color,
        })
        return data


class Vehicle(Item):
    __tablename__ = 'vehicle'
    id: Mapped[str] = mapped_column(
        String(100), db.ForeignKey('item.id'), primary_key=True)
    passengers: Mapped[int] = mapped_column(db.Integer, nullable=False)
    cost_in_credits: Mapped[int] = mapped_column(db.Integer, nullable=False)
    max_atmosphering_speed: Mapped[int] = mapped_column(
        db.Integer, nullable=False)
    crew: Mapped[int] = mapped_column(db.Integer, nullable=False)
    __mapper_args__ = {
        'polymorphic_identity': 'vehicle',
    }

    def serialize(self):
        data = super().serialize()
        data.update({
            'passengers': self.passengers,
            'cost_in_credits': self.cost_in_credits,
            'max_atmosphering_speed': self.max_atmosphering_speed,
            'crew': self.crew,
        })
        return data


class Planet(Item):
    __tablename__ = 'planet'
    id: Mapped[str] = mapped_column(
        String(100), db.ForeignKey('item.id'), primary_key=True)
    population: Mapped[int] = mapped_column(db.Integer, nullable=False)
    climate: Mapped[str] = mapped_column(String(50), nullable=False)
    terrain: Mapped[str] = mapped_column(String(50), nullable=False)
    orbital_period: Mapped[int] = mapped_column(db.Integer, nullable=False)
    rotation_period: Mapped[int] = mapped_column(db.Integer, nullable=False)
    __mapper_args__ = {
        'polymorphic_identity': 'planet',
    }

    def serialize(self):
        data = super().serialize()
        data.update({
            'population': self.population,
            'climate': self.climate,
            'terrain': self.terrain,
            'orbital_period': self.orbital_period,
            'rotation_period': self.rotation_period,
        })
        return data


class Favorite(db.Model):
    item_id: Mapped[str] = mapped_column(
        db.ForeignKey('item.id'), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        db.ForeignKey('user.id'), primary_key=True)
    user: Mapped["User"] = relationship("User", back_populates="favorites")
    item: Mapped["Item"] = relationship("Item", back_populates="favorites")

    def serialize(self):
        return {
            'item_id': self.item_id,
            'user_id': self.user_id
        }
