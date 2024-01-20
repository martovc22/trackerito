import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="7e10fc0f015f47518d86ac497d180326",
                                               client_secret="61c79d84f0fc41eab6241e3fdf7c6e15",
                                               redirect_uri="http://localhost:8080/",
                                               scope="user-library-read playlist-modify-public"
                                              ))

# get user id
user_id = sp.current_user()['id']

# get user's top tracks
tracks = sp.current_user_top_tracks(limit=500, time_range='long_term')['items']

# get track uris
track_uris = [track['uri'] for track in tracks]

# create playlist
playlist = sp.user_playlist_create(user=user_id, name='My Most Played Tracks', public=True)

# add tracks to playlist
sp.playlist_add_items(playlist_id=playlist['id'], items=track_uris)

print("Playlist created successfully.")