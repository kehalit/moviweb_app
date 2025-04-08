
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


