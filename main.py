import os
import time
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

# Setup the client
scope = "user-read-currently-playing playlist-modify-public"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

def track_spotify():
    last_track_id = None

    print("--- Librarian Active ---")

    while True:
        try:
            # Ask Spotify what's playing right now
            current_track = sp.currently_playing()

            # Check if something is actually playing
            if current_track is not None and current_track['is_playing']:
                track_id = current_track['item']['id']
                track_name = current_track['item']['name']
                artist_name = current_track['item']['artists'][0]['name']

                # Check if song has changed, print new info if triggered
                if track_id != last_track_id:
                    print(f"🎵 Now Playing: {track_name} by {artist_name}")
                    last_track_id = track_id

            #Wait 5 seconds before asking again
            time.sleep(5)
            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    track_spotify()