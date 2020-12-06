import pygst
pygst.require("0.10")
import gst
from constants.config import *


class AudioConvertor:

    __WAV_PCM_PARSE =("audio/x-raw-int, endianness=(int)1234, width=(int)16, "
                     "depth=(int)16, signed=(boolean)true, rate=(int)44100, "
                     "channels=(int)2")

    __running = False

    def __init__ (self, sink_format=WAV_FORMAT):
        self.sink_format = sink_format
        self.__running = False

    """
    Converts a given source element to wav format and sends it to sink element.

    To convert a media file to a wav using gst-launch:
    source ! decodebin ! audioconvert ! audioresample ! audioconvert ! wavenc
    """
    def convert_to_wav (self, source_location, sink_location):
        # sink element
        sink = gst.element_factory_make("filesink")
        sink.set_property("location", sink_location)

        # source element
        src = gst.element_factory_make("filesrc")
        src.set_property("location", source_location)

        self.bin = gst.parse_launch(
        "decodebin name=stw_decodebin ! audioconvert ! "
        "audioresample ! audioconvert ! %s ! wavenc name=stw_wavenc" % self.__WAV_PCM_PARSE
        )
        bus = self.bin.get_bus()
        bus.add_watch (self.__cb_gst_evnt)

        decoder = self.bin.get_by_name("stw_decodebin")
        encoder = self.bin.get_by_name("stw_wavenc")

        self.bin.add (src)
        self.bin.add (sink)

        src.link (decoder)
        encoder.link (sink)

        if  self.bin.set_state(gst.STATE_PLAYING):
            self.__running = True
        else:
            pass

    def query_position(self):
        "Returns a (position, duration) tuple"
        try:
            position, format = self.bin.query_position(gst.FORMAT_TIME)
        except:
            position = gst.CLOCK_TIME_NONE

        try:
            duration, format = self.bin.query_duration(gst.FORMAT_TIME)
        except:
            duration = gst.CLOCK_TIME_NONE

        return (position, duration)

    def __cb_gst_evnt(self,bus,message):
        if message.type == gst.MESSAGE_TAG:
            return True

        elif message.type == gst.MESSAGE_EOS:
            self.bin.set_state(gst.STATE_NULL)

            if self.callback != None:
                self.callback()

            self.__running = False
            return False

        elif message.type == gst.MESSAGE_ERROR:
            self.bin.set_state(gst.STATE_NULL)
            self.__running = False
            return False

        else:
            return True



    def convert (self, source_location, sink_location, callback):
        self.callback = callback
        if self.sink_format == WAV_FORMAT:
            self.convert_to_wav(source_location,sink_location)



