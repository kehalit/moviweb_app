from flask import Flask,render_template, request, redirect, url_for, session,flash
from datamanager.sqllite_data_magager import SQLiteDataManager
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = "your_super_secret_key"
data_manager = SQLiteDataManager(app)


@app.errorhandler(404)
def page_not_found(e):
    """Handles 404 Not Found error."""
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    """Handles 500 Internal Server Error."""
    return render_template('500.html'), 500


@app.route('/')
def home():
   #return "Welcome to MovieWeb! Go to /users to see all users."
    users = data_manager.get_all_users()
    return render_template('home.html', users=users)


@app.route('/users')
def users_list():
   users = data_manager.get_all_users()
   return render_template('users.html', users=users)


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    user = data_manager.get_user(user_id)
    if user is None:
        return f"User with ID {user_id} not found.", 404
    movies = user.movies
    if not movies:
        return f"No movies found for user {user_id}.", 404
    return render_template('user_movies.html', user=user, movies=movies)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
  if request.method == 'POST':
      user_name = request.form['name']
      new_user = data_manager.add_user(user_name)
      return redirect(url_for('users_list'))
  return render_template('add_user.html')


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    user = data_manager.get_user(user_id)  # Fetch the user by ID

    if user is None:
        return f"User with ID {user_id} not found.", 404  # If user is not found, show an error

    if request.method == 'POST':
        movie_name = request.form.get('name')
        director = request.form.get('director')
        year = request.form.get('year')
        rating = request.form.get('rating')

        # Add movie using the data manager method
        data_manager.add_movie(user_id, movie_name, director, year, rating)
        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('add_movie.html', user=user)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    # Fetch the movie details from the database
    movie = data_manager.get_movie(movie_id)
    if movie is None:
        return f"Movie with ID {movie_id} not found.", 404

    if request.method == 'POST':
        # Fetch movie details from the API (for comparison)
        movie_data_from_api = data_manager.fetch_movie_details(movie.movie_name)

        # Check if the user has modified the fields, if not we compare with API data
        movie_name_changed = request.form['name'] != movie.movie_name
        director_changed = request.form['director'] != movie.director
        year_changed = int(request.form['year']) != movie.year
        rating_changed = float(request.form['rating']) != movie.rating

        if not (movie_name_changed or director_changed or year_changed or rating_changed):
            # If nothing has changed, let's check with the OMDb API
            if movie_data_from_api:
                # If the API data is different, update the movie details from the API
                if movie_data_from_api['movie_name'] != movie.movie_name:
                    movie.movie_name = movie_data_from_api['movie_name']
                if movie_data_from_api['director'] != movie.director:
                    movie.director = movie_data_from_api['director']
                if int(movie_data_from_api['year']) != movie.year:
                    movie.year = int(movie_data_from_api['year'])
                if float(movie_data_from_api['rating']) != movie.rating:
                    movie.rating = float(movie_data_from_api['rating'])

        else:
            # If the user has changed anything, update it directly from the form
            movie.movie_name = request.form['name']
            movie.director = request.form['director']
            movie.year = int(request.form['year'])
            movie.rating = float(request.form['rating'])

        # Commit the changes to the database
        data_manager.update_movie(movie)
        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('update_movie.html', movie=movie, user_id=user_id)




@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['GET', 'POST'])
def delete_movie(user_id, movie_id):
    movie = data_manager.get_movie(movie_id)  # Fetch movie by ID
    if movie is None:
        return f"Movie with ID {movie_id} not found.", 404

    if request.method == 'POST':
        data_manager.delete_movie(movie_id)  # Delete the movie
        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('delete_movie.html', user_id=user_id, movie=movie)


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    user = data_manager.get_user(user_id)
    if user:
        data_manager.delete_user(user_id)
        flash("User deleted successfully!", "success")
    else:
        flash ("Failed to delete user!", "error")

    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
