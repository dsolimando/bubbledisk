import os
import os.path
import random
import gtk
import gobject
import string
import popen2

from bd_exceptions.bubbledisk_exceptions import *

from re import match, compile



class Common_tools:

    def execute (self,command,params,window=None,data_container=None):
        output = []
        stdout = "pas vide"

        # GUI Case
        if window != None:
            gobject.idle_add(window.show_window)

        #pipe = os.popen4 (command+" "+ params)
        process = popen2.Popen4 (command+" "+ params)

        if data_container != None:
            data_container.pid = process.pid

        if window != None:
            window.pid = process.pid

        while stdout != "":
            round = True
            while (round):
                stdout,round = self.read_output(process.fromchild)
                #stdout = pipe[1].readline()

                #stdout = string.strip (stdout)
                output.append(stdout)
                # GUI Case
                if window != None:
                    gobject.idle_add(window.update,stdout)

                if data_container !=None:
                    data_container.update(stdout)

        # GUI Case
#===============================================================================
#        if window != None:
#            gobject.idle_add(window.hide_window)
#===============================================================================

#        if (pipe[0] != None):
#            pipe[0].close()
#        if (pipe[1] != None):
#            pipe[1].close()

        os.wait()
#        del pipe
#        pipe = None
        return output

    def read_output (self,pipe):
        out = " "
        line = ""
        round = False
        while out != "\n" and out != "" and out!='\b':
                out = pipe.read(1)
                line = line + out
                if out == "\b":
                    temp = "toto"
                    while (temp == '\b'):
                        temp=pipe.read(1)
                    round = True
                    break
                if out == "\r":
                    round = True
                    break

        return line,round

    def get_file_size (self,file):
        if (os.path.isfile (file) or os.path.isdir (file)):
            regexp_size =  compile("(\d+)\s+")
            output = self.execute("du"," -sL '" + file+"'")

            for value in output:
                size_match = regexp_size.match(value)
                if size_match != None:
                    return int(size_match.group(0))

    def cut_symlink_copy_outpout (self, output):
        try:
            # Regexp engine initialisation
            regexp_file_copied = compile("(.*)(\s+)->(\s+)(.*)")
            regexp_trunc_url = compile("(/.*/)(.*)")

            processed_regexp =  regexp_file_copied.match(output)

            root_dir = processed_regexp.group(1)
            dest_dir = processed_regexp.group(4)

            root_dir_processed_regexp = regexp_trunc_url.match (root_dir[1:-1])

            root_pwd =  root_dir_processed_regexp.group(1)
            file_name = root_dir_processed_regexp.group(2)

            dest_dir_processed_regexp = regexp_trunc_url.match (dest_dir[1:-1])
            dest_pwd = dest_dir_processed_regexp.group(1)

            copy_infos = (file_name,root_pwd,dest_pwd)

        except AttributeError,error:
            copy_infos = ("","","")

        return copy_infos

    def count_numfiles (self,dir):
        i = 0
        for root, dirs, files in os.walk(dir):
            i = i + len(files) + len(dirs)

        return i

    def create_correct_path (self, dirs):
        path = ""
        for dir in dirs:
            path  += (dir+":")

        path = path.rstrip(":")
        return path

    def swap_paths (self,a,b,path):
        index_a = path.index (a)
        index_b = path.index (b)
        tmp = path[index_b]
        path[index_b] = path[index_a]
        path[index_a] = tmp

    def eject_disk (self):
        self.execute ("eject","")

    def get_session_num (self,data):
        c = compile("(\d*)\s.*")
        m = c.match(data)
        return m.group(1)

    def split_url (self,url):
        protocol,queue = url.split("://")
        hostname,port = queue.split(":")
        return (protocol,hostname,port)

    def time_2_seconds (h,m,s):
        return s+m*60+h*3600

    def time_2_milliseconds (h,m,s,ms):
        return ms+(1000*s)+(m*60000)+(h*3600000)

    def milli_to_time (value):
        milli = value %1000
        sec = value/1000

        if milli >=500:
            sec += 1

        reste = sec % 60
        min = sec/60

        return (min,reste,milli)

    def ko_2_msec (ko):
        return ko*6

    def split_file_path (path):
        splitted_path = path.split("/")

        return (path.rsplit(os.path.sep+splitted_path[-1])[0],splitted_path[-1])

    split_file_path = staticmethod (split_file_path)
    time_2_seconds = staticmethod(time_2_seconds)
    milli_to_time = staticmethod(milli_to_time)
    ko_2_msec = staticmethod(ko_2_msec)
    time_2_milliseconds = staticmethod(time_2_milliseconds)

class mkisofs:
    # Specifies a text string that will be written into the volume header.  This should  describe  the  application
    # that  will be on the disc.  There is space on the disc for 128 characters of information.
    #
    # In the gui this parameter stay in volume desc tab in the Burning Project Window
    application_id = "BubbledisK Burning Rom Version 0.0.1, 2005, Damien Solimando"

    allow_leading_dots = False

    # Allow  ISO9660  filenames  to  begin with a period.  Usually, a leading dot is replaced with an underscore in
    # order to maintain MS-DOS compatibility.  This violates the ISO9660 standard
    #
    # In the gui this parameter stay in Filesystem tab, in the advanced iso9660 treeview
    leading_dots = False

    # This options allows lower case characters to appear in iso9660 filenames.
    # This violates the ISO9660 standard
    #
    # In the gui this parameter stay in Filesystem tab, in the advanced iso9660 treeview
    allow_lowercase = False

    # This options allows more than one dot to appear in iso9660 filenames.
    # This violates the ISO9660 standard
    #
    # In the gui this parameter stay in Filesystem tab, in the advanced iso9660 treeview
    allow_multidot = False

    # Specifies  the  bibliographic  file name.  There is space on the disc for 37 characters of information.
    #
    # In the gui this parameter stay in volume desc tab in the Burning Project Window
    biblio = ""

    # Specifies the Copyright file name.  There is space on  the  disc
    # for  37  characters  of information
    #
    # In the gui this parameter stay in volume desc tab in the Burning Project Window
    copyright = ""

    # -d option in mkisofs command
    # Omit trailing period from files that do not have a period
    #
    # In the gui this parameter stay in Filesystem tab, in the advanced iso9660 treeview
    omit_trailing_period = False

    # Input  charset  that  defines  the characters used in local file names.
    #
    # In the gui this parameter stay in Filesystem tab, in the advanced parameters
    input_charset = "iso8859-1"

    # Set the iso9660 conformance level. Valid numbers are 1..3 and 4.
    #
    # In the gui this parameter stay in Filesystem tab, in the advanced parameters
    iso_level = "1"

    # -J option in mkisofs command
    # Generate Joliet directory records in addition to regular iso9660
    # file  names.   This is primarily useful when the discs are to be
    # used on Windows-NT or Windows-95 machines.
    #
    # In the gui this parameter stay in Filesystem tab
    gen_joliet = True

    # Allow  Joliet filenames to be up to 103 Unicode characters. This
    # breaks the Joliet specification
    #
    # In the gui this parameter stay in Filesystem tab, in the advanced iso9660 treeview
    joliet_long = False

    # -l option in mkisofs command
    # Allow  full  31 character filenames.  Normally the ISO9660 file-
    # name will be in an 8.3 format which is compatible  with  MS-DOS,
    # even  though  the  ISO9660 standard allows filenames of up to 31
    # characters.
    #
    # In the gui this parameter stay in Filesystem tab, in the advanced iso9660 treeview
    allow_31_char_fn = False

    #  Allow  37 chars in iso9660 filenames.  This option forces the -N
    #  option as the extra name space is taken from the space  reserved
    #  for ISO-9660 version numbers.
    #
    #  In the gui this parameter stay in Filesystem tab, in the advanced iso9660 treeview
    max_iso9660_filenames = False

    # -N option in mkisofs command
    # Omit version numbers from ISO9660 file names.
    #
    #  In the gui this parameter stay in Filesystem tab, in the advanced iso9660 treeview
    omit_version_number = False

    #  Do not include backup files files on the iso9660 filesystem.  If
    #  the  -no-bak option is specified, files that contain the charac-
    #  ters '~' or '#' or end in '.bak' will not be included
    #
    #  In the gui this parameter stay in Filesystem tab, in the advanced iso9660 treeview
    no_bak = False

    #  Specifies a text string that will be  written  into  the  volume
    #  header.   This  should describe the publisher of the CDROM, usu-
    #  ally with a mailing address and phone number.  There is space on
    #  the  disc for 128 characters of information.
    #
    # In the gui this parameter stay in volume desc tab in the Burning Project Window
    publisher = ""

    # -p option in mkisofs command
    # Specifies  a  text  string  that will be written into the volume
    # header.  This should describe the preparer of the CDROM, usually
    # with  a mailing address and phone number.  There is space on the
    # disc for 128 characters of information.
    #
    # In the gui this parameter stay in volume desc tab in the Burning Project Window
    preparer = "BubbledisK - Version 0.0.1"

    # -r option in mkisofs command
    # Generate SUSP and RR records using the Rock  Ridge  protocol  to
    # further describe the files on the iso9660 filesystem.
    #
    #  In the gui this parameter stay in Filesystem tab, in the advanced parameters
    gen_rock_ridge_ext = True

    # The   option  -relaxed-filenames  allows  ISO9660  filenames  to
    # include digits, upper case characters and all other 7 bit  ASCII
    # characters
    #
    #  In the gui this parameter stay in Filesystem tab, in the advanced iso9660 treeview
    relaxed_filenames = False

    # Specifies  the  system  ID.   There  is space on the disc for 32
    # characters of information.
    #
    #  In the gui this parameter stay in volume desc tab in the Burning Project Window
    sysid = "GNU/Linux"

    # -T option in mkisofs command
    #  Generate a file TRANS.TBL in each directory on the CDROM,  which
    #  can  be used on non-Rock Ridge capable systems to help establish
    #  the correct file names.  There is also  information  present  in
    #  the  file  that  indicates the major and minor numbers for block
    #  and character devices, and each symlink has the name of the link
    #  file given.
    #  In the gui this parameter stay in Filesystem tab, in the advanced iso9660 treeview
    gen_transbl = False

    # Hide the TRANS.TBL files from the Joliet tree.  These files usu-
    # ally don't make sense in the Joliet World as they list the  real
    # name  and  the ISO9660 name which may both be different from the
    # Joliet name.
    #
    # In the gui this parameter stay in Filesystem tab, in the advanced iso9660 treeview
    hide_joliet_trans_tbl = False

    # Include UDF support in the generated filesystem image.
    #
    # In the gui this parameter stay in Filesystem tab,
    udf = False

    # -U option in mkisofs command
    # Allows  "Untranslated"  filenames,  completely   violating   the
    # iso9660  standards  described  above.
    #
    # In the gui this parameter stay in Filesystem tab, in the advanced iso9660 treeview
    allow_untranslated_filenames = False

    #  Do  not  translate  the characters '#' and '~' which are invalid
    #  for iso9660 filenames.   These  characters  are  though  invalid
    #  often used by Microsoft systems.
    #
    #  In the gui this parameter stay in Filesystem tab, in the advanced iso9660 treeview
    no_iso_translate = False

    # -V option in mkisofs command
    # Specifies the volume ID (volume name or  label)  to  be  written
    # into  the master block.  There is space on the disc for 32 char-
    # acters of information.
    #
    # In the gui this parameter stay in volume desc tab in the Burning Project Window
    volume_id = "BubbledisK Data Project"

    # Specifies the volset ID.  There is space on  the  disc  for  128
    # characters  of  information.
    #
    # In the gui this parameter stay in volume desc tab in the Burning Project Window
    volset = ""

    app_man = None
    mkisofs_url = ""
    isofile_name = ""

    last_sess_start = ""
    next_sess_start = ""

    multisess = False


    def __init__(self,app_manager):
        self.app_man = app_manager
        name,self.mkisofs_url,version = self.app_man.get_application_infos ("mkisofs")
        self.publisher = ""

    def generate_command (self,gp,iso_creation_directory,device=None):
        command = self.mkisofs_url
        command = command + " -v "
        if self.application_id != "":
            command = command + " -A '"+self.application_id+"' \\\n"

        if self.biblio != "":
            command = command + " -biblio '" + self.biblio+"' \\\n"

        if self.copyright != "":
            command = command + " -copyright '"+ self.copyright+"' \\\n"

        if self.publisher != "":
            command = command + " -publisher '" + self.publisher+"' \\\n"

        if self.preparer != "":
            command = command + " -p '"+ self.preparer+"' \\\n"

        if self.sysid != "":
            command = command + " -sysid "+ self.sysid+" \\\n"

        if self.volume_id != "":
            command = command + " -V '"+ self.volume_id+"' \\\n"

        if self.volset != "":
            command = command + " -volset " + self.volset +" \\\n"

        if self.allow_untranslated_filenames:
            command = command  + " -d -l -N -allow-leading-dots -relaxed-filenames -allow-lowercase -allow-multidot -no-iso-translate -max-is9669-filenames"+" \\\n"
        else:
            if self.omit_trailing_period:
                command = command + " -d "+" \\\n"

            if self.allow_31_char_fn:
                command = command + " -l "+" \\\n"

            if self.omit_version_number:
                command = command + " -N "+" \\\n"

            if self.allow_leading_dots:
                command = command + " -allow-leading-dots "+" \\\n"

            if self.relaxed_filenames:
                command = command + " -relaxed-filenames "+" \\\n"

            if self.allow_lowercase:
                command = command + " -allow-lowercase "+" \\\n"

            if self.allow_multidot:
                command = command + " -allow-multitdot "+" \\\n"

            if self.no_iso_translate:
                command = command + " -no-iso-translate "+" \\\n"

            if self.max_iso9660_filenames:
                command = command + " -max-iso9660-filenames "+" \\\n"

        if self.gen_joliet:
            command = command + " -J -joliet-long "+" \\\n"

#===============================================================================
#            if self.joliet_long:
#                command = command + " -joliet-long "+" \\\n"
#===============================================================================

        if self.gen_rock_ridge_ext:
            command = command + " -R -hide-rr-moved "+" \\\n"

        if self.udf:
            command = command + " -udf "+" \\\n"

        if self.gen_transbl:
            command = command + " -T "+" \\\n"

            if self.hide_joliet_trans_tbl:
                command = command + " -hide-joliet-trans-tbl "+" \\\n"

        if self.multisess:
            command = command + " -C %s,%s -M %s "%(self.last_sess_start,self.next_sess_start,device)

        self.isofile_url = iso_creation_directory+"/project-"+str(int(10000000000*random.random()))+".iso"
        command = command + " -o  "+self.isofile_url+" \\\n"
        command = command + " -input-charset "+self.input_charset+" \\\n"
        command = command + " -iso-level "+self.iso_level+" \\\n"
        command = command + " -graft-points  \\\n"

        for gp_key in gp.keys():
            command = command + "'"+gp_key+"'='"+gp[gp_key]+ "' \\\n"
        return command

class burning_tool:
    multisess = "No multisession Disk"
    track_mode = "Auto"
    fixating = True
    simulation = False
    write = True
    write_method = "Disk at once"
    write_speed = "Auto"

class cdrecord (burning_tool):
    app_manager = None
    device_manager = None
    cdrecord_url = ""

    def __init__(self,app_manager,device_manager):
        self.app_man = app_manager
        self.device_manager = device_manager
        name,self.cdrecord_url,version = self.app_man.get_application_infos ("cdrecord")

    def blank_disk (device,blank_type,speed):
        print device
        if speed == "Auto":
            params = "-v dev="+device+" gracetime=2 blank="+blank_type
        else:
            params = "-v dev="+device+" gracetime=2 speed="+speed+" blank="+blank_type

        return params
    blank_disk = staticmethod (blank_disk)


    def write_iso (self,iso_file,speed,multisess=False,overburn=False,eject=False):

        command = self.cdrecord_url + " -v gracetime=2 "

        if overburn:
            command += " -overburn"

        if multisess:
            command += " -multi"

        if eject:
            command += " -eject"

        if self.write_speed != "Auto":
            command += " speed="+speed

        command += " dev="+self.device_manager.get_current_writer().get_device()+" "

        command += iso_file

        return command


    def generate_command (self,iso,simulation=False):

        command = self.cdrecord_url + " -v gracetime=2"
        command += " dev="+self.device_manager.get_current_writer().get_device()
        if self.write_speed!= "Auto":
            command += " speed="+self.write_speed

        if not (self.multisess == "No multisession Disk" or self.multisess == "Finish a multisession Disk"):
            command += " -multi"

        if self.track_mode == "Mode 1":
            command += " -data"
        elif self.track_mode == "Mode 2":
            command += " -mode2"
        elif self.track_mode == "xa":
            command += " -xa"
        elif self.track_mode == "xa1":
            command += " -xa1"
        elif self.track_mode == "xa2":
            command += " -xa2"
        elif self.track_mode == "xamix":
            command += " -xamix"

        if self.multisess == "No multisession Disk":
            if self.write_method == "Disk at once":
                command += " -dao"
            elif self.write_method == "Disk at once":
                command += " -tao"
        if simulation:
            command += " -dummy"

#===============================================================================
#        if self.fixating:
#            command += " -fix"
#        else:
#            command += " -nofix"
#===============================================================================

        command += " "+iso

        return command

class readcd:
    app_manager = None
    dev_manager = None
    config_handler = None
    comline_tools = None

    readcd_url = None
    retries = -1

    def __init__(self,comline_tools,app_manager,dev_manager,config_handler):
        self.comline_tools = comline_tools
        self.app_manager = app_manager
        self.dev_manager = dev_manager
        self.config_handler = config_handler
        name,self.readcd_url,version = self.app_manager.get_application_infos ("readcd")

    def read_session (self,
                      device,
                      sector_first,
                      sector_last,
                      raw_mode=False,
                      image_file=os.devnull,
                      read_speed="",
                      ignore_read_errors=False,
                      ):

        command = self.readcd_url

        if raw_mode:
            command += " -nocorr"

        if ignore_read_errors:
            command += " -noerror"

        command += " dev=%s "%device
        command += " f=%s "%image_file

        if read_speed != "" and read_speed !="Auto":
            command += " speed=%s "%read_speed

        command += " sectors=%s-%s "%(sector_first,sector_last)

        return command

    def is_tao_disk (self,toc,device):

        first_track = toc.tracks[0]

        sector_end = int(first_track.file_length_sectors)
        sector_first = sector_end -2

        ttd = test_tao_data ()

        print self.readcd_url + "dev=%s sectors=%s-%s"%(device,sector_first,sector_end)
        self.comline_tools.execute (self.readcd_url,
                                    "dev=%s sectors=%s-%s f=%s"%(device,sector_first,sector_end,os.devnull),
                                    None,
                                    ttd)

        return ttd.istao

class Cdrdao (burning_tool):
    app_manager = None
    dev_manager = None
    config_handler = None
    comline_tools = None

    cdrdao_url = None

    READ_TOC = "read-toc"
    DATA_DISK = 0
    AUDIO_DISK = 1
    EXTRA_DISK = 2
    MULTI_SESSION_DATA_DISK = 3

    # Buffer off all tocs from last disk read
    tocs_buffer = None
    speed = ""

    def __init__(self,comline_tools,app_manager,dev_manager,config_handler):
        self.comline_tools = comline_tools
        self.app_manager = app_manager
        self.dev_manager = dev_manager
        self.config_handler = config_handler
        name,self.cdrdao_url,version = self.app_manager.get_application_infos ("cdrdao")

    def get_tocs_buffer (self):
        if self.tocs_buffer != None:
            return self.tocs_buffer
        else:
            return self.read_tocs()

    def write_cd (self,
                  buffer_underrun,
                  write_speed_control,
                  force,
                  keep_image,
                  overburn,
                  eject,
                  toc_file,
                  multisess=False):

        command = self.cdrdao_url
        command += " write"
        command += " --device %s"%self.dev_manager.get_current_writer().get_device()

        if self.write_speed != "Auto":
            command += " --speed %s"%write_speed

        if overburn:
            command += " --overburn"

        if multisess:
            command += " --multi"

        if eject:
            command += " --eject"

        if keep_image:
            command += " --keepimage"

        if force:
            command += " --force"

        if not buffer_underrun:
            command += " --buffer-under-run-protection 0"

        if not write_speed_control:
            command += " --write-speed-control 0"

        command += " %s"%toc_file

        return command


    def copy_cd (self,
                  device,
                  source_device,
                  simulate,
                  write_speed,
                  read_speed,
                  multisess,
                  overburn,
                  eject,
                  on_the_fly,
                  data_file,
                  session,
                  keep_image,
                  tao_source,
                  force):

        command = self.cdrdao_url
        command += " copy"
        command += " --source-device %s"%self.dev_manager.get_current_writer().get_device()
        command += " --device %s"%self.dev_manager.get_current_writer().get_device()

        if simulate:
            command += " --simulate"

        command += " --speed %s"%write_speed
        command += " --rspeed %s"%read_speed

        if multisess:
            command += " --multi"

        if overburn:
            command += " --overburn"
        if eject:
            command += " --eject"
        if on_the_fly:
            command += " --on-the-fly"

        command += " --datafile %s"
        command += " --session %d"
        command += " --fast-toc"

        if keep_image:
            command += " --keepimage"
        if tao_source:
            command += " --tao-source"

        if force:
            command += " --force"

        if self.config_handler.get("cddb/use_cddb_servers"):
            command += " --with-cddb"
            #command += " --cddb-servers"%

        if self.config_handler.get("cddb/use_local_cddb"):
            dirs = self.config_handler.get("cddb/cddb_dirs")
            command += " --cddb-directory "
            for dir in dirs:
                command += dir + " "
        command += "  -v 5"

        return command

    def get_disk_infos(self):
        disk_info = {}
        cmd_result = self.comline_tools.execute (self.cdrdao_url," disk-info --device "+self.dev_manager.get_current_writer().get_device())

        cdrw_info_regexp = compile (".*CD-RW\s*:(.*)")
        total_cap_info_regexp = compile (".*Total\sCapacity\s*:(.*)")
        cdr_medium_info_regexp = compile (".*CD-R\smedium\s*:(.*)")
        cdr_medium_suite_info_regexp = compile("\s+(.+)")
        record_speed_info_regexp = compile ("Recording\sSpeed\s*:(.*)")
        empty_info_regexp = compile ("CD-R\sempty\s*:(.*)")
        toc_type_info_regexp = compile ("Toc\sType\s*:(.*)")
        sessions_info_regexp = compile ("Sessions\s*:(.*)")
        last_track_info_regexp = compile ("Last\sTrack\s*:(.*)")
        start_last_session_info_regexp = compile ("Start\sof\slast\ssession\s*:(.*)")
        start_new_session_info_regexp = compile ("Start\sof\snew\ssession\s*:(.*)")
        appendable_info_regexp = compile ("Appendable\s*:(.*)")

        device_empty_info_regexp = compile (".*WARNING: Unit not ready, still trying.*")
        sorted_keys = []

        cdr_medium_flag = False
        for res in cmd_result:

            match = device_empty_info_regexp.match(res)
            if match != None:
               raise DeviceEmptyError

            match = cdrw_info_regexp.match(res)
            if match != None:
                sorted_keys.append("CD-RW")
                disk_info["CD-RW"] = match.group(1).strip()

            match = total_cap_info_regexp.match(res)
            if match != None:
                sorted_keys.append("Total Capacity")

                disk_info["Total Capacity"] = match.group(1).strip()

            match = cdr_medium_info_regexp.match(res)
            if match != None:
                cdr_medium_flag = True
                sorted_keys.append("CD-R medium")
                disk_info["CD-R medium"] = match.group(1).strip()

            match = cdr_medium_suite_info_regexp.match(res)
            if match != None:
                if cdr_medium_flag:
                    disk_info["CD-R medium"] += " "+match.group(1).strip()
                    cdr_medium_flag = False

            match = record_speed_info_regexp.match(res)
            if match != None:
                sorted_keys.append("Recording Speed")
                disk_info["Recording Speed"] = match.group(1).strip()

            match = empty_info_regexp.match(res)
            if match != None:
                sorted_keys.append("CD-R empty")
                disk_info["CD-R empty"] = match.group(1).strip()
                print disk_info["CD-R empty"]

            match = toc_type_info_regexp.match(res)
            if match != None:
                sorted_keys.append("Toc Type")
                disk_info["Toc Type"] = match.group(1).strip()

            match = sessions_info_regexp.match(res)
            if match != None:
                sorted_keys.append("Sessions")
                disk_info["Sessions"] = match.group(1).strip()

            match = last_track_info_regexp.match(res)
            if match != None:
                sorted_keys.append("Last Track")
                disk_info["Last Track"] = match.group(1).strip()

            match = appendable_info_regexp.match(res)
            if match != None:
                sorted_keys.append("Appendable")
                disk_info["Appendable"] = match.group(1).strip()

            match = start_last_session_info_regexp.match(res)
            if match != None:
                sorted_keys.append("Start of last session")
                disk_info["Start of last session"] = self.comline_tools.get_session_num(match.group(1).strip())

            match = start_new_session_info_regexp.match(res)
            if match != None:
                sorted_keys.append("Start of new session")
                disk_info["Start of new session"] = str(int(self.comline_tools.get_session_num(match.group(1).strip()))-150)
        return sorted_keys,disk_info

    def read_cd (self,
                 device,
                  raw_mode,
                  fasttoc,
                  image_file,
                  toc_file,
                  read_speed,
                  ignore_read_errors,
                  audio_disk,
                  session="",
                  source_device=""):


        keys,disk_infos = self.get_disk_infos()

        command_line = self.cdrdao_url
        command_line += " read-cd"

        if audio_disk:
            if self.config_handler.get("cddb/use_cddb_servers"):
                command_line += " --with-cddb"

                if self.config_handler.get("cddb/servers").strip()!= "":
                    command_line += " --cddb-servers %s"%self.config_handler.get("cddb/servers").rsplit(":")[1]

                if self.config_handler.get("cddb/cddb_dirs").strip()!= "":
                    command_line += " --cddb-directory %s"%self.config_handler.get("cddb/cddb_dirs").split(";")[0]

        if fasttoc:
            command_line += " --fast-toc"

        if ignore_read_errors:
            command_line += " --read-raw"

        if raw_mode:
            command_line += " --read-subchan rw_raw"

        if read_speed != "" and read_speed != "Auto":
            command_line += " --rspeed %s"%read_speed

        if image_file != "":
            command_line += " --datafile %s"%image_file

        command_line += " --device %s %s"%(device,toc_file)

        return command_line


    def read_tocs(self,window=None):
        tmp_dir = self.config_handler.get ("misc/tempdir")

        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)

        keys,disk_infos = self.get_disk_infos()

        all_tocs = []
        for i in range (int(disk_infos["Sessions"])):
            disk_toc_data = Toc_Data()

            tmp_toc = str(int(10000000000*random.random()))+".toc"

            if window != None:
                window.reset(i)

            self.comline_tools.execute (self.cdrdao_url,"read-toc --force --fast-toc --session %d --device %s %s"%(i+1,
                                                                    self.dev_manager.get_current_writer().get_device(),
                                                                    tmp_dir+os.path.sep+tmp_toc),
                                                                window,disk_toc_data)

            disk_toc = disk_toc_data.toc
            fh = open(tmp_dir+os.path.sep+tmp_toc)
            disk_toc.get_from_toc_file(fh)
            fh.close()
            disk_toc.session = i+1
            all_tocs.append(disk_toc)

        self.tocs_buffer = all_tocs
        return all_tocs

    def get_CD_type(self):
        keys,disk_infos = self.get_disk_infos()
        tocs = self.read_tocs()
        num_sessions = int(disk_infos["Sessions"])

        if num_sessions == 1:
            if self.__is_audio_disk(tocs):
                return self.AUDIO_DISK
            elif self.__is_data_cd(tocs):
                return self.DATA_DISK
        else:
            if num_sessions == 2:
                if self.__is_cdextra(tocs):
                    return self.EXTRA_DISK
            else:
                return self.MULTI_SESSION_DATA_DISK

    def __is_cdextra(self,tocs):
        if tocs[0].type == "AUDIO" and tocs[1] == "DATA":
            return True
        else:
            return False

    def __is_data_cd (self,tocs):
        if tocs[0].type == "DATA":
            return True
        else:
            return False

    def __is_audio_disk (self,tocs):
        if tocs[0].type == "AUDIO":
            return True
        else:
            return False

class Disk_toc:
    catalog = ""
    # type could be DATA, AUDIO or XA
    type = None
    __CD_DA = 0
    __CD_ROM = 1
    __CD_ROM_XA = 2
    languages_map = []
    global_cd_text = []
    tracks = []
    session = -1

    # set default language to english
    default_language = 0

    def __init__(self):
        self.tracks = []

    def __read_section (self,fh):
        line = ""
        section = []
        while line != "}":
            line = fh.readline()
            line = line.strip()

            if line != "}":
                section.append(line)

        return section

    def get_default_global_cd_text (self):
        return self.global_cd_text[self.default_language]

    def set_audio_nature (self):
        self.type = self.__CD_DA

    def get_from_toc_file (self,toc_file):
        catalog_regxp = compile ("CATALOG \"(.*)\"")
        cdda_regxp = compile ("CD_DA")
        cdrom_regxp = compile ("CD_ROM")
        cdromxa_regxp = compile ("CD_ROM_XA")
        track_regxp = compile("TRACK\s+(.*)")
        copy_regxp = compile ("(.*)\s*COPY")
        preemph_regxp = compile ("(.*)\s*PRE_EMPHASIS")
        two_chans_regxp = compile ("TWO_CHANNEL_AUDIO")
        four_chans_regxp = compile ("FOUR_CHANNEL_AUDIO")
        isrc_regxp = compile ("ISRC \"(.*)\"")
        silence_regexp = compile("SILENCE\s*(.*)")
        zero_regexp = compile("ZERO\s*(.*)")
        file_regexp = compile ("FILE \"(.*)\"\s*(\d\d:\d\d:\d\d)\s+(\d\d:\d\d:\d\d)*")
        audiofile_regep = compile ("AUDIOFILE \"(.*)\"\s*(\d\d:\d\d:\d\d)\s+(\d\d:\d\d:\d\d)*")
        datafile_regexp = compile ("DATAFILE \"(.*)\"\s*(\d\d:\d\d:\d\d)\s+(\d\d:\d\d:\d\d)*")
        file_regexp0 = compile ("FILE \"(.*)\"\s*(\d)\s+(\d\d:\d\d:\d\d)*")
        audiofile_regep0 = compile ("AUDIOFILE \"(.*)\"\s*(\d)\s+(\d\d:\d\d:\d\d)*")
        datafile_regexp0 = compile ("DATAFILE \"(.*)\"\s*(\d)\s+(\d\d:\d\d:\d\d)*")
        fifo_regexp = compile ("FIFO \"(.*)\"\s*(.*)\s+(.*)")
        start_regexp = compile("START\s*(.*)")
        pregap_regexp = compile("PREGAP\s*(.*)")
        index_regexp = compile("INDEX\s*(.*)")
        cdtext_regxp = compile ("CD_TEXT")
        language_map_regexp = compile ("\s*LANGUAGE_MAP\s+{")
        language_num = compile ("\s*(.*) : (.*).*")
        language_regexp = compile ("\s*LANGUAGE\s+(.*)\s+{")

        global_section = True
        line = " "

        track_num = -1

        while True:
            line = toc_file.readline()

            if line == "":
                break

            line = line.strip()

            matched = catalog_regxp.match (line)
            if matched != None:
                self.catalog = matched.group(1)

            """
            CD TYPE
            """
            matched = cdda_regxp.match (line)
            if matched != None:
                self.type = "AUDIO"

            matched = cdrom_regxp.match (line)
            if matched != None:
                self.type = "DATA"

            matched = cdromxa_regxp.match (line)
            if matched != None:
                    self.type = "XA"

            matched = cdtext_regxp.match (line)
            if matched != None:
                subline = " "

                """
                CD_TEXT
                """
                while subline != "}":
                    subline = toc_file.readline()
                    subline = subline.strip()

                    submatched = language_map_regexp.match(subline)
                    if submatched != None:
                        subsubline = " "

                        """
                        Language Map
                        """
                        while subsubline != "}":
                            subsubline = toc_file.readline()
                            subsubline = subsubline.strip()

                            subsubmatched = language_num.match(subsubline)
                            if subsubmatched != None:
                                index = int(subsubmatched.group(1))
                                self.languages_map[index] =  subsubmatched.group(2)

                    submatched = language_regexp.match(subline)
                    if submatched != None:
                        num_language = int(submatched.group(1))
                        section = self.__read_section(toc_file)
                        cdt_inst = self.get_cd_text_values(section)
                        print cdt_inst
                        cdt_inst.language = num_language

                        if global_section:
                            self.global_cd_text = cdt_inst
                        else:
                            self.tracks[track_num].cd_text.append(cdt_inst)


            match = copy_regxp.match(line)
            if match != None:
                if match.group(1).strip() == "NO":
                    self.tracks[track_num].copy = False
                else:
                    self.tracks[track_num].copy = True

            match = preemph_regxp.match(line)
            if match != None:
                if match.group(1).strip() == "NO":
                    self.tracks[track_num].pre_emphasis = False
                else:
                    self.tracks[track_num].pre_emphasis = True

            match = two_chans_regxp.match(line)
            if match != None:
                self.tracks[track_num].two_audio_channels = True

            match = four_chans_regxp.match(line)
            if match != None:
                self.tracks[track_num].four_audio_channels = True

            match = isrc_regxp.match(line)
            if match != None:
                self.tracks[track_num].isrc = match.group(1)

            match = silence_regexp.match(line)
            if match != None:
                self.tracks[track_num].silence = match.group(1)

            match = zero_regexp.match(line)
            if match != None:
                self.tracks[track_num].zero = match.group(1)

            match = file_regexp.match(line)
            if match != None:
                self.tracks[track_num].filename = match.group(1)
                #self.tracks[track_num].file_start= match.group(2)
                #if len(match.groups()) > 2:
                #    if match.group(3) != None:
                #        self.tracks[track_num].file_length = match.group(3)
            else:
                match = file_regexp0.match(line)
                if match != None:
                    self.tracks[track_num].filename = match.group(1)

            match = audiofile_regep.match(line)
            if match != None:
                self.tracks[track_num].filename = match.group(1)
            else:
                match = audiofile_regep0.match(line)
                if match != None:
                    self.tracks[track_num].filename = match.group(1)

            match = datafile_regexp.match(line)
            if match != None:
                self.tracks[track_num].filename = match.group(1)
            else:
                match = datafile_regexp0.match(line)
                if match != None:
                    self.tracks[track_num].filename = match.group(1)

            match = fifo_regexp.match(line)
            if match != None:
                self.tracks[track_num].fifo_path = match.group(1)
                self.tracks[track_num].fifo_length = match.group(2)

            match = start_regexp.match(line)
            if match != None:
                self.tracks[track_num].start = match.group(1)

            match = pregap_regexp.match(line)
            if match != None:
                self.tracks[track_num].pregap = match.group(1)

            match = index_regexp.match(line)
            if match != None:
                self.tracks[track_num].index = match.group(1)

    def get_num_tracks(self):
        return len(self.tracks)

    def get_cd_text_values (self,cdtext_section):
        title_regexp = compile ("\s*TITLE \"(.*)\"")
        performer_regexp = compile ("\s*PERFORMER \"(.*)\"")
        songwriter_regexp = compile ("\s*SONGWRITER \"(.*)\"")
        composer_regexp = compile ("\s*COMPOSER \"(.*)\"")
        aranger_regexp = compile ("\s*ARANGER \"(.*)\"")
        message_regexp = compile ("\s*MESSAGE \"(.*)\"")
        diskid_regexp = compile ("\s*DISC_ID\s+(.*)")
        genre_regexp = compile("\s*GENRE\s+(.*)")
        upcean_regexp = compile ("\s*UPC_EAN \"(.*)\"")
        isrc_regexp = compile ("\s*ISRC \"(.*)\"")

        cdt_inst = Cd_text()

        for line in cdtext_section:
            subsubmatched = title_regexp.match (line)
            if subsubmatched != None:
                cdt_inst.title = subsubmatched.group(1)

            subsubmatched = performer_regexp.match (line)
            if subsubmatched != None:
                cdt_inst.performer = subsubmatched.group(1)

            subsubmatched = songwriter_regexp.match (line)
            if subsubmatched != None:
                cdt_inst.songwriter = subsubmatched.group(1)

            subsubmatched = composer_regexp.match (line)
            if subsubmatched != None:
                cdt_inst.composer = subsubmatched.group(1)

            subsubmatched = aranger_regexp.match (line)
            if subsubmatched != None:
                cdt_inst.aranger = subsubmatched.group(1)

            subsubmatched = message_regexp.match (line)
            if subsubmatched != None:
                cdt_inst.message = subsubmatched.group(1)

            subsubmatched = diskid_regexp.match (line)
            if subsubmatched != None:
                cdt_inst.disc_id = subsubmatched.group(1)

            subsubmatched = genre_regexp.match (line)
            if subsubmatched != None:
                cdt_inst.genre = subsubmatched.group(1)

            subsubmatched = upcean_regexp.match (line)
            if subsubmatched != None:
                cdt_inst.upc_ean = subsubmatched.group(1)

            subsubmatched = isrc_regexp.match (line)
            if subsubmatched != None:
                cdt_inst.isrc = subsubmatched.group(1)

        return cdt_inst

    def create_cdtext_section (self, cd_text):

    	section = "CD_TEXT {\n\tLANGUAGE_MAP {\n"

    	i = 0
    	for map in language_map:
    		section += "\t\t%d : %d\n"%(i,map)

    	section += "\t}\n"

    def to_string (self):
        output = ""

        if self.type == self.__CD_DA:
            output += "CD_DA\n\n"
        elif self.type == self.__CD_ROM:
            output += "CD_ROM\n\n"
        elif self.type == self.__CD_ROM_XA:
            output += "CD_ROM_XA\n\n"
        else:
            raise TocError()

        # Global CD TEXT Section
        if len(self.global_cd_text) != 0:
            output += "CD_TEXT {\n\tLANGUAGE_MAP {\n"

            for i in range(len(self.languages_map)):
                output += "\t\t%d: %d\n"%(i,self.languages_map[i])

            output += "\t}\n"

            for i in range (len(self.global_cd_text)):
                output += "\tLANGUAGE %d {\n"%i
                output += "\t\t TITLE \"%s\"\n"%self.global_cd_text[i].title
                output += "\t\t PERFORMER \"%s\"\n"%self.global_cd_text[i].performer
                output += "\t\t COMPOSER \"%s\"\n"%self.global_cd_text[i].composer
                output += "\t\t ARRANGER \"%s\"\n"%self.global_cd_text[i].arranger
                output += "\t\t SONGWRITER \"%s\"\n"%self.global_cd_text[i].songwriter
                output += "\t\t MESSAGE \"%s\"\n"%self.global_cd_text[i].message
                output += "\t\t DISC_ID \"%s\"\n"%self.global_cd_text[i].disc_id
                output += "\t\t GENRE \"%s\"\n"%self.global_cd_text[i].genre
                output += "\t\t UPC_EAN \"%s\"\n"%self.global_cd_text[i].upc_ean
                output += "\t}\n"

            output += "}\n\n"

        for track in self.tracks:
            if track.type == track.AUDIO:
                output += "TRACK AUDIO\n"
            elif track.type == track.MODE1:
                output += "TRACK MODE1\n"
            elif track.type == track.MODE1_RAW:
                output += "TRACK MODE1_RAW\n"
            elif track.type == track.MODE2:
                output += "TRACK MODE2\n"
            elif track.type == track.MODE2_FORM1:
                output += "TRACK MODE2_FORM1\n"
            elif track.type == track.MODE2_FORM2:
                output += "TRACK MODE2_FORM2\n"
            elif track.type == track.MODE2_FORM_MIX:
                output += "TRACK MODE2_FORM_MIX\n"
            elif track.type == track.MODE2_RAW:
                output += "TRACK MODE2_RAW\n"

            if track.copy_permited:
                output += "COPY\n"
            else:
                output += "NO COPY\n"

            if track.pre_emphasis:
                output += "PRE_EMPHASIS\n"
            else:
                output += "NO PRE_EMPHASIS\n"

            if track.two_audio_channels:
                output += "TWO_CHANNEL_AUDIO\n"
            elif track.four_audio_channels:
                output += "FOUR_CHANNEL_AUDIO\n"

            if track.isrc != "":
                output += "ISRC %s"%track.isrc

            if len (track.cd_text) > 0:
                output += "CD_TEXT {\n"

                for i in range(len(track.cd_text)):
                    output += "\tLANGUAGE %d {\n"%i
                    output += "\t\t TITLE \"%s\"\n"%track.cd_text[i].title
                    output += "\t\t PERFORMER \"%s\"\n"%track.cd_text[i].performer
                    output += "\t\t COMPOSER \"%s\"\n"%track.cd_text[i].composer
                    output += "\t\t ARRANGER \"%s\"\n"%track.cd_text[i].arranger
                    output += "\t\t SONGWRITER \"%s\"\n"%track.cd_text[i].songwriter
                    output += "\t\t MESSAGE \"%s\"\n"%track.cd_text[i].message
                    if track.cd_text[i].isrc != "":
                        output += "\t\t ISRC \"%s\"\n"%track.cd_text[i].isrc
                    output += "\t}\n"

                output += "}\n"

            if track.pregap != None:
                output += "PREGAP %02d:%02d:%02d"%track.pregap

            output += "FILE \"%s\" 0\n\n"%track.filename

        return output


class Track:
    AUDIO = 0
    MODE1 = 1
    MODE1_RAW = 2
    MODE2 = 3
    MODE2_FORM1 = 4
    MODE2_FORM2 = 5
    MODE2_FORM_MIX = 6
    MODE2_RAW = 7

    default_language = 0

    def __init__(self):
        self.cd_text = []

        # By default a cd text in english language is created
        self.cd_text.append(Cd_text())

        self.copy_permited = True
        self.pre_emphasis = ""
        self.two_audio_channels = True
        self.four_audio_channels = False
        self.isrc = ""
        self.filename = ""
        self.pregap = None

        # Audio type by default
        self.type = self.AUDIO

    def get_default_cdText (self):
        return self.cd_text[self.default_language]

class Cd_text:

    def __init__(self,global_section=False):
        self.global_section = global_section
        self.title = ""
        self.performer = ""
        self.songwriter = ""
        self.composer = ""
        self.arranger = ""
        self.message = ""
        self.disc_id = ""
        self.genre = ""
        self.upc_ean = ""
        self.isrc = ""
        self.language = 0


class Fake_window:

    def show_window (self):
        pass

    def hide_window (self):
        pass

    def update(self,output):
        pass

class Readtoc_fake_window (Fake_window):
    toc = None

    def __init (self):
        self.track_analyse_regxp = compile("Analyzing track\s+(\d\d)\s+\((.*)\).*")
        self.track_regxp = compile ("\s*(\d*)\s+(.*)\s+(\d)\s+(\d\d:\d\d:\d\d)\(\s*(\d*)\)\s+(\d\d:\d\d:\d\d)\(\s*(\d*)\)")
        self.last_track_regxp = compile ("\s*Leadout\s+(.*)\s+(\d)\s+(\d\d:\d\d:\d\d)\(\s*(\d*)\)")

    def update(self,output):
        match = self.track_regxp.match(output)
        if match!=None:
            t = Track()
            t.type = match.group(2)
            t.number = int(match.group(1))
            t.file_start = match.group(4)
            t.file_start_sectors = match.group(5)
            t.file_length = match.group(6)
            t.file_length_sectors= match.group(7)
            self.toc.tracks.append(t)

    def reset (self,i):
        self.toc = Disk_toc()

class Data_Container:

    def update (self,data):
        pass

class Toc_Data (Data_Container):
    toc = None

    def __init__ (self,pid=None):
        self.track_analyse_regxp = compile("Analyzing track\s+(\d\d)\s+\((.*)\).*")
        self.track_regxp = compile ("\s*(\d*)\s+(.*)\s+(\d)\s+(\d\d:\d\d:\d\d)\(\s*(\d*)\)\s+(\d\d:\d\d:\d\d)\(\s*(\d*)\)")
        self.last_track_regxp = compile ("\s*Leadout\s+(.*)\s+(\d)\s+(\d\d:\d\d:\d\d)\(\s*(\d*)\)")
        self.toc = Disk_toc()

    def update(self,output):
        match = self.track_regxp.match(output)
        if match!=None:
            t = Track()
            t.type = match.group(2)
            t.number = int(match.group(1))
            t.file_start = match.group(4)
            t.file_start_sectors = match.group(5)
            t.file_length = match.group(6)
            t.file_length_sectors= match.group(7)
            self.toc.tracks.append(t)



class test_tao_data(Data_Container):

    istao=False
    pid = None

    def __init__ (self,pid=None):
        self.cannot_read_disk_regexp = compile (".*Cannot read source disk.*")

    def update (self,output):
        match = self.cannot_read_disk_regexp.match(output)

        if match!=None:
            print "killing process %d"%self.pid
            try:
                os.kill(self.pid+1,15)
            except OSError:
                # Workaround if readcd pid is not sh pid +1
                os.kill(self.pid+2,15)

            self.istao = True


#ct = Common_tools ()
#ttd = test_tao_data()
#
#for i in range(1):
#    ct.execute("/usr/bin/readcd", "dev=/dev/hdc sectors=6803-6805 f=/dev/zero", None, ttd)