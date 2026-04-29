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

def get_all_playlists(sp):
    """Fetch all user playlists and return as a list"""
    all_playlists = []
    results = sp.current_user_playlists(limit=50)
    
    while results:
        all_playlists.extend(results['items'])
        if results['next']:
            results = sp.next(results)
        else:
            break
    
    return all_playlists

def ask_which_playlist(track_name, artist_name, playlists):
    """Ask user which playlist to add the song to"""
    print(f"\n{'='*60}")
    print(f"🎵 Save '{track_name}' by {artist_name}?")
    print(f"{'='*60}")
    print("\nYour playlists:")
    
    for idx, playlist in enumerate(playlists, 1):
        print(f"  {idx}. {playlist['name']}")
    
    print(f"\nEnter playlist number (1-{len(playlists)}), or press Enter to skip (auto-skip in 10 seconds)")
    
    # Wait for input with timeout
    i, o, e = select.select([sys.stdin], [], [], 10)
    
    if i:
        response = sys.stdin.readline().strip()
        if response.isdigit():
            playlist_num = int(response)
            if 1 <= playlist_num <= len(playlists):
                return playlist_num - 1  # Return 0-indexed position
    
    return None  # User skipped or invalid input

def track_spotify():
    # Fetch all user playlists at startup
    print("📋 Fetching your playlists...")
    playlists = get_all_playlists(sp)
    
    if not playlists:
        print("❌ No playlists found. Please create at least one playlist first.")
        return
    
    print(f"✅ Found {len(playlists)} playlists\n")

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
                                
                                # Ask which playlist to add to
                                playlist_idx = ask_which_playlist(prev_track_info['name'], prev_track_info['artist'], playlists)
                                last_popup_time = time.time()

                                if playlist_idx is not None:
                                    selected_playlist = playlists[playlist_idx]
                                    
                                    # Fetch ALL items in the selected playlist (with pagination)
                                    existing_ids = []
                                    results = sp.playlist_items(selected_playlist['id'], limit=100)
                                    
                                    while results:
                                        # Extract the IDs from current page
                                        for playlist_item in results['items']:
                                            if playlist_item and playlist_item.get('item') and playlist_item['item'].get('id'):
                                                existing_ids.append(playlist_item['item']['id'])
                                        
                                        # Get next page if available
                                        if results['next']:
                                            results = sp.next(results)
                                        else:
                                            break

                                    # Add the song if not already in playlist
                                    if prev_track_info['id'] not in existing_ids:
                                        sp.playlist_add_items(selected_playlist['id'], [prev_track_info['id']])
                                        print(f"🚀 Added {prev_track_info['name']} to {selected_playlist['name']}")
                                    else:
                                        print(f"ℹ️  {prev_track_info['name']} already in {selected_playlist['name']}")

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