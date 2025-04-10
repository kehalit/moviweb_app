import os
import requests
from sqlalchemy.exc import SQLAlchemyError
from datamanager.data_manager_interface import DataManagerInterface
from datamanager.data_models import db, User, Movie, Review
from dotenv import load_dotenv
from pathlib import Path


# OMDb API configuration
load_dotenv()
OMDB_API_URL = os.getenv('API_URL')
OMDB_API_KEY = os.getenv('API_KEY')


# Database configuration
basedir = Path(__file__).resolve().parent.parent
database_path = os.path.join(basedir, 'db', 'movies.db')


class SQLiteDataManager(DataManagerInterface):
    """SQLite data manager for handling movie and user data in the database."""

    def __init__(self, app):
        """Initialize the data manager with Flask app and configure the database."""
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(app)

        with app.app_context():
            db.create_all()

    def fetch_movie_details(self, movie_name):
        """Fetch movie details from OMDb API."""

        timeout_duration = 10
        params = {"t": movie_name, "apikey": OMDB_API_KEY}
        response = requests.get(OMDB_API_URL, params=params, timeout= timeout_duration)

        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "True":  # Movie found
                return {
                    "movie_name": data.get("Title"),
                    "director": data.get("Director"),
                    "year": data.get("Year"),
                    "rating": data.get("imdbRating"),
                }
        return None

    def get_all_users(self):
        """Retrieve all users from the database."""
        return User.query.all()

    def get_user(self, user_id):
        """Retrieve a user by their ID."""
        return User.query.get(user_id)

    def get_user_movies(self, user_id):
        """Retrieve all movies of a specific user by their user ID."""
        return Movie.query.filter_by(user_id=user_id).all()

    def get_movie(self, movie_id):
        """Retrieve a specific movie by its ID."""
        return Movie.query.filter_by(movie_id=movie_id).first()

    def add_user(self, name):
        """Add a new user to the database."""
        new_user = User(name=name)
        db.session.add(new_user)
        db.session.commit()
        return new_user

    def add_movie(self, user_id, movie_name):
        """
        Add a new movie to the database.

        If movie details are available from OMDb API, use those. Otherwise,
        use the provided user inputs.
        """

        movie_data = self.fetch_movie_details(movie_name)

        if not movie_data:
            return None  # Movie not found in OMDb, do not add

        new_movie = Movie(
            movie_name=movie_data["movie_name"],
            director=movie_data["director"],
            year=int(movie_data["year"]),
            rating=float(movie_data["rating"]),
            user_id=user_id
        )

        db.session.add(new_movie)
        db.session.commit()
        return new_movie


    def update_movie(self, movie_id, new_movie_name, new_director, new_year, new_rating):
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

        if not movie:
            return None

        updated_movie_data = self.fetch_movie_details(new_movie_name)
        if not updated_movie_data:
            print("❌ Movie not found in OMDb.")  # Debugging print
            return None

        movie.movie_name = new_movie_name
        movie.director =new_director
        movie.year = new_year
        movie.rating = new_rating

        db.session.commit()
        return movie


    def delete_movie(self, movie_id):
        """Delete a specific movie from the database."""
        movie = Movie.query.get(movie_id)
        if not movie:
            return False

        db.session.delete(movie)
        db.session.commit()
        return True

    def delete_user(self, user_id):
        """Delete a specific user from the database."""
        user = User.query.get(user_id)
        if not user:
            return False  # User not found

        db.session.delete(user)  # This will also delete related movies due to `cascade="all, delete-orphan"`
        db.session.commit()
        return True  # Successfully deleted the user

    def get_movie_reviews(self, movie_id):
        """
                Retrieves all reviews for a specific movie.

                Args:
                    movie_id (int): The ID of the movie for which reviews are being fetched.

                Returns:
                    list: A list of all review objects associated with the given movie ID.
        """
        return Review.query.filter_by(movie_id=movie_id).all()

    def get_user_reviews(self, user_id):
        """
                Retrieves all reviews submitted by a specific user.

                Args:
                    user_id (int): The ID of the user for which reviews are being fetched.

                Returns:
                    list: A list of all review objects submitted by the given user ID.
        """
        return Review.query.filter_by(user_id=user_id).all()

    def add_review(self, user_id, movie_id, review_text, rating):
        """
            Adds a new review for a specific movie by a user.

            Args:
                 user_id (int): The ID of the user submitting the review.
                 movie_id (int): The ID of the movie being reviewed.
                review_text (str): The text content of the review.
                rating (float): The rating given by the user for the movie, between 1.0 and 10.0.

            Returns:
                Review or None: Returns the created Review object if successful,
                                    or None if the movie or user does not exist.
        """
        movie = Movie.query.get(movie_id)
        user = User.query.get(user_id)

        if not movie or not user:
            return None

        new_review = Review(
            user_id=user_id,
            movie_id = movie_id,
            review_text = review_text,
            rating = float(rating)

        )

        db.session.add(new_review)
        db.session.commit()
        return new_review

    def view_review(self, movie_id):
        """Fetch all reviews for a given movie ID."""
        return Review.query.filter_by(movie_id=movie_id).all()

    def delete_review(self, review_id):
        """Delete a review by its ID."""
        review = Review.query.get(review_id)
        if Review:
            try:
                db.session.delete(review)
                db.session.commit()
                return True
            except SQLAlchemyError as e:
                db.session.rollback()
                print(f"Error deleting review: {str(e)}")
        return False