from settings import (SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET,
                      SPOTIFY_REDIRECT_URI, SPOTIFY_USER_ID)
import spotipy
from spotipy.client import SpotifyException
import spotipy.util as util

# A dict of playlists currently in We Jam
# key = playlist name, value = playlist id
wejam_playlists = {}


class Song:
    def __init__(self, title, artist, song_id=0):
        self.title = title
        self.artist = artist
        self.id = song_id


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
        raise spotipy.oauth2.SpotifyOauthError("Couldn't get token for user \
                                                {0}".format(SPOTIFY_USER_ID))


def get_wejam_playlists():
    return wejam_playlists.keys()


def create_playlist(playlist_name):
    sp = spotify()

    response = sp.user_playlist_create(SPOTIFY_USER_ID, playlist_name)

    if 'id' in response:
        playlist_id = response['id']
        wejam_playlists[playlist_name] = playlist_id
    else:
        raise SpotifyException(response['error']['status'],
                               'Could not create playlist.')


def track_listing(playlist_name):
    if playlist_name not in wejam_playlists:
        raise SpotifyException(400, -1,
                               '{0} is not currently managed by We Jam.'.
                               format(playlist_name))

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

        artists = artists[:-2].encode('utf-8')
        title = track['name'].encode('utf-8')
        track_list.append(Song(title, artists))

    return track_list


def search(query):
    sp = spotify()
    search_results = []
    response = sp.search(query, limit=3)
    for i in range(3):
        track = response['tracks']['items'][i]
        artists = ''
        for artist in track['artists']:
            artists += artist['name'] + ', '
        artists = artists[:-2].encode('utf-8')
        song_id = track['id'].encode('utf-8')
        title = track['name'].encode('utf-8')
        search_results.append(Song(title, artists, song_id))

    return search_results


def add_track(playlist_name, track_id):
    if playlist_name not in wejam_playlists:
        msg = '{0} is not currently managed by We Jam.'.format(playlist_name)
        raise spotipy.client.SpotifyException(400, -1, msg)

    sp = spotify()

    sp.user_playlist_add_tracks(SPOTIFY_USER_ID,
                                wejam_playlists[playlist_name],
                                ['spotify:track:' + track_id])
