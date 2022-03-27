import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import json
import dbus
from dbus.mainloop.glib import DBusGMainLoop
from gi.repository import GLib
from urllib.request import urlopen
from colorthief import ColorThief
import io
from phue import Bridge
from colour import Color

load_dotenv()  # take environment variables from .env.

MAX_HUE = 65535
MAX_SAT = 255
MAX_BRI = 255

# this is based on your Hue setup.
# which lights do you want to be affected?
# these are the indexes phue uses.
lights = [1,3,4,5]

#credentials are configured using environment variables (loaded from dotenv)
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())

def all_on(b):
    for light in lights:
        b.set_light(light, 'on', True)

def set_color(b, hex):
    color = hex
    color_c = Color(color)
    color_hsl = color_c.get_hsl()
    hue = color_hsl[0]*MAX_HUE
    sat = color_hsl[1]*MAX_SAT
    bri = color_hsl[2]*MAX_BRI

    for light in lights:
        b.set_light(light, 'hue', int(hue))
        b.set_light(light, 'sat', int(sat))
        b.set_light(light, 'bri', int(bri))


def handle_image(props, bridge):
    song = props['mpris:trackid']
    # print(song)
    track = spotify.track(song)
    image_url = track['album']['images'][0]['url']
    print(image_url)

    image_file = urlopen(image_url)
    image_bytes = io.BytesIO(image_file.read())
   
    color_thief = ColorThief(image_bytes)
    # returns rgb on a 0 -> 255 scale
    color = color_thief.get_color(quality=1)
    print('colorthief color')
    print(color)
    # map to 0 -> 255 to 0 -> 1, for usage of Color lib hex conversion
    c = Color(rgb=(color[0]/255.0, color[1]/255.0, color[2]/255.0))

    # as this has evolved, is this even necessary? maybe we just need to pass a Color to set_color?
    chex = c.hex
    print('hexed color')
    print(chex)
    set_color(bridge, chex)



# set up main app loop, telling it to use Glib
dbus_loop = DBusGMainLoop(set_as_default=True)
loop = GLib.MainLoop()

# connect to Hue bridge
b = Bridge('192.168.1.127')
b.connect()


def handler(*args, **kwargs):
    print("got signal")
    props = args[1]['Metadata']
    handle_image(props, b)


# set up listener
try:
    bus = dbus.SessionBus(mainloop=dbus_loop)
    spotify_dbus = bus.get_object("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
    spotify_iface = dbus.Interface(spotify_dbus, 'org.freedesktop.DBus.Properties')
    print(spotify_iface)
    spotify_iface.connect_to_signal("PropertiesChanged", handler, sender_keyword='sender')
except dbus.exceptions.DBusException as err:
    print(err)
    print('error')
    exit


# turn on the lights!
all_on(b)
# start listening
loop.run()





