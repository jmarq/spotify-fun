import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib


load_dotenv()  # take environment variables from .env.

#credentials are configured using environment variables (loaded from dotenv)
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

# set up main app loop, telling it to use Glib
dbus_loop = DBusGMainLoop(set_as_default=True)
loop = GLib.MainLoop()

VALENCE_THRESHOLD = 0.5

def valence_by_id(id):
    song = spotify.audio_features([id])[0]
    valence = song['valence']
    return valence


# set up listener
try:
    bus = dbus.SessionBus(mainloop=dbus_loop)
    spotify_dbus = bus.get_object("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
    spotify_iface = dbus.Interface(spotify_dbus, 'org.freedesktop.DBus.Properties')
    player_iface = dbus.Interface(spotify_dbus, 'org.mpris.MediaPlayer2.Player')
    props = spotify_iface.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
    current_song = props['mpris:trackid']

    def handler(*args, **kwargs):
        global current_song
        props = args[1]['Metadata']
        ## get valence of song
        prev_song = current_song
        current_song = props['mpris:trackid']
        print(props['xesam:title'])
        if current_song != prev_song:
            song = spotify.audio_features([current_song])[0]
            valence = song['valence']
            print(valence)
            if valence < VALENCE_THRESHOLD:
                print("SAD SONG ALERT")
                # skip song
                player_iface.Next()
            else:
                print("song is happy enough, I'll allow it")

    spotify_iface.connect_to_signal("PropertiesChanged", handler, sender_keyword='sender')
except dbus.exceptions.DBusException as err:
    print(err)
    print('error')
    exit

# start listening
loop.run()





