from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError

from datamanager.sqllite_data_magager import SQLiteDataManager

api = Blueprint('api', __name__)
data_manager = None


def init_data_manager(data_manager_app):
    """
    Initializes the global data_manager used across the API.

    Args:
        data_manager_app (SQLiteDataManager): The data manager instance from the app.
    """
    global data_manager
    data_manager = data_manager_app


@api.route('/users', methods=['GET'])
def get_users():
    """
    Retrieve a list of all users.

    Returns:
        JSON: A list of user objects with their ID and name.
    """
    try:
        users = data_manager.get_all_users()
        users_data = [{
            "user_id": user.user_id,
            "name": user.name
        } for user in users]
        return jsonify({"users": users_data}), 200
    except SQLAlchemyError as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500


@api.route('/users/<int:user_id>/movies', methods=['GET'])
def get_user_movies(user_id):
    """
    Retrieve a list of movies for a specific user.

    Args:
        user_id (int): The user's ID.

    Returns:
        JSON: User details along with their list of movies.
    """
    try:
        user = data_manager.get_user(user_id)
        if not user:
            return jsonify({"error": f"User with ID {user_id} not found"}), 404

        movies_data = [{
            "movie_id": movie.movie_id,
            "title": movie.movie_name,
            "director": movie.director,
            "year": movie.year,
            "rating": movie.rating
        } for movie in user.movies]

        return jsonify({
            "user_id": user.user_id,
            "name": user.name,
            "movies": movies_data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api.route('/users/<int:user_id>/movies', methods=['POST'])
def add_movie_to_user(user_id):
    """
    Add a new favorite movie to a user's collection.

    Request JSON:
        {
            "title": "Movie Title"
        }

    Args:
        user_id (int): The user's ID.

    Returns:
        JSON: Confirmation message and movie data if successful.
    """
    try:
        data = request.get_json()
        if not data or 'title' not in data:
            return jsonify({'error': 'Missing movie title in request'}), 400

        title = data['title']
        user = data_manager.get_user(user_id)

        if not user:
            return jsonify({'error': f'User with ID {user_id} not found'}), 404

        movie = data_manager.add_movie(user_id, title)

        if not movie:
            return jsonify({'error': 'Movie not found in OMDb'}), 404

        movie_data = {
            "movie_id": movie.movie_id,
            "title": movie.movie_name,
            "director": movie.director,
            "year": movie.year,
            "rating": movie.rating
        }

        return jsonify({'message': 'Movie added successfully', 'movie': movie_data}), 201

    except SQLAlchemyError as e:
        return jsonify({'error': f'Database error: {str(e)}'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500
