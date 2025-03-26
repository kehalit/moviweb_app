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
  if request.method == 'POST':
      user_name = request.form['name']
      new_user = data_manager.add_user(user_name)
      return redirect(url_for('users_list'))
  return render_template('add_user.html')


@app.route('/users/<user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    if request.method == 'POST':
        movie_name= request.form['movie_name']
        director = request.form['director']
        year = int(request.form['year'])
        rating = float(request.form['rating'])
        new_movie = data_manager.add_movie(user_id, movie_name, director, year, rating)
        if new_movie:
            return redirect(url_for('users_movies', user_id=user_id))
        else:
            return f"User with ID {user_id} not found.", 404
    return render_template('add_movie.html', user_id=user_id)


@app.route('/users/<user_id>/update_movie/<movie_id>')
def update_movie(user_id, movie_id):
    movie = data_manager.get_user_movies(user_id)
    if movie is None:
        return f"User with ID {user_id} not found.", 404

    movie_to_update = next((m for m in movie if m.id == movie_id), None)
    if movie_to_update is None:
        return f"Movie with ID {movie_id} not found.", 404

    if request.method == 'POST':
        movie_to_update.name = request.form['name']
        movie_to_update.director = request.form['director']
        movie_to_update.year = int(request.form['year'])
        movie_to_update.rating = float(request.form['rating'])
        data_manager.update_movie(movie_to_update)
        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('update_movie.html', movie=movie_to_update)

@app.route('/users/<user_id>/delete_movie/<movie_id>')
def delete_movie(user_id, movie_id):
    movie = data_manager.get_user_movies(user_id)
    if movie is None:
        return f"User with ID {user_id} not found.", 404

    movie_to_delete = next((m for m in movie if m.id == movie_id), None)
    if movie_to_delete is None:
        return f"Movie with ID {movie_id} not found.", 404

    data_manager.delete_movie(movie_id)
    return redirect(url_for('user_movies', user_id=user_id))


if __name__ == "__main__":
    app.run(debug=True)
