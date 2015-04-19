from settings import FLASK_SECRET_KEY, KNOWN_NUMBERS
import spotify

from flask import Flask, request, session
import twilio.twiml

app = Flask(__name__)
app.config.from_object(__name__)
app.secret_key = FLASK_SECRET_KEY


@app.route('/', methods=['GET', 'POST'])
def hello_monkey():
    """Respond with the number of text messages sent between two parties."""

    counter = session.get('counter', 0)

    # increment the counter
    counter += 1

    # Save the new counter value in the session
    session['counter'] = counter

    from_number = request.values.get('From')
    if from_number in KNOWN_NUMBERS:
        name = KNOWN_NUMBERS[from_number]
    else:
        name = "Monkey"

    message = "".join([name, " has messaged ", request.values.get('To'), " ",
                      str(counter), " times."])
    resp = twilio.twiml.Response()
    resp.sms(message)

    return str(resp)


@app.route('/twilio', methods=['POST'])
def process_twilio():
    text = request.values.get('Body').lower().strip()
    if text == 'playlists':
        session['new_song'] = False
        playlists = spotify.get_wejam_playlists()
        if not playlists:
            message = 'There are currently no playlists.'
        else:
            message = ','.join(playlists)
            message = 'Playlists: ' + message
    elif text.startswith('new'):
        session['new_song'] = False
        playlist_name = text[4:]
        try:
            spotify.create_playlist(playlist_name)
            session['playlist'] = playlist_name
            message = '{0} playlist created!'.format(playlist_name)
        except spotify.SpotifyException, e:
            message = str(e)
    elif text.startswith('choose'):
        session['new_song'] = False
        playlist_name = text[7:]
        if playlist_name in spotify.get_wejam_playlists():
            session['playlist'] = playlist_name
            message = 'Playlist successfully chosen!'
        else:
            message = 'Invalid playlist choice.'
    elif session.get('new_song', False):
        if text == '1' or text == '2' or text == '3':
            song_id = session['song_ids'][int(text) - 1]
            spotify.add_track(session['playlist'], song_id)
            session['new_song'] = False
            message = 'New song added to playlist!'
        elif text == 'none':
            session['new_song'] = False
            message = 'Adding a song was canceled.'
        else:
            message = 'Invalid song choice.\
                       Please type "1", "2", "3", or "none".'
    elif text.startswith('add'):
        if 'playlist' in session:
            playlist_name = session['playlist']
            query = text[4:]
            search_results = spotify.search(query)
            message = 'Please respond with the song # or none:\n'
            song_ids = []
            for i, song in enumerate(search_results):
                song_ids.append(song.id)
                message += '{0}) {1} by {2}\n'.format(i + 1,
                                                      song.title,
                                                      song.artist)
            session['song_ids'] = song_ids
            session['new_song'] = True
        else:
            message = 'Please use the "choose" command before "add".'
    elif text.startswith('tracks'):
        if 'playlist' in session:
            playlist_name = session['playlist']
            try:
                tracks = spotify.track_listing(playlist_name)
                message = ''
                for i, song in enumerate(tracks):
                    message += '{0}) {1}\n'.format(i + 1, song.title)
                if len(message) >= 1600:
                    message = message[:1595] + '...'
            except spotify.SpotifyException, e:
                message = str(e)
        else:
            message = 'Please use the "choose" command before "tracks".'
    else:
        message = "Unsupported command.  Valid commands are: "
        for command in ['playlists', 'new [playlist name]',
                        'choose [playlist name]', 'tracks',
                        'add [song search query]']:
            message += '"{0}", '.format(command)

    resp = twilio.twiml.Response()
    resp.sms(message)
    return str(resp)


@app.route('/callback', methods=['GET'])
def spotify_callback():
    return 'Authenticated successfully with Spotify!'


if __name__ == "__main__":
    app.run(debug=True)
