# Spotify Librarian

Spotify Librarian is a Python script that watches your currently playing Spotify track and asks whether you want to save the song after you move to the next one.

When a song ends or you skip to another track, the script displays a terminal prompt with your Spotify playlists. Enter a playlist number to add the previous song to that playlist, or skip it.

## Features

- Monitors the currently playing Spotify track.
- Prompts you when a track changes.
- Lists all of your Spotify playlists, including public and private playlists.
- Lets you choose the target playlist by number.
- Prevents duplicate additions by checking the selected playlist first.
- Checks every song in the selected playlist, including playlists with more than 100 songs.
- Tracks songs already prompted during the current session to avoid repeated prompts.
- Uses a cooldown to avoid prompt spam during rapid track changes.

## Requirements

- Python 3
- Spotify account
- Spotify Developer app credentials
- Python packages:
  - `spotipy`
  - `python-dotenv`

## Setup

Install dependencies:

```bash
pip install spotipy python-dotenv
```

Create a `.env` file in the project root:

```env
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

In your Spotify Developer Dashboard, make sure the same redirect URI is added to your app settings.

## Spotify Scopes

The script requests these scopes:

```text
user-read-currently-playing playlist-read-private playlist-modify-private playlist-modify-public
```

These allow the script to:

- Read the song currently playing.
- Read your private playlists.
- Add songs to private playlists.
- Add songs to public playlists.

## Usage

Run the script:

```bash
python3 main.py
```

On startup, the script fetches your playlists:

```text
📋 Fetching your playlists...
✅ Found 25 playlists
--- Librarian Active ---
```

When the current track changes, you will see a prompt like:

```text
============================================================
🎵 Save 'Song Name' by Artist?
============================================================

Your playlists:
  1. Playlist A
  2. Playlist B
  3. Playlist C

Enter playlist number (1-3), or press Enter to skip (auto-skip in 10 seconds)
```

Enter the playlist number and press Enter to save the song. Press Enter without typing a number, or wait 10 seconds, to skip.

## Duplicate Checking

Before adding a song, Spotify Librarian fetches all tracks from the selected playlist in pages of 100 songs.

This means duplicate checks work for long playlists, not just the first 100 songs.

If the song is already in the selected playlist, it will not be added again.

## Notes

- The script prompts for the previous song after a new song starts.
- Songs are only prompted once per script session.
- If you restart the script, session memory resets.
- The playlist list is fetched once at startup. Restart the script if you create or delete playlists while it is running.

## Troubleshooting

### Spotify API timeout

If you see a timeout error from `api.spotify.com`, it usually means Spotify or your network was slow to respond. Run the script again.

The Spotify client timeout is currently set to 10 seconds.

### Authentication issues

If authentication fails:

- Check your `.env` values.
- Confirm the redirect URI matches exactly in the Spotify Developer Dashboard.
- Re-run the script and complete the browser login flow if prompted.
