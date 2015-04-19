from settings import (SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET,
                      SPOTIFY_REDIRECT_URI, SPOTIFY_USER_ID)
import spotipy
import spotipy.util as util

# A dict of playlists currently in We Jam
# key = playlist name, value = playlist id
wejam_playlists = {'Best of Disney': '2dKLJaJTw0YC8U5Rd9GXKy'}


class Song:
    def __init__(self, title, artist):
        self.title = title
        self.artist = artist


# Makes sure user is currently authenticated and returns Spotify object
def spotify():
    token = util.prompt_for_user_token(SPOTIFY_USER_ID,
                                       'playlist-modify-public',
                                       SPOTIFY_CLIENT_ID,
                                       SPOTIFY_CLIENT_SECRET,
                                       SPOTIFY_REDIRECT_URI)

    if token:
        return spotipy.Spotify(auth=token)
    else:
        print("Couldn't get token for user {0}".format(SPOTIFY_USER_ID))


def get_wejam_playlists():
    return wejam_playlists.keys()


def create_playlist(playlist_name):
    return []


def track_listing(playlist_name):
    if playlist_name not in wejam_playlists:
        return '{0} is not currently managed by We Jam.'

    sp = spotify()

    playlist_id = wejam_playlists[playlist_name]
    playlist = sp.user_playlist_tracks(SPOTIFY_USER_ID, playlist_id,
                                       fields='items(track(name, \
                                               artists(name)))',
                                       limit=None)

    track_list = []
    for item in playlist['items']:
        track = item['track']
        artists = ''
        for artist in track['artists']:
            artists += artist['name'] + ', '

        artists = artists[:-2]
        track_list.append(Song(track['name'], artists))

    return track_list
