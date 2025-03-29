import pytest
from app import app
import re
from datamanager.sqllite_data_magager import SQLiteDataManager


@pytest.fixture
def client():
    """Set up a test client for Flask."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_page(client):
    """Test if the home page loads correctly.""" #pass
    response = client.get("/")
    assert response.status_code == 200
    assert b"Welcome to MovieWeb" in response.data


def test_add_user(client):
    """Test adding a new user.""" #pass
    response = client.post("/add_user", data={"name": "Test User"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Test User" in response.data  # Check if user appears on the users list


def extract_user_id(response_data):
    """Extract the first user ID from response HTML."""

    match = re.search(r"/users/(\d+)/add_movie", response_data.decode())
    return match.group(1) if match else None


def test_add_movie(client):
    """Test adding a movie to a user.""" #pass

    # Step 1: Add a new test user
    response = client.post("/add_user", data={"name": "Test User"}, follow_redirects=True)
    assert response.status_code == 200

    # Step 2: Fetch the user list to get the newly created user's ID
    users_response = client.get("/users")
    assert users_response.status_code == 200
    user_id = extract_user_id(users_response.data)
    assert user_id is not None  # Ensure we extracted a valid user ID

    # Step 3: Add a movie for the user
    response = client.post(
        f"/users/{user_id}/add_movie",
        data={"name": "Inception", "director": "Christopher Nolan", "year": "2010", "rating": "8.8"},
        follow_redirects=True
    )

    assert response.status_code == 200  # Ensure movie is added
    assert b"Inception" in response.data


def test_update_movie(client):
    """Test updating a movie.""" #pass

    # Step 1: Add a test user
    response = client.post("/add_user", data={"name": "Test User"}, follow_redirects=True)
    assert response.status_code == 200

    # Step 2: Get the user ID
    users_response = client.get("/users")
    user_id = extract_user_id(users_response.data)

    # Step 3: Add a test movie
    response = client.post(
        f"/users/{user_id}/add_movie",
        data={"name": "Inception", "director": "Christopher Nolan", "year": "2010", "rating": "8.8"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Inception" in response.data

    # Step 4: Fetch the movie ID
    movies_response = client.get(f"/users/{user_id}")
    movie_id = extract_movie_id(movies_response.data)

    # Step 5: Update the movie
    response = client.post(
        f"/users/{user_id}/update_movie/{movie_id}",
        data={"name": "Interstellar", "director": "Christopher Nolan", "year": "2014", "rating": "8.6"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Interstellar" in response.data  # Check if update was successful


def extract_movie_id(response_data, movie_name="Inception"):
    """Extracts the movie ID for a specific movie from response HTML."""
    pattern = rf'/users/\d+/delete_movie/(\d+)".*?>Delete</a>\n\s*<\/li>\n\s*<li>\n\s*<strong> {movie_name}'
    match = re.search(pattern, response_data.decode(), re.IGNORECASE)
    return match.group(1) if match else None


def test_delete_movie(client):
    """Test deleting a movie."""

    # Step 1: Add a user
    response = client.post("/add_user", data={"name": "Test User"}, follow_redirects=True)
    assert response.status_code == 200

    # Step 2: Get user ID
    users_response = client.get("/users")
    user_id = extract_user_id(users_response.data)

    # Step 3: Add a movie
    response = client.post(
        f"/users/{user_id}/add_movie",
        data={"name": "Inception", "director": "Christopher Nolan", "year": "2010", "rating": "8.8"},
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Inception" in response.data

    # Step 4: Get the movie ID
    movies_response = client.get(f"/users/{user_id}")
    movie_id = extract_movie_id(movies_response.data)
    assert movie_id is not None, "Movie ID extraction failed!"

    # Step 5: Delete the movie
    response = client.post(f"/users/{user_id}/delete_movie/{movie_id}", follow_redirects=True)
    assert response.status_code == 200

    # Step 6: Re-fetch movies list and ensure "Inception" is removed
    updated_movies_response = client.get(f"/users/{user_id}")
    assert movie_id not in updated_movies_response.data.decode(), "Movie ID still present after deletion!"
    assert b"Inception" not in updated_movies_response.data, "Movie name still present after deletion!"

