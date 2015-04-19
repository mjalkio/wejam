from settings import (ACCOUNT_SID, AUTH_TOKEN, FLASK_SECRET_KEY, KNOWN_NUMBERS,
                      TWILIO_NUMBER)
import spotify

from flask import Flask, request, session
from threading import Thread
from time import sleep
from twilio.rest import TwilioRestClient
import twilio.twiml

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = FLASK_SECRET_KEY

approving_song = False
song_score = 1
client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)


@app.route('/', methods=['GET'])
def index():
    return 'Nothing to see here!'


def list_playlists():
    session['new_song'] = False
    playlists = spotify.get_wejam_playlists()
    if not playlists:
        return 'There are currently no playlists.'
    else:
        message = ','.join(playlists)
        return 'Playlists: ' + message


def new_playlist(text):
    session['new_song'] = False
    playlist_name = text[4:]
    try:
        spotify.create_playlist(playlist_name)
        session['playlist'] = playlist_name
        return '{0} playlist created!'.format(playlist_name)
    except spotify.SpotifyException, e:
        return str(e)


def add_song(text):
    if 'playlist' in session:
        query = text[4:]
        search_results = spotify.search(query)
        message = 'Please respond with the song # or none:\n'
        session['songs'] = []
        for i, song in enumerate(search_results):
            message += '{0}) {1} by {2}\n'.format(i + 1,
                                                  song.title,
                                                  song.artist)
            session['songs'].append({'title': song.title,
                                     'artist': song.artist,
                                     'id': song.id})
        session['new_song'] = True
        return message
    else:
        return ('Please use the "choose" or "new" command before "add".')


def attempt_add_song(playlist, song):
    global approving_song
    global song_score
    body = '{0} by {1} has been suggested for {2}.\n'.format(song['title'],
                                                             song['artist'],
                                                             playlist)
    body += 'Please respond "upvote" or "downvote" in the next 30s.'
    for number in KNOWN_NUMBERS:
        client.messages.create(to=number, from_=TWILIO_NUMBER, body=body)
    approving_song = True
    sleep(20)
    if song_score >= 0:
        spotify.add_track(playlist, song['id'])
        body = '{0} by {1} has been added!'.format(song['title'],
                                                   song['artist'])
    else:
        body = '{0} by {1} was not approved.'.format(song['title'],
                                                     song['artist'])

    for number in KNOWN_NUMBERS:
        client.messages.create(to=number, from_=TWILIO_NUMBER, body=body)

    approving_song = False
    song_score = 1


def add_song_response(text):
    if text == '1' or text == '2' or text == '3':
        song = session['songs'][int(text) - 1]
        thread = Thread(target=attempt_add_song, args=(session['playlist'],
                                                       song))
        thread.start()
        session['new_song'] = False
        return 'Song will be approved for adding!'
    elif text == 'none':
        session['new_song'] = False
        return 'Adding a song was canceled.'
    else:
        return 'Invalid song choice. Please type "1", "2", "3", or "none".'


def playlist_tracks(text):
    if 'playlist' in session:
        playlist_name = session['playlist']
        try:
            tracks = spotify.track_listing(playlist_name)
            message = ''
            for i, song in enumerate(tracks):
                message += '{0}) {1}\n'.format(i + 1, song.title)
            if len(message) >= 1600:
                message = message[:1595] + '...'

            return message

        except spotify.SpotifyException, e:
            return str(e)
    else:
        return ('Please use the "choose" or "new" command before "tracks".')


@app.route('/twilio', methods=['POST'])
def process_twilio():
    text = request.values.get('Body').lower().strip()
    if approving_song:
        global song_score
        if text == 'upvote':
            song_score += 1
            message = 'Song has score {0}'.format(song_score)
        elif text == 'downvote':
            song_score -= 1
            message = 'Song has score {0}'.format(song_score)
        else:
            message = 'Song is being approved, can only upvote or downvote.'
    elif text == 'playlists':
        message = list_playlists()
    elif text.startswith('new'):
        message = new_playlist(text)
    elif text in spotify.get_wejam_playlists():
        session['new_song'] = False
        session['playlist'] = text
        message = 'Playlist successfully chosen!'
    elif session.get('new_song', False):
        message = add_song_response(text)
    elif text.startswith('add'):
        message = add_song(text)
    elif text.startswith('tracks'):
        message = playlist_tracks(text)
    # elif text == 'spam':
    #     for number in KNOWN_NUMBERS:
    #         if KNOWN_NUMBERS[number] != 'Michael Jalkio':
    #             with open('shrek.txt', 'r') as f:
    #                 for line in f:
    #                     client.messages.create(to=number,
    #                                            from_=TWILIO_NUMBER,
    #                                            body=line[:-1])
    #                 f.seek(0)
    else:
        message = "Unsupported command.  Valid commands are: "
        for command in ['playlists', 'new {playlist name}',
                        '{playlist name}', 'tracks',
                        'add {song search query}']:
            message += '"{0}", '.format(command)

    resp = twilio.twiml.Response()
    resp.sms(message)
    return str(resp)


@app.route('/callback', methods=['GET'])
def spotify_callback():
    return 'Authenticated successfully with Spotify!'


if __name__ == "__main__":
    app.run(debug=True)
