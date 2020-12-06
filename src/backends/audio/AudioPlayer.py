import pygst
pygst.require("0.10")
import gst


class AudioPlayer:

    gst_player=None
    playing = None
    uri = None
    curent_song_selected = None

    def __init__ (self):
        self.playing = False

        self.gst_player = gst.element_factory_make("playbin", "player")
        fakesink = gst.element_factory_make('fakesink', "my-fakesink")
        self.gst_player.set_property("video-sink", fakesink)
        bus = self.gst_player.get_bus()
        bus.enable_sync_message_emission()
        bus.add_signal_watch()
        bus.connect('message', self.on_message)

    def on_message(self, bus, message):
        t = message.type

        if t == gst.MESSAGE_ERROR:
            err, debug = message.parse_error()
            print "Error: %s" % err, debug
            self.playing = False

    def start (self,uri=""):
        print "init playing"
        if uri == "":
            if self.curent_song_selected == None:
                return
            else:
                uri = self.curent_song_selected.filename

        if uri != self.uri:
            print "playing an other song"
            self.gst_player.set_state(gst.STATE_NULL)

        self.uri = uri
        self.gst_player.set_property('uri', "file://"+uri)
        self.playing = True

        self.gst_player.set_state(gst.STATE_PLAYING)
        print "state play ok"

    def stop (self,uri=""):
        self.gst_player.set_property('uri', "file://"+uri)
        self.playing = False
        self.gst_player.set_state(gst.STATE_NULL)

    def pause (self,uri=""):
        if uri == "":
            self.gst_player.set_property('uri', "file://"+self.uri)

        self.gst_player.set_property('uri', "file://"+uri)
        self.playing = False
        self.gst_player.set_state(gst.STATE_PAUSED)
        print "state pause"

    def is_playing (self):
        return self.playing

    def set_current_song (self,song):
        self.curent_song_selected = song

    def get_current_song (self):
        return self.curent_song_selected

    def query_position(self):
        "Returns a (position, duration) tuple"
        try:
            position, format = self.gst_player.query_position(gst.FORMAT_TIME)
        except:
            position = gst.CLOCK_TIME_NONE

        try:
            duration, format = self.gst_player.query_duration(gst.FORMAT_TIME)
        except:
            duration = gst.CLOCK_TIME_NONE

        return (position, duration)

    def seek(self, location):
        """
        @param location: time to seek to, in nanoseconds
        """
        gst.debug("seeking to %r" % location)
        event = gst.event_new_seek(1.0, gst.FORMAT_TIME,
            gst.SEEK_FLAG_FLUSH | gst.SEEK_FLAG_ACCURATE,
            gst.SEEK_TYPE_SET, location,
            gst.SEEK_TYPE_NONE, 0)

        res = self.gst_player.send_event(event)
        if res:
            gst.info("setting new stream time to 0")
            self.gst_player.set_new_stream_time(0L)
        else:
            gst.error("seek to %r failed" % location)

