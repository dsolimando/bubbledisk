import pygst
pygst.require("0.10")
import gst
import gobject
import gtk

from gst.extend.discoverer import Discoverer

class MetadataRetriever:
    songs = []
    current_song = None
    gui_model = None
    finished = None
    callback = None

    def __init__(self,songs,callback):
        self.songs = songs
        self.current_song = 0
        self.finished = False
        self.callback = callback

    def discover_songs_metadata(self):
        gobject.idle_add(self.__discover_one)

    def __discovered (self,discoverer,ismedia):

        ms = discoverer.audiolength / gst.MSECOND
        sec = ms / 1000
        ms = ms % 1000
        min = sec / 60
        sec = sec % 60

        try:
            artist = discoverer.tags["artist"]
        except KeyError:
            artist = ""

        try:
            title = discoverer.tags["title"]
        except KeyError:
            title = ""

        try:
            genre = discoverer.tags["genre"]
        except KeyError:
            genre = ""

        try:
            album = discoverer.tags["album"]
        except KeyError:
            album = ""

        self.callback (self.songs[self.current_song],
                           [str(self.current_song),
                           artist,
                           title,
                           "%02d:%02d:%03d"%(min,sec,ms),
                           self.songs[self.current_song].filename],
                       self.finished)

        self.songs[self.current_song].artist = artist
        self.songs[self.current_song].title = title
        self.songs[self.current_song].genre = genre
        self.songs[self.current_song].album = album
        self.songs[self.current_song].length = "%02d:%02d:%03d"%(min,sec,ms)
        self.songs[self.current_song].decodable = ismedia


        self.current_song += 1
        gobject.idle_add(self.__discover_one)

    def __discover_one (self):
        if len (self.songs) == self.current_song:
            self.finished = True
            self.callback(None,None,self.finished)
            return

        song = self.songs[self.current_song]
        discoverer = Discoverer (song.filename)
        discoverer.connect ("discovered",self.__discovered)
        discoverer.discover()

    def get_songs (self):
        return self.songs

class Song:

    """
    Song attributes
    """
    artist = None
    title = None
    filename = None
    genre = None
    length = None
    album = None
    decodable = None

    """
    gk.gdk.Pixbuf
    """
    cover = None