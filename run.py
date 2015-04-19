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
        playlists = spotify.get_wejam_playlists()
        message = ','.join(playlists)
        message = 'Playlists: ' + message
    elif text.startswith('tracks'):
        playlist_name = text[7:]
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
        message = "Unsupported command.  Valid commands are: "
        for command in ['playlists', 'tracks [playlist name]']:
            message += '"{0}"'.format(command)
    resp = twilio.twiml.Response()
    resp.sms(message)
    return str(resp)


@app.route('/callback', methods=['GET'])
def spotify_callback():
    return 'Authenticated successfully with Spotify!'


if __name__ == "__main__":
    app.run(debug=True)
