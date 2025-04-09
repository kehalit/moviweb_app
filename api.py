
from sqlalchemy.exc import SQLAlchemyError
from flask import Blueprint, jsonify, request

from datamanager.sqllite_data_magager import SQLiteDataManager


api = Blueprint('api', __name__)
data_manager = None


def init_data_manager(data_manager_app):
    """ Inititalite the data_manager with the Flask App"""
    global data_manager
    data_manager = data_manager_app


@api.route('/users', methods=['GET'])
def get_users():
    """Return a list of all users as JSON"""
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
    try:
        user = data_manager.get_user(user_id)
        if not user:
            return jsonify({"error": f"User with ID {user_id} not found"}), 404

        movies_data = [{
            "movie_id": movie.movie_id,
            "title": movie.movie_name,  # Try movie.movie_name or whatever works
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
