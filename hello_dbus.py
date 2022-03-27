import dbus

# print properties of currently playing track in spotify linux player
# (NOTE: this is for linux systems running dbus for cross application communication)
try:
    bus = dbus.SessionBus()
    spotify_bus = bus.get_object("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
    spotify_iface = dbus.Interface(spotify_bus, 'org.freedesktop.DBus.Properties')
    props = spotify_iface.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
    print(props)
except dbus.exceptions.DBusException:
	exit
