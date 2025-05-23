import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from datamanager.sqllite_data_magager import SQLiteDataManager
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException
from api import api, init_data_manager


# Initialize the Flask app
app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
data_manager = SQLiteDataManager(app)
init_data_manager(data_manager)
app.register_blueprint(api, url_prefix='/api')


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


@app.route("/users/<int:user_id>/add_movie", methods=["GET", "POST"])
def add_movie(user_id):
    """
    Handle adding a new movie for a specific user.

    - If accessed via GET: Displays the movie addition form.
    - If accessed via POST: Retrieves movie details from OMDb and adds the movie.

    Args:
        user_id (int): The ID of the user adding the movie.

    Returns:
        - Renders add_movie.html for GET requests.
        - Redirects to the user's movie list after a successful addition.
        - Re-renders the form with an error message if the movie is not found.
    """
    user = data_manager.get_user(user_id)  # Fetch user from database

    if not user:
        flash("❌ User not found!", "error")
        return redirect(url_for("home"))

    if request.method == "GET":
        session.pop('_flashes', None)

    if request.method == "POST":
        movie_name = request.form.get("movie_name")

        if not movie_name:
            flash("❌ Please enter a movie name!", "error")
            return render_template("add_movie.html", user=user, user_id=user_id)

        new_movie = data_manager.add_movie(user_id, movie_name)

        if not new_movie:
            flash("❌ Movie not found in OMDb. Please check the name and try again.", "error")
            return render_template("add_movie.html", user=user, user_id=user_id)

        flash(f"✅ '{movie_name}' added successfully!", "success")
        return redirect(url_for("user_movies", user_id=user_id))

    return render_template("add_movie.html", user=user, user_id=user_id)


@app.route('/users/<int:user_id>/update_movie/<int:movie_id>', methods=['GET', 'POST'])
def update_movie(user_id, movie_id):
    """
    Handles the movie update for a specific user.
    Users can only change the movie name, and the system fetches the latest details from OMDb API.
    """
    try:
        movie = data_manager.get_movie(movie_id)

        if not movie:
            flash(f"❌ Movie with ID {movie_id} not found.", "error")
            return redirect(url_for('user_movies', user_id=user_id))

        if request.method == 'POST':
            new_movie_name = request.form.get('movie_name')
            new_director = request.form.get('director')
            new_year = int(request.form.get('year'))
            new_rating = float(request.form.get('rating'))

            if not new_movie_name:
                flash("❌ Please enter a valid movie name!", "error")
                return render_template('update_movie.html', movie=movie, user_id=user_id)

            updated_movie = data_manager.update_movie(movie_id, new_movie_name, new_director, new_year, new_rating)
            if not updated_movie:
                flash("❌ Movie not found in OMDb. Please check the name and try again.", "error")
                return render_template('update_movie.html', movie=movie, user_id=user_id)

            flash(f"✅ '{new_movie_name}' updated successfully!", "success")
            return redirect(url_for('user_movies', user_id=user_id))

        return render_template('update_movie.html', movie=movie, user_id=user_id)

    except SQLAlchemyError as e:
        flash(f"❌ Database error: {str(e)}", "error")
        session.rollback()
    except Exception as e:
        flash(f"❌ Unexpected error: {str(e)}", "error")

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
    """
    Handles the addition of a review for a specific movie by a user.

    - GET request: Renders the review form for the user to submit a review for the movie.
    - POST request: Validates and processes the review submitted by the user.

    Parameters:
    user_id (int): The ID of the user adding the review.
    movie_id (int): The ID of the movie being reviewed.

    Returns:
    - Redirects to the movie's page if the review is added successfully.
    - Renders the review form if there are validation errors or if it's a GET request.
    """

    user = data_manager.get_user(user_id)
    movie = data_manager.get_movie(movie_id)

    if request.method == 'POST':
        review_text = request.form.get("review_text")
        rating = request.form.get("rating")

        # Check if rating is provided
        if not rating:
            flash('Rating is required', 'error')
            return render_template("add_review.html", user=user, movie=movie)

        try:
            # Validate rating value
            rating = float(rating)
            if rating < 1 or rating > 10:
                flash("Rating must be between 1.0 and 10.0!", "error")
                return render_template("add_review.html", user=user, movie=movie)
        except ValueError:
            flash("Rating must be a valid number", "error")
            return render_template("add_review.html", user=user, movie=movie)

        # Add the review to the database
        data_manager.add_review(user_id, movie_id, review_text, rating)
        flash("Review added successfully", "success")
        return redirect(url_for('user_movies', user_id=user_id))

    return render_template("add_review.html", user=user, movie=movie)


@app.route('/movies/<int:movie_id>/reviews', methods=['GET', 'POST'])
def view_reviews(movie_id):
    """Displays reviews for a movie and allows deletion."""
    movie = data_manager.get_movie(movie_id)

    if not movie:
        flash("Movie not found.", "error")
        return redirect(url_for('users_list'))

    if request.method == "POST":
        review_id = request.form.get("review_id")  # Get the review ID from form
        if review_id and data_manager.delete_review(int(review_id)):
            flash("Review deleted successfully!", "success")
        else:
            flash("Error deleting review.", "error")

        return redirect(url_for('view_reviews', movie_id=movie_id))  # Refresh page

    reviews = movie.reviews
    return render_template('movie_reviews.html', movie=movie, reviews=reviews)


if __name__ == "__main__":
    app.run(debug=True)
