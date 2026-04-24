import os
import time
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import subprocess

load_dotenv()

# Setup the client
scope = "user-read-currently-playing playlist-modify-public"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

def ask_to_save(track_name, artist_name):
    # AppleScript command to create a 10-second popup
    script = f'''
    display dialog "Save '{track_name}' by {artist_name} to your Librarian playlist?" ¬
    with title "Spotify Librarian" ¬
    buttons {{"Ignore", "Save to Playlist"}} ¬
    default button "Save to Playlist" ¬
    giving up after 10
    '''

    try:
        # Use subprocess to run the AppleScript from Python
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        
        # Check what the user clicked
        if "button returned:Save to Playlist" in result.stdout:
            return True
        return False
    except Exception as e:
        print(f"UI Error: {e}")
        return False

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

                    # Load popup to see if the user wants to save the song
                    user_wants_to_save = ask_to_save(track_name, artist_name)
                    
                    if user_wants_to_save:
                        print(f"✅ User confirmed: Saving {track_name}...")
                    else:
                        print(f"⏭️ User ignored or timed out.")

            #Wait 5 seconds before asking again
            time.sleep(5)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    track_spotify()