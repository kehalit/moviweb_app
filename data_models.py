
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer
from sqlalchemy.orm import backref
from sqlalchemy.sql.sqltypes import NULLTYPE

db = SQLAlchemy()

class User(db.Model):

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    movies = db.relationship('Movie', backref= 'user', cascade = "all, delete-orphan")

    def __str__(self):
        return f"users(user_id = {self.user_id}, name = {self.name})"

class Movie(db.Model):

    __tablename__ = 'movies'

    movie_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    movie_name = db.Column(db.String(255), nullable=False)
    director = db.Column(db.String(255), nullable = False)
    year = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)

    def __str__(self):
        return (
                f"movies(id = {self.movie_id}, movie_name={self.movie_name},"
                f"director={self.director}, year={self.year},"
                f"rating= {self.rating})"
        )
