import os

from datamanager.data_manager_interface import DataManagerInterface
from data_models import db, User, Movie


# Database configuration
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
database_path = os.path.join(basedir, 'db', 'movies.db')
print(database_path)
class SQLiteDataManager(DataManagerInterface):
    def __init__(self, app, db_file_name = "movies.db"):
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)

        with app.app_context():
            db.create_all()

    def get_all_users(self):
        #return all users
        return User.query.all()

    def get_user_movies(self, user_id):
        #return all movie list
        user = User.query.get(user_id) #!
        return user.movies if user else None


    def add_user(self, name):
        #add new user to db
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def add_movie(self, user_id, movie_name, director, year, rating):
        # add new movie to db
        user = User.query.get(user_id)
        if not user:
            return None
        new_movie = Movie(movie_name = movie_name, director=director, year=year, rating=rating, user_id=user_id)
        db.session.add(new_movie)
        db.session.commit()
        return new_movie

    def update_movie(self, movie_id , movie_name=None, director=None, year=None, rating=None):
        #update details of a specific movie in db
        movie = Movie.query.get(movie_id)
        if not movie:
            return None
        if movie_name:
            movie.movie_name = movie_name
        if director:
            movie.director = director
        if year:
            movie.year = year
        if rating:
            movie.rating = rating

        db.session.commit()
        return movie


    def delete_movie(self, movie_id):
        #delete specific movie from db
        movie = Movie.query.get(movie_id)
        if not movie:
            return False

        db.session.delete(movie) #sew
        db.session.commit()
        return True
