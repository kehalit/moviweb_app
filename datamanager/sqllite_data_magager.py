import os
import requests
from datamanager.data_manager_interface import DataManagerInterface
from data_models import db, User, Movie
from dotenv import load_dotenv

# OMDb API configuration
load_dotenv()
OMDB_API_URL = os.getenv('API_URL')
OMDB_API_KEY = os.getenv('API_KEY')


# Database configuration
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
database_path = os.path.join(basedir, 'db', 'movies.db')


class SQLiteDataManager(DataManagerInterface):
    """SQLite data manager for handling movie and user data in the database."""

    def __init__(self, app, db_file_name="movies.db"):
        """Initialize the data manager with Flask app and configure the database."""
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)

        with app.app_context():
            db.create_all()

    def fetch_movie_details(self, movie_name):
        """Fetch movie details from OMDb API."""
        params = {"t": movie_name, "apikey": OMDB_API_KEY}
        response = requests.get(OMDB_API_URL, params=params)

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
        """Retrieve all users from the database."""
        return User.query.all()

    def get_user(self, user_id):
        """Retrieve a user by their ID."""
        return User.query.get(user_id)

    def get_user_movies(self, user_id):
        """Retrieve all movies of a specific user by their user ID."""
        return User.query.filter_by(user_id=user_id).first()

    def get_movie(self, movie_id):
        """Retrieve a specific movie by its ID."""
        return Movie.query.filter_by(movie_id=movie_id).first()

    def add_user(self, name):
        """Add a new user to the database."""
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def add_movie(self, user_id, movie_name, director=None, year=None, rating=None):
        """
        Add a new movie to the database.

        If movie details are available from OMDb API, use those. Otherwise,
        use the provided user inputs.
        """
        movie_data = self.fetch_movie_details(movie_name)

        # Use fetched data if available, otherwise use user input
        if movie_data:
            new_movie = Movie(
                movie_name=movie_data["movie_name"],
                director=movie_data["director"],
                year=int(movie_data["year"]),
                rating=float(movie_data["rating"]),
                user_id=user_id
            )
        else:
            # If OMDb does not provide data, use user input directly
            new_movie = Movie(
                movie_name=movie_name,
                director=director,
                year=int(year),
                rating=float(rating),
                user_id=user_id
            )

        db.session.add(new_movie)
        db.session.commit()
        return new_movie

    def update_movie(self, movie_id, movie_name=None, director=None, year=None, rating=None):
        """
        Update the details of a specific movie in the database.

        Args:
            movie_id (int): The ID of the movie to be updated.
            movie_name (str, optional): The new movie name.
            director (str, optional): The new director name.
            year (int, optional): The new release year.
            rating (float, optional): The new IMDB rating.
        """
        movie = Movie.query.get(movie_id)
        if movie:
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
        return None  # If the movie does not exist, return None

    def delete_movie(self, movie_id):
        """Delete a specific movie from the database."""
        movie = Movie.query.get(movie_id)
        if not movie:
            return False  # Movie not found

        db.session.delete(movie)
        db.session.commit()
        return True  # Successfully deleted the movie

    def delete_user(self, user_id):
        """Delete a specific user from the database."""
        user = User.query.get(user_id)
        if not user:
            return False  # User not found

        db.session.delete(user)  # This will also delete related movies due to `cascade="all, delete-orphan"`
        db.session.commit()
        return True  # Successfully deleted the user
