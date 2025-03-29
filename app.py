import os
from csv import excel
from multiprocessing.managers import Value

from flask import Flask, render_template, request, redirect, url_for, flash
from datamanager.sqllite_data_magager import SQLiteDataManager
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
data_manager = SQLiteDataManager(app)


@app.errorhandler(404)
def page_not_found(e):
    """Handles 404 Not Found error."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    """Handles 500 Internal Server Error."""
    return render_template('500.html'), 500


@app.errorhandler(Exception)
def handle_exception(e):
    """Handles generic exceptions."""
    if isinstance(e, HTTPException):
        return e  # If it's a Flask HTTPException (e.g., 404, 405), return it directly
    else:
        # Log the error or notify the admin if necessary
        flash(f"An unexpected error occurred: {str(e)}", "error")
        return redirect(url_for('home'))  # Redirect to home page with error message


@app.route('/')
def home():
    """Displays the home page with the list of users."""
    try:
        users = data_manager.get_all_users()
        return render_template('home.html', users=users)
    except SQLAlchemyError as e:
        flash(f"Database error occurred: {str(e)}", "error")
        return render_template('home.html')


@app.route('/users')
def users_list():
    """Displays the list of all users."""
    try:
        users = data_manager.get_all_users()
        return render_template('users.html', users=users)
    except SQLAlchemyError as e:
        flash(f"Database error occurred: {str(e)}", "error")
        return render_template('users.html')


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    """Displays a user's movies."""
    try:
        user = data_manager.get_user(user_id)
        if user is None:
            return f"User with ID {user_id} not found.", 404
        movies = user.movies if user.movies else []
        return render_template('user_movies.html', user=user, movies=movies)
    except SQLAlchemyError as e:
        flash(f"Database error occurred: {str(e)}", "error")
        return render_template('home.html')


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """Handles the addition of a new user."""
    try:
        if request.method == 'POST':
            user_name = request.form['name']
            if not user_name:
                flash("User name cannot be empty!", "error")
                return redirect(url_for('add_user'))
            new_user = data_manager.add_user(user_name)
            return redirect(url_for('users_list'))
        return render_template('add_user.html')
    except SQLAlchemyError as e:
        flash(f"Database error occurred: {str(e)}", "error")
        return redirect(url_for('add_user'))


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """Handles adding a movie for a specific user."""
    try:
        user = data_manager.get_user(user_id)
        if user is None:
            return f"User with ID {user_id} not found.", 404

        if request.method == 'POST':
            movie_name = request.form.get('name')
            director = request.form.get('director')
            year = request.form.get('year')
            rating = request.form.get('rating')

            if not movie_name or not director or not year or not rating:
                flash("Please fill in all fields!", "error")
                return redirect(url_for('add_movie', user_id=user_id))

            # Add movie using the data manager method
            data_manager.add_movie(user_id, movie_name, director, year, rating)
            return redirect(url_for('user_movies', user_id=user_id))

        return render_template('add_movie.html', user=user)
    except SQLAlchemyError as e:
        flash(f"Database error occurred: {str(e)}", "error")
        return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """Handles the update of a movie for a specific user."""
    try:
        movie = data_manager.get_movie(movie_id)
        if movie is None:
            return f"Movie with ID {movie_id} not found.", 404

        if request.method == 'POST':
            movie_data_from_api = data_manager.fetch_movie_details(movie.movie_name)

            # Check if the user has modified the fields, if not compare with API data
            movie_name_changed = request.form['name'] != movie.movie_name
            director_changed = request.form['director'] != movie.director
            year_changed = int(request.form['year']) != movie.year
            rating_changed = float(request.form['rating']) != movie.rating

            if not (movie_name_changed or director_changed or year_changed or rating_changed):
                # If nothing has changed, compare with the API data
                if movie_data_from_api:
                    if movie_data_from_api['movie_name'] != movie.movie_name:
                        movie.movie_name = movie_data_from_api['movie_name']
                    if movie_data_from_api['director'] != movie.director:
                        movie.director = movie_data_from_api['director']
                    if int(movie_data_from_api['year']) != movie.year:
                        movie.year = int(movie_data_from_api['year'])
                    if float(movie_data_from_api['rating']) != movie.rating:
                        movie.rating = float(movie_data_from_api['rating'])
            else:
                movie.movie_name = request.form['name']
                movie.director = request.form['director']
                movie.year = int(request.form['year'])
                movie.rating = float(request.form['rating'])

            data_manager.update_movie(movie)
            return redirect(url_for('user_movies', user_id=user_id))

        return render_template('update_movie.html', movie=movie, user_id=user_id)
    except SQLAlchemyError as e:
        flash(f"Database error occurred: {str(e)}", "error")
        return redirect(url_for('user_movies', user_id=user_id))
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", "error")
        return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/delete_movie/<int:movie_id>', methods=['GET', 'POST'])
def delete_movie(user_id, movie_id):
    """Handles the deletion of a movie for a specific user."""
    try:
        movie = data_manager.get_movie(movie_id)
        if movie is None:
            return f"Movie with ID {movie_id} not found.", 404

        if request.method == 'POST':
            data_manager.delete_movie(movie_id)
            return redirect(url_for('user_movies', user_id=user_id))

        return render_template('delete_movie.html', user_id=user_id, movie=movie)
    except SQLAlchemyError as e:
        flash(f"Database error occurred: {str(e)}", "error")
        return redirect(url_for('user_movies', user_id=user_id))
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", "error")
        return redirect(url_for('user_movies', user_id=user_id))


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    """Handles the deletion of a user."""
    try:
        user = data_manager.get_user(user_id)
        if user:
            data_manager.delete_user(user_id)
            flash("User deleted successfully!", "success")
        else:
            flash("Failed to delete user!", "error")

        return redirect(url_for('home'))
    except SQLAlchemyError as e:
        flash(f"Database error occurred: {str(e)}", "error")
        return redirect(url_for('home'))
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", "error")
        return redirect(url_for('home'))


@app.route("/users/<user_id>/movies/<movie_id>/add_review", methods=['GET', 'POST'])
def add_review(user_id, movie_id):
    user = data_manager.get_user(user_id)
    movie = data_manager.get_movie(movie_id)

    if request.method == 'POST':
        review_text = request.form.get("review_text")
        rating = request.form.get("rating")
        if not rating:
            flash('Rating is required', 'error')
            return render_template("add_review.html", user=user, movie = movie)
        try:
            rating = float(rating)
            if rating < 1 or rating > 10:
                flash("Rating must be in between 1.0 to 10 !", "error")
                return render_template("add_review.html", user=user, movie=movie)

        except ValueError:
            flash("Rating must be a valid number", "error")
            return render_template("add_review.html", user=user, movie=movie)

        data_manager.add_review(user_id, movie_id, review_text, rating)
        flash("review added successfully", "success")
        return redirect(url_for('user_movies', user_id=user_id))

    return render_template("add_review.html", user=user, movie=movie)

if __name__ == "__main__":
    app.run(debug=True)
