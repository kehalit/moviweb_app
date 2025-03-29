# Movie_web_App

This is a Flask-based web application that allows users to manage their movie collections. The app integrates with the OMDb API to automatically fetch movie details, 
including title, director, year, and IMDb rating, review.

## Features
- **User Management**: Create, view, and delete users.
- **Movie Management**: Add, update, and delete movies in a user's collection.
- **OMDb API Integration**: Fetches movie details such as title, director, year, and rating.
- **Error Handling**: Custom error pages for 404 (Not Found) and 500 (Internal Server Error).

## Requirements
- Python 3.6+
- Flask
- SQLAlchemy
- OMDb API Key

## Setup Instructions
1. Clone the repository:
   git clone <repository-url>
2. Install the required dependencies:
   pip install -r requirements.txt
3. Set up your environment variables:
   - FLASK_SECRET_KEY: Secret key for session management.
   - OMDB_API_KEY: Your OMDb API key
4. Run the app:
     flask run
   
## Database
The app uses SQLite to store user and movie data locally.

 
