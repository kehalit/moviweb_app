import os
import requests
from datamanager.data_manager_interface import DataManagerInterface
from data_models import db, User, Movie


OMDB_API_KEY = os.getenv('API_KEY')
OMDB_URL = "http://www.omdbapi.com/"

# Database configuration
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
database_path = os.path.join(basedir, 'db', 'movies.db')


class SQLiteDataManager(DataManagerInterface):
    def __init__(self, app, db_file_name = "movies.db"):
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)

        with app.app_context():
            db.create_all()

    def fetch_movie_details(self, movie_name):
        """Fetch movie details from OMDb API."""
        params = {"t": movie_name, "apikey": OMDB_API_KEY}
        response = requests.get(OMDB_URL, params=params)

        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "True":  # Movie found
                return {
                    "movie_name": data.get("Title"),
                    "director": data.get("Director"),
                    "year": data.get("Year"),
                    "rating": data.get("imdbRating"),
                }
        return None  # Return None if movie not found

    def get_all_users(self):
        #return all users
        return User.query.all()

    def get_user(self, user_id):
        # Returns a single user by their ID
        return User.query.get(user_id)

    def get_user_movies(self, user_id):
        #return all movie list
        return User.query.filter_by(user_id=user_id).first()

    def get_movie(self, movie_id):
        return Movie.query.filter_by(movie_id=movie_id).first()

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
        db.session.commit()
        #return movie


    def delete_movie(self, movie_id):
        #delete specific movie from db
        movie = Movie.query.get(movie_id)
        if not movie:
            return False

        db.session.delete(movie) #sew
        db.session.commit()
        return True

    def delete_user(self, user_id):
        user = User.query.get(user_id)
        if not user:
            return False

        db.session.delete(user)  # This will also delete related movies due to `cascade="all, delete-orphan"`
        db.session.commit()
        return True

