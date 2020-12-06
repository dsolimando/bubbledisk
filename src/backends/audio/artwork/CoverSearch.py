from Coroutine import *
from Loader import *
from AmazonCoverArtSearch import *

class CoverSearch:

    cache = None

    def __init__ (self):
        self.loader = Loader()
        self.engine = AmazonCoverArtSearch(Loader())
        self.song = None
        self.cache = {}

    def get_pixbuf (self, song, callback):
        self.song = song

        artist = song.artist
        album = song.album
        # replace quote characters
        # don't replace single quote: could be important punctuation
        for char in ["\""]:
            artist = artist.replace (char, '')
            album = album.replace (char, '')

        try:
            pixbuf = self.cache[artist][album]
            print "in cache"
            callback (pixbuf,self.song)

        except KeyError:
            Coroutine (self.image_search, artist, album, callback).begin ()

    def image_search (self,plexer,artist,album,callback):

        plexer.clear ()
        self.engine.search (artist,album, plexer.send ())

        while True:
            yield None

            try:
                _, (engine , results) = plexer.receive ()
            except ValueError:
                break

            if not results:
                break

            for url in engine.get_best_match_urls (results):

                yield self.loader.get_url (str (url), plexer.send ())
                data_tuple = plexer.receive ()

                try:
                    _, (data, ) = data_tuple
                except ValueError:
                    try:
                        (data, ) = data_tuple
                    except ValueError:
                        continue

                pixbuf = self.image_data_load (data)

                # Save pixbuf in cache
                try:
                    self.cache[artist][album] = pixbuf
                except KeyError:
                    self.cache[artist] = {}
                    self.cache[artist][album] = pixbuf

                if pixbuf:
                    callback (pixbuf,self.song)

    def image_data_load (self, data):
        if data :
            pbl = gtk.gdk.PixbufLoader ()

            try:
                if pbl.write (data) and pbl.close ():
                        return pbl.get_pixbuf ()
            except gobject.GError:
                pass

        return None