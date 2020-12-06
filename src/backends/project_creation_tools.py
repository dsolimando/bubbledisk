#/usr/bin/python

from tool_box import *
import os
import os.path
import string
import math
import tool_box
import bubblevfs
import time
import gnomevfs
import copy
import gobject
from bd_exceptions.bubbledisk_exceptions import *
from constants.config import *
from backends.audio.AudioConvertor import AudioConvertor
from pyro_threads import Threaded_writing

# abstract class for a burning project
class burning_project:
    base_dir = ""
    disk_size = 0
    name = ""
    file_system = "ISO 9660"

    def __init__(self,base_dir,disk_size):
        self.base_dir = base_dir
        self.disk_size = (int)(disk_size)

    def add_file (self,file):
        return

    def remove_file (self,file):
        return

    def finalize (self):
        return

class iso9660_project (burning_project):

    system_tools = None
    current_dir = ""
    current_size = 0
    oversized = False
    progbar_size = 0
    iso9660_tool = None
    vfs = None
    temp_dir = ""
    temp_dir_infos = None
    numtracks = 1
    cdrdao_tool = None
    dev_manager = None
    name = ""

    def __init__(self,base_dir,disk_size,progbar_size,iso9660_tool,cdrecord_tool,temp_dir,vfs,dev_manager,cdrdao_tool):
        burning_project.__init__(self,base_dir,disk_size)
        self.system_tools = Common_tools()
        self.current_dir = base_dir
        self.progbar_size = progbar_size
        self.iso9660_tool = copy.copy(iso9660_tool)
        self.burning_tool = copy.copy(cdrecord_tool)
        self.cdrdao_tool = cdrdao_tool
        self.temp_dir = temp_dir
        self.name = DATA_CD
        try:
            self.temp_dir_infos = gnomevfs.get_file_info(self.temp_dir)
        except gnomevfs.NotFoundError:
            gnomevfs.make_directory (self.temp_dir,0755)
            self.temp_dir_infos = gnomevfs.get_file_info(self.temp_dir)

        self.vfs = vfs
        self.dev_manager = dev_manager
        self.file_system = "ISO 9660"

    # copy the files in the current directory
    # params:
    #        files:    list containing the asbsolute paths to copy
    #
    def add_files (self,files,window = None):
        for file in files:
            # TODO: Travailler avec des exceptions
            if os.path.exists (file):
                # receives total amount of data copied in Ko
                copy_size = self.vfs.cp (file,self.current_dir,window=window)
                splitted = file.split("/")
                self.current_size += int(float(copy_size)/1024.)

                if self.current_size >= self.disk_size:
                    self.oversized = True

                return 1

    # delete the files in the current directory
    # params:
    #        files:    list containing the asbsolute paths to delete
    #
    def remove_files (self,files):
        for file in files:
            size_to_remove = self.vfs.rm (file)
            self.current_size = self.current_size - int(float(size_to_remove)/1024.)

            if self.current_size < self.disk_size:
                    self.oversized = False
        return 1

    def move_file (self,source,destination):
        self.vfs.mv (source,destination)

    def create_dir (self,dirname):
        self.vfs.mkdir (dirname,self.current_dir)

    def set_current_dir (self,dir):
        self.current_dir = dir

    def get_current_dir (self):
        return self.current_dir

    def get_base_dir (self):
        return self.base_dir

    def get_project_size (self):
        return self.current_size

    def get_used_percent (self):
        if not self.oversized:
            return (float)(self.current_size)/(float)(self.progbar_size)
        else:
            return 1.0

    def get_project_size_inM(self):
        return ("%d Mo" % math.ceil(float(self.current_size)/1024.))

    def get_file_infos(self,url):
#        file_size = self.vfs.get_file_size (url)
#        file_permission = self.vfs.get_file_permissions(url)
#        file_type = self.vfs.get_file_type (url)
#        file_target = self.vfs.get_target_file (url)
#        return (file_size,file_permission,file_type,file_target)
        return self.vfs.get_file_infos(url)

    def finalize (self,window=None):
       device_name = self.dev_manager.get_current_writer().get_device()
       command_to_execute = self.iso9660_tool.generate_command(self.vfs.generate_graftpoints(),self.temp_dir,device_name)

       if window != None:
           gobject.idle_add(window.begin_iso_notification)

       print command_to_execute
       self.system_tools.execute (command_to_execute,"",window)

       if self.burning_tool.simulation:
           if window != None:
               gobject.idle_add(window.begin_simulating_writing_notification)
           command_to_execute = self.burning_tool.generate_command(self.iso9660_tool.isofile_url,True)
           self.system_tools.execute (command_to_execute,"",window)

       if self.burning_tool.write:
           if window != None:
               window.overal_progress = 0
               gobject.idle_add(window.begin_writing_notification)
           command_to_execute = self.burning_tool.generate_command(self.iso9660_tool.isofile_url)

           disk_info = self.cdrdao_tool.get_disk_infos()

           if disk_info[1]["CD-R empty"] != "yes":
               if self.dev_manager.is_current_writer_mounted():
                   self.dev_manager.unmount_current_writer()

           self.system_tools.execute (command_to_execute,"",window)

    def import_session (self,window):
        mpoint = self.dev_manager.get_current_writer_mount_point()
        for file in gnomevfs.open_directory(mpoint):
            if file.name != "." and file.name != "..":
                if self.vfs.cp (mpoint+os.path.sep+file.name,self.base_dir,session="1",graftpoint="0",window=window):
                    self.current_size = self.current_size + file.size
                    if self.current_size >= self.disk_size:
                        self.oversized = True



class Blank_disk_project :
    blank_mode = ""
    speed = ""
    device = ""
    app_manager = None
    dev_manager = None
    system_tools = None
    cdrdao_tool = None

    def __init__ (self,app_manager,dev_manager,cdrdao_tool):
        self.app_manager = app_manager
        self.dev_manager = dev_manager
        self.system_tools = Common_tools ()
        self.cdrdao_tool = cdrdao_tool

    def set_blank_mode (self,blank_mode):
        if blank_mode == "Minimal":
            self.blank_mode = "fast"
        elif blank_mode == "Full":
            self.blank_mode = "all"

    def set_speed (self,speed):
        self.speed = speed

    def set_device (self,device):
        self.device = device

    def write (self,window = None):
        params = cdrecord.blank_disk (self.device,self.blank_mode,self.speed)
        name,cdrecord_url,version = self.app_manager.get_application_infos ("cdrecord")

        if self.dev_manager.media_in_current_writer():
            disk_info = self.cdrdao_tool.get_disk_infos()
            if disk_info[1]["CD-R empty"] != "yes":
                #self.dev_manager.unmount_current_writer()
                print "disk unmiunt"
                print params
            self.system_tools.execute (cdrecord_url,params,window)
        else:
            window.infos_treestore.set (iter,0,"Please insert a disk")


class Copy_cd_project (burning_project):
    disk_type = None
    device_manager = None
    app_manager = None
    cdrdao_tools = None
    config_handler = None
    readcd = None
    cdrecord = None
    system_tools = None

    on_the_fly = False
    writing_speed = -1
    buffer_underrun_protection = False
    write_speed_control = False
    ignore_write_errors = False
    delete_iso_image = False
    fasttoc = True
    simulate = False
    raw_mode = False
    useCDDB = True
    multisess = False
    iso_image = ""

    # reader block device file name
    reader_device = None
    reading_speed = -1
    ignore_read_errors = None

    DATA_DISK = 0
    AUDIO_DISK = 1
    EXTRA_DISK = 2
    MULTI_SESSION_DATA_DISK = 3

    type = None

    toc_file_location = None

    num_sessions = None


    def __init__ (self,system_tools,device_manager,app_manager,cdrdao,config_handler,readcd,cdrecord_tool):
        self.app_manager = app_manager
        self.device_manager = device_manager
        self.cdrdao_tools = cdrdao
        self.config_handler = config_handler
        self.readcd = readcd
        self.name = COPY_CD
        self.system_tools = system_tools
        self.iso_image = self.config_handler.get ("misc/tempdir")+os.path.sep+"image.iso"
        self.reading_speed = "Auto"
        self.writing_speed = "Auto"
        self.reader_device = self.device_manager.devices.keys()[0]
        self.ignore_read_errors = True
        self.cdrecord = cdrecord_tool

    def check_cd_type (self):
        self.type =  self.cdrdao_tools.get_CD_type()

    def copy_cdextra (self):
        pass

    def copy_multisess_disk (self):
        pass

    def copy_data_disk_on_the_fly (self,window=None):
        pass

    def read_data_disk (self,window=None):
        tmp_dir,file = Common_tools.split_file_path(self.iso_image)

        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)

        self.toc_file_location = tmp_dir+os.path.sep+str(int(10000000000*random.random()))+".toc"

        command_to_execute = self.cdrdao_tools.read_cd (self.reader_device,
                                                        self.raw_mode,
                                                        self.fasttoc,
                                                        self.iso_image,
                                                        self.toc_file_location,
                                                        self.reading_speed,
                                                        self.ignore_read_errors,
                                                        self.type == self.cdrdao_tools.AUDIO_DISK
                                                        )
        print command_to_execute
        self.system_tools.execute (command_to_execute,"",window)

    def read_multisess_data_disk (self,window=None):
        tmp_dir,file = Common_tools.split_file_path(self.iso_image)

        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)

        # Analyse disk
        keys, infos = self.cdrdao_tools.get_disk_infos()
        self.num_sessions = int (infos["Sessions"])
        tocs = self.cdrdao_tools.get_tocs_buffer()

        if window != None:
            window.set_num_session(self.num_sessions)
            gobject.idle_add(window.begin_copy_reading_disk_notification_multisess)

        # Chacks wether it's a TAO Mode disk
        tao_disk = self.readcd.is_tao_disk (tocs[0],self.reader_device)

        for i in range (self.num_sessions):

            if window != None:
                # If process was stopped
                if window.is_aborted():
                    return

            # Compute sectors limits
            first_track = tocs[i].tracks[0]
            last_track = tocs[i].tracks[-1]

            sector_end = int(last_track.file_start_sectors) + int(last_track.file_length_sectors)
            sector_first = first_track.file_start_sectors

            if window != None:
                window.set_current_session_copied(i+1)
                window.set_current_session_size(int(last_track.file_length_sectors))
                window.set_current_session_first_sector(int(sector_first))

            # TAO Disk adjustment
            if tao_disk:
                sector_end -=2

            command_to_execute = self.readcd.read_session (self.reader_device,
                                                          sector_first,
                                                          sector_end,
                                                          self.raw_mode,
                                                          self.iso_image+str(i),
                                                          self.reading_speed,
                                                          self.ignore_read_errors
                                                          )
            print command_to_execute
            self.system_tools.execute (command_to_execute,"",window)

    def write_data_disk (self,window=None):
        self.cdrdao_tools.write_speed = self.writing_speed
        command_to_execute = self.cdrdao_tools.write_cd (self.buffer_underrun_protection,
                                                         self.write_speed_control,
                                                         self.ignore_write_errors,
                                                         not self.delete_iso_image,
                                                         self.config_handler.get ("writing/overburning"),
                                                         self.config_handler.get ("writing/eject"),
                                                         self.toc_file_location)
        print command_to_execute
        self.system_tools.execute (command_to_execute,"",window)

    def write_multisess_data_disk (self,window=None):

        for i in range (self.num_sessions):
            # GUI Aspect
            if window != None:
                window.set_current_session_copied(i+1)

            if i == self.num_sessions-1:
                eject = self.config_handler.get ("writing/eject")
                multisess = self.multisess
            else:
                eject = False
                multisess = True

            command_to_execute = self.cdrecord.write_iso (self.iso_image+str(i),
                                                       self.writing_speed,
                                                       True,
                                                       self.config_handler.get ("writing/overburning"),
                                                       eject)

            print command_to_execute
            self.system_tools.execute (command_to_execute,"",window)

class AudioCdProject (burning_project):
    """
    Backends
    """
    system_tools = None
    device_manager = None
    app_manager = None
    config_handler = None
    burning_tool = None

    # List of Song objects
    songs = []
    # Current project size in seconds
    current_size = 0

    # Disk Toc
    toc = None

    # 80 min Disk
    total_size = 4800000

    audio_convertor = None

    name = "Audio CD Project"


    UPDATE_INTERVAL = 500

    current_selected_song_index = -1


    def __init__ (self,system_tools,device_manager,app_manager,config_handler,burning_tool):
        self.system_tools = system_tools
        self.device_manager = device_manager
        self.app_manager = app_manager
        self.audio_convertor = AudioConvertor()
        self.config_handler = config_handler

        self.toc = Disk_toc()
        self.toc.set_audio_nature()
        self.toc.languages_map.append(9) #English by default

        cd_text = Cd_text()
        cd_text.global_section = True
        self.toc.global_cd_text.append(cd_text)
        self.burning_tool = burning_tool

    def get_current_selected_song (self):
        return self.songs[self.current_selected_song_index]

    def get_current_selected_track (self):
        return self.toc.tracks[self.current_selected_song_index]

    def add_song (self,song):
        self.songs.append (song)

    def add_songs (self,songs):
        self.songs += songs

    def remove_song (self,index):
        m,s,ms = self.songs[index].length.split(":")
        self.current_size -= int(ms)+1000*int(s)+60000*int(m)
        del self.songs[index]

    def get_num_songs (self):
        return len(self.songs)

    def get_current_size (self):
        return self.current_size

    def get_current_size_no_dimension (self):
        return float(self.current_size)/self.total_size

    def get_current_size_in_Min_Sec (self):
        return Common_tools.milli_to_time(self.current_size)

    def get_free_space_in_Min_Sec (self):
        return Common_tools.milli_to_time(self.total_size - self.current_size)

    def get_disk_size (self):
        return self.total_size

    def get_disk_size_in_Min (self):
        return Common_tools.milli_to_time(self.total_size)[0]

    def get_songs (self):
        return self.songs

    def convert (self, window = None):
        if window != None:
            self.window = window
            # Init audio Conversion window state
            window.init_for_convertion()
            window.num_tracks = self.get_num_songs()
            self.update_id = gobject.timeout_add(
                                                 self.UPDATE_INTERVAL,
                                                 self.cb_update_window)
            self.stop_update_window = False

        self.i = 0

        self.toc.tracks[self.i].filename = self.config_handler.get("misc/tempdir")+os.path.sep+"song_%d.wav"%self.i
        self.audio_convertor.convert(self.songs[self.i].filename, self.config_handler.get("misc/tempdir")+os.path.sep+"song_%d.wav"%self.i,self.convert_next_song)


    def convert_next_song (self):
        self.i+=1
        if self.window != None:
            try:
                self.window.update_convertion_state (self.i,self.get_num_songs(),1,self.songs[self.i].title)
            except IndexError:
                self.window.update_convertion_state (self.i,self.get_num_songs(),1,"")

        if self.i < self.get_num_songs():

            print "converting song %d"%self.i
            self.toc.tracks[self.i].filename = self.config_handler.get("misc/tempdir")+os.path.sep+"song_%d.wav"%self.i
            self.audio_convertor.convert(self.songs[self.i].filename, self.config_handler.get("misc/tempdir")+os.path.sep+"song_%d.wav"%self.i,self.convert_next_song)

        else:
            if self.window != None:
                self.stop_update_window = True
            writing_thread = Threaded_writing (self,self.window)
            writing_thread.start()


    def finalize (self,window):

        tmpFilename = self.config_handler.get("misc/tempdir")+"/toc.txt"
        fd = open(tmpFilename,"w")
        fd.write(self.toc.to_string())
        fd.close()

        command = self.burning_tool.write_cd (
                                    self.config_handler.get("writing/bufferunderrun"),
                                    self.config_handler.get("writing/writespeedcontrol"),
                                    False,
                                    False,
                                    self.config_handler.get("writing/overburning"),
                                    self.config_handler.get("writing/eject"),
                                    self.config_handler.get("misc/tempdir")+"/toc.txt"
                                   )

        if window != None:
            window.init_for_writing()
            i = 0
            for song in self.songs:
                m,s,ms = song.length.split(":")
                window.track_lengths_in_msec[str(i+1)] = Common_tools.time_2_milliseconds(0, int(m), int(s), int(ms))
                i+=1
        self.system_tools.execute (command, "" , window)


    def cb_update_window (self):
        position,duration = self.audio_convertor.query_position();

        value = float(position) / duration
        try:
            self.window.update_convertion_state (self.i,self.get_num_songs(),value,self.songs[self.i].title)
        except IndexError:
            self.window.update_convertion_state (self.i,self.get_num_songs(),value,"")

        if not self.stop_update_window:
            return True
        else:
            # Stop the timeout!
            return False
