from abc import ABC, abstractmethod

class DataManagerInterface(ABC):

    @abstractmethod
    def get_all_users(self):
        pass

    @abstractmethod
    def get_user_movies(self, user_id):
        pass
    @abstractmethod
    def add_user(self, name):
        pass

    @abstractmethod
    def add_movie(self, user_id, name, director, year, rating):
        pass

    @abstractmethod
    def update_movie(self, movie_id, movie_name, director, year, rating):
        pass

    @abstractmethod
    def delete_movie(self, user_id, movie_id):
        pass

    @abstractmethod
    def get_movie_reviews(self, movie_id):
        pass

    @abstractmethod
    def get_user_reviews(self, user_id):
        pass

    @abstractmethod
    def add_review(self, user_id, movie_id, review_text, rating):
        pass