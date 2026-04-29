import os
import time
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import select
import sys

load_dotenv()

# Setup the client
scope = "user-read-currently-playing playlist-read-private playlist-modify-private playlist-modify-public"
client_id = os.getenv('SPOTIPY_CLIENT_ID')
client_secret = os.getenv('SPOTIPY_CLIENT_SECRET')
redirect_uri = os.getenv('SPOTIPY_REDIRECT_URI')

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope
    ),
    requests_timeout=10  # Increase timeout to 10 seconds
)

def get_or_create_playlist(sp):
    playlist_name = "The Librarian"

    # Check existing playlists
    playlists = sp.current_user_playlists()

    for playlist in playlists['items']:
        if playlist['name'] == playlist_name:
            print(f"✅ Found existing playlist")
            return playlist['id']
    
    # If not found, create it
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
    print(f"\n{'='*60}")
    print(f"🎵 Save '{track_name}' by {artist_name}?")
    print(f"{'='*60}")
    print(f"Press 's' to SAVE or any other key to IGNORE (auto-ignore in 8 seconds)")
    
    # Wait for input with timeout
    i, o, e = select.select([sys.stdin], [], [], 8)
    
    if i:
        response = sys.stdin.readline().strip().lower()
        if response == 's':
            return True
    
    return False

def track_spotify():
    # Intialize playlist ID
    target_playlist_id = get_or_create_playlist(sp)

    prev_track_info = None
    active_id = None
    asked_track_ids = set()  # Track which songs we've already asked about
    last_popup_time = 0  # Track when we last showed a popup

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
                        
                        # Only ask if we haven't asked about this track before
                        if prev_track_info['id'] not in asked_track_ids:
                            # Check if enough time has passed since last popup (prevent spam)
                            current_time = time.time()
                            time_since_last_popup = current_time - last_popup_time
                            
                            if time_since_last_popup < 10:
                                print(f"⏸️  Cooldown active - skipping {prev_track_info['name']}")
                            else:
                                # Mark this track as asked
                                asked_track_ids.add(prev_track_info['id'])
                                
                                # Trigger popup for the previous song
                                user_wants_to_save = ask_to_save(prev_track_info['name'], prev_track_info['artist'])
                                last_popup_time = time.time()

                                if user_wants_to_save:
                                    # Fetch current items in the playlist
                                    results = sp.playlist_items(target_playlist_id)
                                    
                                    # Extract the IDs
                                    existing_ids = []
                                    for playlist_item in results['items']:
                                        if playlist_item and playlist_item.get('item') and playlist_item['item'].get('id'):
                                            existing_ids.append(playlist_item['item']['id'])

                                    # Add the song if not already in playlist
                                    if prev_track_info['id'] not in existing_ids:
                                        sp.playlist_add_items(target_playlist_id, [prev_track_info['id']])
                                        print(f"🚀 Added {prev_track_info['name']} to The Librarian")
                                    else:
                                        print(f"ℹ️  {prev_track_info['name']} already in playlist")

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