import gtk

from re import compile,match

from backends.tool_box import Common_tools
from backends.tool_box import Track
from backends.tool_box import Disk_toc
from gui.gui_tools import *

class window:
    window = None
    pid = None
    aborted = False

    def show_window(self):
        self.window.show_all()
        self.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)

    def hide_window(self):
        self.window.hide_all()

    def update(self,output):
        return

    def get_window (self):
        return self.window

    def abort_process (self):
        self.aborted = True

    def is_aborted (self):
        return self.aborted


class copy_window(window):
    label = None
    variable_copy_label = None
    variable_from_label = None
    variable_to_label = None
    label_north_hbox = None
    label_south_hbox = None
    numfiles_added_label = None
    progress_bar = None
    com_tools = None
    num_files = 0
    current_fraction = 0
    progression_delta = 0.0
    numfiles_copied = 0
    num_files = 0

    def __init__ (self):
        self.com_tools = Common_tools()

        # Widgets
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.window.set_size_request(400,170)
        self.window.set_title("Adding Files")

        self.label = gtk.Label()
        self.label.set_markup ('<span weight="bold">Files added:</span>')

        self.numfiles_added_label = gtk.Label()
        #self.numfiles_added_label.set_markup ('<span weight="bold">1/16000</span>')

        self.label_north_hbox = gtk.HBox(False,0)
        self.label_north_hbox.pack_start(self.label,False,False)
        self.label_north_hbox.pack_end(self.numfiles_added_label,False,True)

        self.label_south_hbox = gtk.HBox (False,0)

        # Est-south Bloc
        #############################################
        #                   #                       #
        #                   #                       #
        #############################################
        #############################################
        #####################                       #
        #####################                       #
        #############################################
        self.constant_labels_vbox = gtk.VBox (False,0)
        self.constant_label_copy_hbox = gtk.HBox (False,0)
        self.constant_label_from_hbox = gtk.HBox (False,0)
        self.constant_label_to_hbox = gtk.HBox (False,0)

        copy_label = gtk.Label()
        copy_label.set_markup ('<span weight="bold">Copy:</span>')
        from_label = gtk.Label()
        from_label.set_markup ('<span weight="bold">From:</span>')
        to_label = gtk.Label()
        to_label.set_markup ('<span weight="bold">To:</span>')

        self.constant_label_copy_hbox.pack_end(copy_label,False,False,2)
        self.constant_label_from_hbox.pack_end(from_label,False,False,2)
        self.constant_label_to_hbox.pack_end(to_label,False,False,2)

        self.constant_labels_vbox.pack_start(self.constant_label_copy_hbox,True,False)
        self.constant_labels_vbox.pack_start(self.constant_label_from_hbox,True,False)
        self.constant_labels_vbox.pack_start(self.constant_label_to_hbox,True,False)

        # West-south Bloc
        #############################################
        #                   #                       #
        #                   #                       #
        #############################################
        #############################################
        #                    ########################
        #                    ########################
        #############################################
        self.variable_labels_vbox = gtk.VBox (False,0)
        self.variable_label_copy_hbox = gtk.HBox (False,0)
        self.variable_label_from_hbox = gtk.HBox (False,0)
        self.variable_label_to_hbox = gtk.HBox (False,0)

        self.variable_copy_label = gtk.Label()
        self.variable_from_label = gtk.Label()
        self.variable_to_label = gtk.Label()

        self.variable_label_copy_hbox.pack_start(self.variable_copy_label,False,False,5)
        self.variable_label_from_hbox.pack_start(self.variable_from_label,False,False,5)
        self.variable_label_to_hbox.pack_start(self.variable_to_label,False,False,5)

        self.variable_labels_vbox.pack_start(self.variable_label_copy_hbox,True,False,3)
        self.variable_labels_vbox.pack_start(self.variable_label_from_hbox,True,False,3)
        self.variable_labels_vbox.pack_start(self.variable_label_to_hbox,True,False,3)

        self.label_south_hbox.pack_start(self.constant_labels_vbox,False,False)
        self.label_south_hbox.pack_start(self.variable_labels_vbox,False,False)

        self.progress_bar = gtk.ProgressBar()
        self.progress_bar.set_size_request(-1,25)
        self.progress_bar.set_fraction(0.)

        vbox = gtk.VBox(False,0)
        vbox.set_border_width(20)
        vbox.pack_start(self.label_north_hbox,False,False)
        vbox.pack_start(self.progress_bar,False,False,10)
        vbox.pack_start(self.label_south_hbox,False,False)

        self.window.add(vbox)

    def set_numfiles (self,num):
        try:
            self.progression_delta = float(1.0/num)
            self.num_files = num
        except ZeroDivisionError,error:
            return
    def update(self,output):
        self.numfiles_copied = self.numfiles_copied + 1
        (filename,root_pwd,dest_pwd) = self.com_tools.cut_symlink_copy_outpout (output)

        self.variable_copy_label.set_label(filename)
        self.variable_from_label.set_label(root_pwd)
        self.variable_to_label.set_label(dest_pwd)

        tmp = "<span weight=\"bold\">%d/%d</span>" % (self.numfiles_copied,self.num_files)
        self.numfiles_added_label.set_markup (tmp)
        try:
            self.progress_bar.set_text("%d " % int(float(float(self.numfiles_copied)/self.num_files)*100) +"%")
        except ZeroDivisionError,error:
            self.progress_bar.set_text('100"%')
        self.current_fraction = self.current_fraction + self.progression_delta

        if self.current_fraction < 1.0:
            self.progress_bar.set_fraction(self.current_fraction)
        #self.__emit_pulse()

    def initialize (self):
         self.num_files = 0
         self.current_fraction = 0
         self.progression_delta = 0.0
         self.numfiles_copied = 0
         self.num_files = 0

class create_dir_win (window):
    gui_control = None
    com_tools = None
    image = None
    label = None
    textbox = None
    ok_button = None
    cancel_button = None

    def __init__ (self,gui_control):
        self.gui_control = gui_control
        self.com_tools = Common_tools()

        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.window.set_size_request(280,130)
        self.window.set_title("Create Directory")

        self.image = gtk.Image ()
        self.image.set_from_stock (gtk.STOCK_DIALOG_QUESTION,gtk.ICON_SIZE_DIALOG)

        self.main_hbox = gtk.HBox (False,0)

        self.left_vbox = gtk.VBox (True,0)
        self.left_vbox.set_border_width(10)
        self.left_vbox.pack_start(self.image,True,True)

        self.right_vbox = gtk.VBox (False,0)

        self.label_hbox = gtk.HBox (False,0)
        self.label = gtk.Label()
        self.label.set_markup ('<span weight="bold">Directory name:</span>')
        self.label_hbox.pack_start(self.label,False,False)

        self.entry_hbox = gtk.VBox (False,0)
        self.textbox = gtk.Entry ()
        self.entry_hbox.pack_start(self.textbox)

        self.buttons_hbox = gtk.HBox (True,10)

        self.ok_button = gtk.Button ("Ok",gtk.STOCK_APPLY,True)
        self.ok_button.connect ("pressed",self.gui_control.cb_mkdir_create_dir)

        self.cancel_button = gtk.Button ("Cancel",gtk.STOCK_CANCEL,True)
        self.cancel_button.connect ("pressed",self.gui_control.cb_mkdir_cancel_creation)

        self.buttons_hbox.pack_end(self.ok_button,False,False)
        self.buttons_hbox.pack_end(self.cancel_button,False,False)

        self.right_vbox.pack_start(self.label_hbox,True,True,10)
        self.right_vbox.pack_start(self.entry_hbox,True,True,10)
        self.right_vbox.pack_start(self.buttons_hbox,True,True,10)

        self.main_hbox.pack_start(self.left_vbox,False,False)
        self.main_hbox.pack_start(self.right_vbox,False,False)

        self.window.add(self.main_hbox)

class xmlfs_copy_window (copy_window):
    def update (self,output):
        self.numfiles_copied = self.numfiles_copied + 1
        try:
            (filename,root_pwd,dest_pwd) = output
        except ValueError:
            print output
        self.variable_copy_label.set_label(filename)
        self.variable_from_label.set_label(root_pwd)
        self.variable_to_label.set_label(dest_pwd)

        tmp = "<span weight=\"bold\">%d/%d</span>" % (self.numfiles_copied,self.num_files)
        self.numfiles_added_label.set_markup (tmp)
        try:
            self.progress_bar.set_text("%d " % int(float(float(self.numfiles_copied)/self.num_files)*100) +"%")
        except ZeroDivisionError,error:
            self.progress_bar.set_text('100"%')
        self.current_fraction = self.current_fraction + self.progression_delta

        if self.current_fraction < 1.0:
            self.progress_bar.set_fraction(self.current_fraction)

class import_session_window (window):
    def __init__ (self,dev_manager):
        # Widgets
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.window.set_size_request(500,100)
        self.window.set_title("Import session")

        self.label = gtk.Label()
        self.label.set_markup ('<span weight="bold">Import session from:</span>')

        writer = dev_manager.get_current_writer()

        self.writer_label = gtk.Label(writer.get_display_name())
        #self.numfiles_added_label.set_markup ('<span weight="bold">1/16000</span>')

        self.label_north_hbox = gtk.HBox(False,0)
        self.label_north_hbox.pack_start(self.label,False,False)
        self.label_north_hbox.pack_end(self.writer_label,False,True)

        self.progress_bar = gtk.ProgressBar()
        self.progress_bar.set_size_request(-1,15)
        self.progress_bar.set_pulse_step(0.2)

        vbox = gtk.VBox(False,0)
        vbox.set_border_width(20)
        vbox.pack_start(self.label_north_hbox,False,False)
        vbox.pack_start(self.progress_bar,False,False,10)

        self.window.add(vbox)

    def update (self,output):
        self.progress_bar.pulse()

class Read_toc_window (window):
    pb_fraction = 0.
    pb_delta = 0.

    session = 0
    track_regxp = None

    toc= None
    num_tracks = 0

    window = None
    label = None
    writer_label = None
    session_label = None
    track_label = None
    label_south_hbox = None
    label_center_hbox = None
    label_north_hbox = None
    progress_bar = None


    def __init__ (self,dev_manager,num_tracks):
        # Widgets
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.window.set_size_request(500,150)
        self.window.set_title("Reading TOC")

        self.label = gtk.Label()
        self.label.set_markup ('<span weight="bold">Reading TOC from</span>')

        writer = dev_manager.get_current_writer()

        self.writer_label = gtk.Label(writer.get_device())
        #self.numfiles_added_label.set_markup ('<span weight="bold">1/16000</span>')

        self.label_north_hbox = gtk.HBox(False,0)
        self.label_north_hbox.pack_start(self.label,False,False)
        self.label_north_hbox.pack_end(self.writer_label,False,True)

        self.session_label = gtk.Label()
        self.session_label.set_markup ('<span weight="bold">Session:</span>')
        self.label_center_hbox = gtk.HBox(False,0)
        self.label_center_hbox.pack_start(self.session_label,False,False)

        self.track_label = gtk.Label()
        self.track_label.set_markup ('<span weight="bold">Track:</span>')
        self.label_south_hbox = gtk.HBox(False,0)
        self.label_south_hbox.pack_start(self.track_label,False,False)

        self.progress_bar = gtk.ProgressBar()
        self.progress_bar.set_size_request(-1,15)
        self.progress_bar.set_fraction(self.pb_fraction)

        vbox = gtk.VBox(False,0)
        vbox.set_border_width(20)
        vbox.pack_start(self.label_north_hbox,False,False)
        vbox.pack_start(self.label_center_hbox,False,False)
        vbox.pack_start(self.label_south_hbox,False,False)
        vbox.pack_start(self.progress_bar,False,False,10)

        self.window.add(vbox)

        self.track_analyse_regxp = compile("Analyzing track\s+(\d\d)\s+\((.*)\).*")
        self.track_regxp = compile ("\s*(\d*)\s+(.*)\s+(\d)\s+(\d\d:\d\d:\d\d)\(\s*(\d*)\)\s+(\d\d:\d\d:\d\d)\(\s*(\d*)\)")
        self.last_track_regxp = compile ("\s*Leadout\s+(.*)\s+(\d)\s+(\d\d:\d\d:\d\d)\(\s*(\d*)\)")
        #self.pb_delta = 1./(float(num_tracks)-1.)
        self.num_tracks = 0
        self.session_numtracks = []
        self.session_num_tracks = 0

    def update (self,output):
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
            self.num_tracks+=1
            self.session_num_tracks +=1

        match = self.last_track_regxp.match(output)
        if match!=None:
            self.session_numtracks.append(self.session_num_tracks)
            self.pb_delta = 1./float(self.session_num_tracks)
            self.session_num_tracks = 0

        match = self.track_analyse_regxp.match(output)
        if match != None:
            track = match.group(1)
            type = match.group(2)
            self.session_label.set_markup ('<span weight="bold">Session: %d</span>'%self.session)
            self.track_label.set_markup ('<span weight="bold">Track: %s (%s)</span>'%(track,type))
            self.pb_fraction +=self.pb_delta
            self.progress_bar.set_fraction(self.pb_fraction)

    def reset (self,i):
        self.session = i+1
        self.pb_fraction = 0.0
        self.toc = Disk_toc()
        self.progress_bar.set_fraction(0.0)

class cdtext_track_window (window):
    cd_text_entries = {}

    def __init__ (self, gui_control, project_id, default_pregap="020"):
        # Widgets
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.window.set_size_request(400,480)
        self.window.set_title("Audio track properties")

        self.gui_control = gui_control
        self.project_id = project_id

        frame = gtk.Frame()
        frame.set_shadow_type(gtk.SHADOW_NONE)
        self.window.add(frame)

        vbox = gtk.VBox(False,10)
        frame.add (vbox)
        vbox.set_border_width (10)

        cd_text_frame = section_frame("CD TEXT")
        hbox_inside_frame = gtk.HBox(False,5)
        hbox_inside_frame.set_border_width (10)
        cd_text_frame.add(hbox_inside_frame)

        vbox_inside_left = gtk.VBox(True,0)
        hbox_inside_frame.pack_start(vbox_inside_left,False,True,20)

        labels = ["Title",
                  "Performer",
                  "Arranger",
                  "Songwriter",
                  "Composer",
                  "ISRC",
                  "Message"]

        for label in labels:
            temp_hbox = gtk.HBox(False,0)
            gtk_label =  gtk.Label(label)
            temp_hbox.pack_start(gtk_label,False,False)
            vbox_inside_left.pack_start(temp_hbox,False,False,3)

        vbox_inside_right = gtk.VBox(True,0)
        hbox_inside_frame.pack_start(vbox_inside_right,True,True)

        for label in labels:
            temp_hbox = gtk.HBox(False,0)
            self.cd_text_entries[label] = gtk.Entry(32)
            vbox_inside_right.pack_start(self.cd_text_entries[label],False,False,3)


        self.cd_text_entries ["Title"].connect('focus-out-event',self.gui_control.cb_tw_cdtext_title_lose_focus,self.project_id)
        self.cd_text_entries ["Performer"].connect('focus-out-event',self.gui_control.cb_tw_cdtext_performer_lose_focus,self.project_id)
        self.cd_text_entries ["Arranger"].connect('focus-out-event',self.gui_control.cb_tw_cdtext_arranger_lose_focus,self.project_id)
        self.cd_text_entries ["Songwriter"].connect('focus-out-event',self.gui_control.cb_tw_cdtext_songwriter_lose_focus,self.project_id)
        self.cd_text_entries ["Composer"].connect('focus-out-event',self.gui_control.cb_tw_cdtext_composer_lose_focus,self.project_id)
        self.cd_text_entries ["ISRC"].connect('focus-out-event',self.gui_control.cb_tw_cdtext_isrc_lose_focus,self.project_id)
        self.cd_text_entries ["Message"].connect('focus-out-event',self.gui_control.cb_tw_cdtext_message_lose_focus,self.project_id)

        labels = ["Preemphasis","Copy permitted"]
        options_frame,self.checkboxes = check_boxes_box("Options", labels, [1])

        vbox.pack_start(options_frame,False,False)


        spin_hbox = gtk.HBox (False,0)
        label = gtk.Label ("Default pregap:")

        value_as_string = default_pregap

        spin_adj1 = gtk.Adjustment(value=int(value_as_string[0]), lower=0, upper=10, step_incr=1, page_incr=0, page_size=0)
        spin_button1 = gtk.SpinButton (spin_adj1)
        spin_adj2 = gtk.Adjustment(value=int(value_as_string[1]), lower=0, upper=60, step_incr=1, page_incr=0, page_size=0)
        spin_button2 = gtk.SpinButton (spin_adj2)
        spin_adj3 = gtk.Adjustment(value=int(value_as_string[2]), lower=0, upper=60, step_incr=1, page_incr=0, page_size=0)
        spin_button3 = gtk.SpinButton (spin_adj3)

        #spin_button1.connect ("value-changed",self.gui_control.cv_propw_spinbutton1_changed,spin_button2,spin_button3,self.config_handler)
        #spin_button2.connect ("value-changed",self.gui_control.cv_propw_spinbutton2_changed,spin_button1,spin_button3,self.config_handler)
        #spin_button3.connect ("value-changed",self.gui_control.cv_propw_spinbutton3_changed,spin_button1,spin_button2,self.config_handler)

        spin_hbox.pack_start (label,False,False,15)
        spin_hbox.pack_end (spin_button3,False,False,5)
        spin_hbox.pack_end (spin_button2,False,False,5)
        spin_hbox.pack_end (spin_button1,False,False,5)

        vbox.pack_start (spin_hbox,False,False)
        vbox.pack_start(cd_text_frame,False,False)
        vbox.pack_start(gtk.HSeparator(),False,False)

        button_hbox = gtk.HBox (False,0)
        button_ok = gtk.Button ("Close",gtk.STOCK_CLOSE,True)
        button_ok.connect ("pressed",self.gui_control.cb_tw_close_window,self)
        button_hbox.pack_end(button_ok,False,False,10)
        vbox.pack_start(button_hbox,False,False)


#win = cdtext_track_window()
#win.show_window()
#gtk.main()