import os
import time
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import subprocess

load_dotenv()

# Setup the client
scope = "user-read-currently-playing playlist-read-private playlist-modify-private playlist-modify-public"
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope
))

def get_or_create_playlist(sp):
    playlist_name = "The Librarian"

    # 1. Get the current user's profile info
    user_profile = sp.current_user()
    user_id = user_profile['id']
    print(f"DEBUG: Attempting to check playlists for User ID: {user_id}")

    # 2. Check existing playlists
    playlists = sp.current_user_playlists()

    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            print(f"DEBUG: Found existing playlist: {playlist['id']}")
            return playlist['id']
    
    # 3. If not found, create it
    try:
        print(f"✨ Creating new playlist: {playlist_name}...")
        # Use the modern /me/playlists endpoint instead of /users/{user_id}/playlists
        payload = {
            "name": playlist_name,
            "public": False,
            "description": "Auto-curated by Spotify Librarian"
        }
        new_playlist = sp._post("me/playlists", payload=payload)
        return new_playlist['id']
    except Exception as e:
        print(f"CRITICAL ERROR during creation: {e}")
        raise e

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
    # Intialize playlist ID
    target_playlist_id = get_or_create_playlist(sp)

    prev_track_info = None
    active_id = None

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
                if track_id != active_id:
                    # Check if we have a song that just ended
                    if prev_track_info is not None:                       
                        print(f"🏁 Finished: {prev_track_info['name']}")
                        
                        # Trigger popup for the previous song
                        user_wants_to_save = ask_to_save(prev_track_info['name'], prev_track_info['artist'])

                        if user_wants_to_save:
                            print(f"✅ Saving to playlist: {prev_track_info['name']}")
    
                            # Fetch current items in the playlist
                            results = sp.playlist_items(target_playlist_id)
                            # Extract the IDs from the complex Spotify dictionary
                            existing_ids = []
                            for item in results['items']:
                                if item and item.get('track') and item['track'].get('id'):
                                    existing_ids.append(item['track']['id'])

                            # Add the song into the playlist if ID is not found
                            if prev_track_info['id'] not in existing_ids:
                                sp.playlist_add_items(target_playlist_id, [prev_track_info['id']])
                                print(f"🚀 Successfully added {prev_track_info['name']} to The Librarian.")
                            else:
                                print(f"ℹ️ {prev_track_info['name']} is already in The Librarian.")

                    # Update the info to the song that just started
                    print(f"🎧 Playing: {track_name} by {artist_name}")
                    
                    prev_track_info = {
                        'id': track_id,
                        'name': track_name,
                        'artist': artist_name
                    }
                    active_id = track_id

            # Wait 5 seconds before asking again
            time.sleep(5)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    track_spotify()