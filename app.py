from crypt import methods

from flask import Flask,render_template, request, redirect, url_for
from sqlalchemy.testing.suite.test_reflection import users

from datamanager.sqllite_data_magager import SQLiteDataManager

app = Flask(__name__)
data_manager = SQLiteDataManager(app)

@app.route('/')
def home():
   #return "Welcome to MovieWeb! Go to /users to see all users."
    return render_template('home.html')


@app.route('/users')
def list_users():
   users = data_manager.get_all_users()
   return render_template('users.html', users=users)


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    user = data_manager.get_user_movies(user_id)
    movies = data_manager.get_user_movies(user_id)
    if user is None:
        return f"User with ID {user_id} not found.", 404
    return render_template('user_movies.html', user=user)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
  if request.method == 'POST':
      user_name = request.form['name']
      new_user = data_manager.add_user(user_name)
      return redirect(url_for('list_users'))
  return render_template('add_user.html')


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    movies = data_manager.get_user_movies(user_id)  # Returns a list
    user = data_manager.get_user(user_id)  # Fetch the user by ID

    if user is None:
        return f"User with ID {user_id} not found.", 404  # If user is not found, show an error

    if request.method == 'POST':
        movie_name = request.form.get('name')
        director = request.form.get('director')
        year = request.form.get('year')
        rating = request.form.get('rating')

        if movie_name and director and year and rating:
            data_manager.add_movie(user_id, movie_name, director, year, rating)  # Save the movie to DB
            return redirect(url_for('user_movies', user_id=user_id))  # Redirect to user's movie list

    return render_template('add_movie.html', user=user, movies=movies)  # Pass the user to the template


@app.route('/users/<user_id>/update_movie/<movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    movie = data_manager.get_movie(movie_id)
    if movie is None:
        return f"Movie with ID {movie_id} not found.", 404

    if request.method == 'POST':
        movie.movie_name = request.form['name']  # Fix field names
        movie.director = request.form['director']
        movie.year = int(request.form['year'])
        movie.rating = float(request.form['rating'])

        data_manager.update_movie(movie)  # Save changes to DB
        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('update_movie.html', movie=movie, user_id=user_id)

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
