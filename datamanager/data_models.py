from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

class User(db.Model):

    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)

    movies = db.relationship('Movie', backref= 'user', cascade = "all, delete-orphan")
    reviews = db.relationship('Review', backref= 'user', cascade = "all, delete-orphan")

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

    reviews = db.relationship('Review', backref= 'movie', cascade = "all, delete-orphan")

    def __str__(self):
        return (
                f"movies(id = {self.movie_id}, movie_name={self.movie_name},"
                f"director={self.director}, year={self.year},"
                f"rating= {self.rating})"
        )


class Review(db.Model):
    __tablename__ = 'reviews'
    review_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable = False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.movie_id'), nullable = False)
    review_text = db.Column(db.Text,  nullable=True)
    rating = db.Column(db.Float, nullable=False)


    def __str__(self):
        return (
                f"review(id= {self.review_id}, review_text={self.review_text},"
                f"rating={self.rating})"
        )

