# -*- coding: utf8 -*-
import gnomevfs
import nautilusburn
import os
import xml.dom.minidom
import xml.dom
import string

from re import match, compile

from xml.xpath import Evaluate
from xml.dom.ext.reader import PyExpat

from bd_exceptions.bubbledisk_exceptions import *



class device:
    block_device = ""
    interface = ""
    displayed_interface = ""
    type = ""
    vendor = ""
    identifikation = ""
    revision = ""
    driver = ""
    cd_speeds = []
    dvd_speeds = []
    interface_name = ""

    read_cdr = False
    write_cdr = False
    read_cdrw = False
    write_cdrw = False
    read_dvdrom = False
    read_dvdr = False
    read_dvdram = False
    write_dvdr = False
    write_dvdram = False
    test_writing = False

    support_buffer_underrun = False
    read_multisess = False
    play_audiocd = False
    buffered_size = 0
    supported_modes = ""
    burnfree = False
    gnomevfs_obj = None

    def print_friendly_devices_params (self):
        yesorno = {}
        dict = {}
        sorted_keys = []

        yesorno[True] = "yes"
        yesorno[False] = "no"

        dict ["System device name"] = self.block_device
        dict ["Device type"] = self.type
        dict ["Vendor"] = self.vendor
        dict ["Description"] = self.identifikation
        dict ["Revision"] = self.revision
        dict ["driver"] = self.driver
        dict ["Writes CDs"] = yesorno[self.write_cdr]
        dict ["Writes CD/RWs"] = yesorno[self.write_cdrw]
        dict ["Reads DVDs"] = yesorno[self.read_dvdrom]
        dict ["Write DVD-R(W)s"] = yesorno[self.write_dvdr]
        dict ["Buffer Size"] = self.buffered_size
        if self.write_dvdr:
            dict ["Max DVD write speed"] = self.dvd_speeds [0]
        if self.write_cdr:
            dict ["Max CD write speed"] = self.cd_speeds [0]

        dict ["Support burnfree"] = yesorno[self.burnfree]
        dict ["Write modes"] = self.supported_modes
        dict ["Buffer underrun free recording"] = yesorno[self.support_buffer_underrun]
        dict ["Support multisession"] = yesorno[self.read_multisess]
        dict ["Play audio CDs"] = yesorno [self.play_audiocd]

        sorted_keys.append("System device name")
        sorted_keys.append("Device type")
        sorted_keys.append("Vendor")
        sorted_keys.append("Description")
        sorted_keys.append("Revision")
        sorted_keys.append("driver")
        sorted_keys.append("Writes CDs")
        sorted_keys.append("Writes CD/RWs")
        sorted_keys.append("Reads DVDs")
        sorted_keys.append("Buffer Size")
        if self.write_dvdr:
            sorted_keys.append("Max DVD write speed")
        if self.write_cdr:
            sorted_keys.append("Max CD write speed")
        sorted_keys.append("Support burnfree")
        sorted_keys.append("Write modes")
        sorted_keys.append("Buffer underrun free recording")
        sorted_keys.append("Support multisession")
        sorted_keys.append("Play audio CDs")


        return sorted_keys,dict



class bubble_device_manager:
    # Liste des devices type CD/DVD
    devices = {}
    # Liste des graveurs
    writers = []
    # Listes des desvices et de leurs caractéristiques
    device_features = {}
    # Lisete des readers de type CD/DVD
    readers = {}

    # graveur séléctiionné par l'utilisateur
    used_device = 0

    # gnomevfs.Drive used as reader
    __current_reader = -1

    cmline_tool = None
    app_manager = None

    vfs_volume_monitor = None

    nautilusburn_drive_monitor = None

    def __init__(self,cmline_tool,app_manager):
        self.vfs_volume_monitor = gnomevfs.VolumeMonitor()
        self.vfs_volume_monitor.connect("drive-connected",self.__drive_connected)
        self.vfs_volume_monitor.connect("drive-disconnected",self.__drive_disconnected)
        self.vfs_volume_monitor.connect('volume-mounted',self.__device_mounted)
        self.vfs_volume_monitor.connect('volume-unmounted',self.__device_unmounted)
        self.cmline_tool = cmline_tool
        self.app_manager = app_manager
        self.nautilusburn_drive_monitor = nautilusburn.get_drive_monitor()
        self.search_devices ()

        for writer in self.writers:
        	self.device_features[writer.get_device()] = self.check_drive_features(writer.get_device())

    def __cb_mounting(self,succeeded,error,details):
        pass

    def __cb_eject(self,succeeded,error,details):
        pass

    def __drive_connected (self,vmc,drive):
        print "drive connected"
        self.devices[drive.get_device_path()] = drive
        self.writers = self.get_writers()

    def __drive_disconnected (self,vmc,drive):
        print "drive disconnected"
        del self.devices[drive.get_device_path()]
        self.writers = self.get_writers()

    def __device_mounted(self,vmc,volume):
        print "device mounted"
        self.devices[volume.get_device_path()] = volume.get_drive()
        print volume.get_drive().is_mounted()

    def __device_unmounted(self,vmc,volume):
        print "device unmounted"
        self.devices[volume.get_device_path()] = volume.get_drive()
        print volume.get_drive().is_mounted()

    def search_devices(self):
        self.devices = self.get_disk_devices()
        self.writers = self.get_writers()
        self.readers = self.get_readers()

        if len(self.writers) != 0:
            self.used_device = 0
        else:
            self.used_device = -1

        self.__current_reader = self.devices.values()[0]

    def get_current_writer (self):
        if self.used_device == -1:
            raise NoWriterFoundError
        else:
            return self.writers[self.used_device]

    def get_current_writer_as_gnomevfs_drive (self):
        if self.used_device == -1:
            raise NoWriterFoundError
        else:
            return self.get_gnomevfs_drive(self.writers[self.used_device])

    def get_current_writer_display_name (self):
        return self.devices[self.get_current_writer().get_device()].get_display_name()

    def get_current_reader (self):
        if self.__current_reader == None:
            raise NoReaderFoundError
        else:
            return self.__current_reader

    # Transforms nautilusburn Drive into gnomevfs Drive
    def get_gnomevfs_drive (self,nautilus_drive):
        return self.devices[nautilus_drive.get_device()]

    # Return a list of nautilisburn NautilusBurnDrive objects
    def get_writers(self):
        return self.nautilusburn_drive_monitor.get_recorder_drives()

    # Return a list of Device objects
    def get_readers(self):
        readers = {}
        found = False

        for dev in self.devices.keys():
            for writer in self.writers:
                if dev == writer.get_device():
                    found = True
                    break
            if not found:
                readers [dev] = self.devices [dev]

        return readers

    # Return a hash of gnomevfs drives objects with block device filename as key
    # TODO: replace with nautilusburn get_drives() implementation
    def get_disk_devices (self):
        connected_drives = self.vfs_volume_monitor.get_connected_drives()

        disk_devices = {}
        for drive in connected_drives:
            if drive.get_device_type() == gnomevfs.DEVICE_TYPE_CDROM:
                print drive.get_activation_uri()
                print drive.get_id()
                disk_devices[drive.get_device_path()] = drive
        return disk_devices

    def mount_device (self,device_path):
        self.devices[device_path].mount(self.__cb_mounting)

    def mount_current_writer (self):
        self.devices[self.get_current_writer().get_device()].mount(self.__cb_mounting)

    def unmount_current_writer (self):
        self.get_current_writer().unmount()

    def is_current_writer_mounted(self):
        return self.devices[self.get_current_writer().get_device()].is_mounted()

    def is_current_reader_drive_mounted (self):
        return self.__current_reader.is_mounted()

    def unmont_current_reader_drive (self):
        self.__current_reader.unmount()

    def get_current_writer_mount_point (self):
        print self.devices[self.get_current_writer().get_device()].get_device_path()
        return self.devices[self.get_current_writer().get_device()].get_mounted_volumes()[0].get_activation_uri().split("file://")[1]

    def eject_disk (self):
        self.get_current_writer().eject()

    def eject_reader (self):
        self.get_current_reader().eject(self.__cb_eject)

    def media_in_current_writer(self):
        if self.get_current_writer().get_media_type() == nautilusburn.MEDIA_TYPE_ERROR:
            raise NoMediaInDeviceError
        else:
            return True

#===============================================================================
#    Params:
#        device: natulisburn drive object
#    Return:
#         list of features in bubbledisk device object
#===============================================================================
    def get_drive_features (self,drive_path):
		return self.device_features[drive_path]

#===============================================================================
#    Params:
#        device: natulisburn drive object
#    Return:
#         list of features in bubbledisk device object
#===============================================================================
    def check_drive_features (self,drive_path):
        device_inst = device()

        name,cdrecord_cmd,version = self.app_manager.get_application_infos ("cdrecord")

        if not((self.get_current_writer().get_media_type_full()[2] == 1 and self.is_current_writer_mounted()) or not self.is_current_writer_mounted()):
            self.unmount_current_writer()

        cmd_result = self.cmline_tool.execute (cdrecord_cmd,"  dev="+drive_path+" -checkdrive -prcap")
        cmd_result2 = self.cmline_tool.execute (cdrecord_cmd,"  dev="+drive_path+" -checkdrive")

        device_inst.block_device = drive_path
        # Transform symlinks to real path for gnomevfs compatibility
        head,tail = os.path.split(device_inst.block_device)
        finfo = gnomevfs.get_file_info(gnomevfs.get_uri_from_local_path(device_inst.block_device))
        if finfo.type == gnomevfs.FILE_TYPE_SYMBOLIC_LINK:
            device_inst.block_device = head+os.path.sep+finfo.symlink_name

        write_speeds = self.get_write_speeds (cmd_result)
        try:
            device_inst.cd_speeds = write_speeds[0]
            device_inst.dvd_speeds = write_speeds[1]
        except IndexError:
            device_inst.cd_speeds = [-1]
            device_inst.dvd_speeds = [-1]

        # Can the device read cdr?
        device_inst.read_cdr = self.does_read_cdr(cmd_result)

        # Can the device write cdr?
        device_inst.write_cdr = self.does_write_cdr(cmd_result)

        # Can the device read cdrw?
        device_inst.read_cdrw = self.does_read_cdrw(cmd_result)

        # Can the device write cdrw?
        device_inst.write_cdrw = self.does_write_cdrw(cmd_result)

        # Can the device read dvdrom?
        device_inst.read_dvdrom = self.does_read_dvdrom (cmd_result)

        # Can the device read dvdr?
        device_inst.read_dvdr = self.does_read_dvdr (cmd_result)

        # Can the device write dvdr?
        device_inst.write_dvdr = self.does_write_dvdr (cmd_result)

        # Can the device read dvdram?
        device_inst.read_dvdram = self.does_read_dvdram (cmd_result)

        # Can the device write dvdram?
        device_inst.write_dvdram = self.does_write_dvdram (cmd_result)

        # Does the device support test writing?
        device_inst.test_writing = self.does_support_test_writing (cmd_result)

        # Does the device support buffer underrun?
        device_inst.support_buffer_underrun = self.does_support_buffer_underrun (cmd_result)

        # Does the device support multisession read?
        device_inst.read_multisess = self.does_support_read_multisess (cmd_result)

        # Does the device play audio cds?
        device_inst.play_audiocd = self.does_play_audio_cd (cmd_result)
        device_inst.buffered_size = self.get_buffered_size(cmd_result)
        device_inst.type = self.get_device_type (cmd_result2)
        device_inst.vendor = self.get_device_vendor (cmd_result2)
        device_inst.identifikation = self.get_identification (cmd_result2)
        device_inst.revision = self.get_revision (cmd_result2)
        device_inst.driver = self.get_driver (cmd_result2)
        device_inst.supported_modes = self.get_supported_modes (cmd_result2)

        return device_inst
    def clean_value (self,value):
        if value[0] == "\'" and value [-1]  == "\'":
            return string.strip(value[1:-1])
        else:
            return value

    def get_write_speeds (self,cmd_result):
        regexp_speeds = compile(".*Write\ speed\ \#\ \d:\s+[\d\s]+kB\/s.*\(CD\s+(\d+)x\,\ DVD\s+(\d+)x.*")
        cd_speeds = []
        dvd_speeds = []
        for value in cmd_result:
            speeds_set_match = regexp_speeds.match(value)

            if speeds_set_match != None:
                cd_speeds.append(speeds_set_match.group(1))
                dvd_speeds.append(speeds_set_match.group(2))

        return (cd_speeds,dvd_speeds)

    def get_max_write_speed (self,cmd_result):
        regexp_speeds = compile(".*Maximum\ write\ speed:\ [\d\s]+kB\/s\s*\(CD\s+(\d+)x\,\ DVD\s+(\d+)x.*")
        cd_speed = 0
        dvd_speed = 0
        for value in cmd_result:
            speeds_set_match = regexp_speeds.match(value)

            if speeds_set_match != None:
                cd_speed = speeds_set_match.group(1)
                dvd_speed = speeds_set_match.group(2)

        return (cd_speed,dvd_speed)

    def does_read_cdr(self,cmd_result):
        regexp = compile ("(.*)\s*read\s*CD-R\smedia.*")
        for value in cmd_result:
            capacity = regexp.match (value)
            if capacity != None:
                if string.strip(capacity.group(1)) == "Does":
                    return True
                else:
                    return False

    def does_write_cdr(self,cmd_result):
        regexp = compile ("(.*)\s*write\s*CD-R\smedia.*")
        for value in cmd_result:
            capacity = regexp.match (value)
            if capacity != None:
                if string.strip(capacity.group(1)) == "Does":
                    return True
                else:
                    return False

    def does_read_cdrw(self,cmd_result):
        regexp = compile ("(.*)\s*read\s*CD-RW\smedia.*")
        for value in cmd_result:
            capacity = regexp.match (value)
            if capacity != None:
                if string.strip(capacity.group(1)) == "Does":
                    return True
                else:
                    return False

    def does_write_cdrw(self,cmd_result):
        regexp = compile ("(.*)\s*write\s*CD-RW\smedia.*")
        for value in cmd_result:
            capacity = regexp.match (value)
            if capacity != None:
                if string.strip(capacity.group(1)) == "Does":
                    return True
                else:
                    return False

    def does_read_dvdrom(self,cmd_result):
        regexp = compile ("(.*)\s*read\s*DVD-ROM\smedia.*")
        for value in cmd_result:
            capacity = regexp.match (value)
            if capacity != None:
                if string.strip(capacity.group(1)) == "Does":
                    return True
                else:
                    return False

    def does_read_dvdr (self,cmd_result):
        regexp = compile ("(.*)\s*read\s*DVD-R\smedia.*")
        for value in cmd_result:
            capacity = regexp.match (value)
            if capacity != None:
                if string.strip(capacity.group(1)) == "Does":
                    return True
                else:
                    return False

    def does_write_dvdr (self,cmd_result):
        regexp = compile ("(.*)\s*write\s*DVD-R\smedia.*")
        for value in cmd_result:
            capacity = regexp.match (value)
            if capacity != None:
                if string.strip(capacity.group(1)) == "Does":
                    return True
                else:
                    return False

    def does_write_dvdram (self,cmd_result):
        regexp = compile ("(.*)\s*write\s*DVD-RAM\smedia.*")
        for value in cmd_result:
            capacity = regexp.match (value)
            if capacity != None:
                if string.strip(capacity.group(1)) == "Does":
                    return True
                else:
                    return False

    def does_read_dvdram (self,cmd_result):
        regexp = compile ("(.*)\s*read\s*DVD-RAM\smedia.*")
        for value in cmd_result:
            capacity = regexp.match (value)
            if capacity != None:
                if string.strip(capacity.group(1)) == "Does":
                    return True
                else:
                    return False

    def does_support_test_writing (self,cmd_result):
        regexp = compile ("(.*)\s*support\s*test\swriting.*")
        for value in cmd_result:
            capacity = regexp.match (value)
            if capacity != None:
                if string.strip(capacity.group(1)) == "Does":
                    return True
                else:
                    return False

    def does_support_buffer_underrun (self,cmd_result):
        regexp = compile ("(.*)\s*support\sBuffer-Underrun-Free\srecording.*")
        for value in cmd_result:
            capacity = regexp.match (value)
            if capacity != None:
                if string.strip(capacity.group(1)) == "Does":
                    return True
                else:
                    return False

    def does_support_read_multisess (self,cmd_result):
        regexp = compile ("(.*)\s*read\smulti-session\sCDs.*")
        for value in cmd_result:
            capacity = regexp.match (value)
            if capacity != None:
                if string.strip(capacity.group(1)) == "Does":
                    return True
                else:
                    return False

    def does_play_audio_cd (self,cmd_result):
        regexp = compile ("(.*)\s*play\saudio\sCDs.*")
        for value in cmd_result:
            capacity = regexp.match (value)
            if capacity != None:
                if string.strip(capacity.group(1)) == "Does":
                    return True
                else:
                    return False

    def get_buffered_size (self,cmd_result):
        regexp = compile ("\s*Buffer\ssize\sin\sKB:\s(\d*).*")
        for value in cmd_result:
            capacity = regexp.match (value)
            if capacity != None:
                return self.clean_value(capacity.group(1))

    def get_device_type (self,cmd_result):
        regexp = compile ("Device\stype\s*:\s(.*).*")
        for value in cmd_result:
            capacity = regexp.match (value)
            if capacity != None:
                return self.clean_value(capacity.group(1))

    def get_device_vendor (self,cmd_result):
        regexp = compile ("Vendor_info\s*:\s(.*).*")
        for value in cmd_result:
            capacity = regexp.match (value)
            if capacity != None:
                return self.clean_value (capacity.group(1))

    def get_identification (self,cmd_result):
        regexp = compile ("Identification\s*:\s(.*).*")
        for value in cmd_result:
            capacity = regexp.match (value)
            if capacity != None:
                return self.clean_value (capacity.group(1))

    def get_revision (self,cmd_result):
        regexp = compile ("Revision\s*:\s(.*).*")
        for value in cmd_result:
            capacity = regexp.match (value)
            if capacity != None:
                return self.clean_value (capacity.group(1))

    def get_driver (self,cmd_result):
        regexp = compile ("Driver\sflags\s*:\s(.*).*")
        for value in cmd_result:
            capacity = regexp.match (value)
            if capacity != None:
                return self.clean_value (capacity.group(1))

    def get_supported_modes (self,cmd_result):
        regexp = compile ("Supported\smodes\s*:\s(.*).*")
        for value in cmd_result:
            capacity = regexp.match (value)
            if capacity != None:
                return self.clean_value (capacity.group(1))


