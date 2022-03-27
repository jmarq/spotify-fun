import dbus

# sending a command is pretty simple
# no need for starting a main loop or running async code
# since we are not "listening" for events. just firing off a method call and terminating.
try:
    bus = dbus.SessionBus()
    spotify_dbus = bus.get_object("org.mpris.MediaPlayer2.spotify", "/org/mpris/MediaPlayer2")
    player_iface = dbus.Interface(spotify_dbus, 'org.mpris.MediaPlayer2.Player')
    # Next is a method defined by the dbus interface for the Player. the iface object is a proxy and can call it.
    #  (for more info: run d-feet cli tool to explore interfaces)
    player_iface.Next()
    # similiary, OpenUri is a method for jumping to a specific song/album/etc
    # player_iface.OpenUri('spotify uri goes here')

except dbus.exceptions.DBusException as err:
    print(err)
    print('error')
    exit






