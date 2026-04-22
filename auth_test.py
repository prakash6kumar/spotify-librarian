import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

# Pull URI from .env file
scope = "user-read-currently-playing playlist-modify-public"
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')

# Initialize the Spotify through OAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    open_browser=False
))

# Attempt an authentication to get a token
try:
    user = sp.current_user()
    print(f"--- Authentication Successful! ---")
    print(f"Connected as: {user['display_name']}")
except Exception as e:
    print(f"Authentication failed: {e}")