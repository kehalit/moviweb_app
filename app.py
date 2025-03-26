from flask import Flask,render_template, request, redirect, url_for
from sqlalchemy.testing.suite.test_reflection import users

from datamanager.sqllite_data_magager import SQLiteDataManager

app = Flask(__name__)
data_manager = SQLiteDataManager(app)

@app.route('/')
def home():
    return "Welcome to MovieWeb! Go to /users to see all users."


@app.route('/users')
def list_users():
   users = data_manager.get_all_users()
   return render_template('users_list.html', users=users)


@app.route('/users/<int:user_id>')
def list_user_movies(user_id):
    user = data_manager.get_user_movies(user_id)
    if user is None:
        return f"User with ID {user_id} not found.", 404
    return render_template('user_movies.html', user=user)

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
  pass

@app.route('/users/<user_id>/add_movie', methods=['GET', 'POST'])
def add_movie():
    pass


@app.route('/users/<user_id>/update_movie/<movie_id>')
def update_movie():
    pass

@app.route('/users/<user_id>/delete_movie/<movie_id>')
def delete_movie():
    pass


if __name__ == "__main__":
    app.run(debug=True)
