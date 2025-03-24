from flask_sqlalchemy import SQLAlchemy
from datamanager.data_manager_interface import DataManagerInterface

class SQLiteDataManager(DataManagerInterface):
    def __init__(self, db_file_name):
        self.db = SQLAlchemy(db_file_name)

    def get_all_users(self):
        #return all users
        pass

    def get_user_movies(self, user_id):
        #return all movie list
        pass

    def add_movie(self, user):
        #add new user to db
        pass

    def add_movie(movie):
        # add new movie to db
        pass

    def update_movie(movie):
        #update details of a specific movie in db
        pass

    def delete_movie(movie_id):
        #delete specific movie from db
        pass
