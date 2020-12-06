import gtk
import gobject
def get_icon (exten,icon_theme):

        if exten == "deb":
            file_name = "gnome-mime-application-x-deb"
        elif exten == "rpm":
            file_name = "gnome-mime-application-x-rpm"
        elif exten == "iso":
            file_name = "gnome-mime-application-x-cd-image"
        elif exten == "avi":
            file_name = "gnome-mime-video-x-msvideo"
        elif exten == "asf":
            file_name = "gnome-mime-video-x-ms-asf"
        elif exten == "mpg":
            file_name = "gnome-mime-video-mpeg"
        elif exten == "wmv":
            file_name = "gnome-mime-video-x-ms-wmv"
        elif exten == "mov":
            file_name = "gnome-mime-video-quicktime"
        elif exten == "sql":
            file_name = "gnome-mime-text-x-sql"
        elif exten == "sh":
            file_name = "gnome-mime-text-x-sh"
        elif exten == "java":
            file_name = "gnome-mime-text-x-java"
        elif exten == "c":
            file_name = "gnome-mime-text-x-csrc"
        elif exten == "h":
            file_name = "gnome-mime-text-x-c-headers"
        elif exten == "svg":
            file_name = "gnome-mime-image-svg"
        elif exten == "png":
            file_name = "gnome-mime-image-png"
        elif exten == "jpg":
            file_name = "gnome-mime-image-jpeg"
        elif exten == "bmp":
            file_name = "gnome-mime-image-bmp"
        elif exten == "gif":
            file_name = "gnome-mime-image-gif"
        elif exten == "ief":
            file_name = "gnome-mime-image-ief"
        elif exten == "tiff":
            file_name = "gnome-mime-image-tiff"
        elif exten == "wav":
            file_name = "gnome-mime-audio-x-wav"
        elif exten == "ra":
            file_name = "gnome-mime-audio-x-pn-realaudio"
        elif exten == "mp3":
            file_name = "gnome-mime-audio-x-mp3"
        elif exten == "ogg":
            file_name = "gnome-mime-application-ogg"
        elif exten == "zip":
            file_name = "gnome-mime-application-zip"
        elif exten == "bz2":
            file_name = "gnome-mime-application-x-bzip"
        elif exten == "gz":
            file_name = "gnome-mime-application-x-gzip"
        elif exten == "rar":
            file_name = "gnome-mime-application-x-rar"
        elif exten == "tar":
            file_name = "gnome-mime-application-x-tar"
        elif exten == "ppt":
            file_name = "gnome-mime-application-vnd.ms-powerpoint"
        elif exten == "xls":
            file_name = "gnome-mime-application-vnd.ms-excel"
        elif exten == "doc":
            file_name = "gnome-mime-application-vnd.ms-word"
        elif exten == "pdf":
            file_name = "gnome-mime-application-pdf"
        elif exten == "dvi":
            file_name = "gnome-mime-application-x-dvi"
        elif exten == "ps":
            file_name = "gnome-mime-application-postscript"
        elif exten == "jar":
            file_name = "gnome-mime-application-x-jar"
        elif exten == "sxw":
            file_name = "gnome-mime-application-vnd.sun.xml.writer"
        elif exten == "sxi":
            file_name = "gnome-mime-application-vnd.sun.xml.impress"
        elif exten == "sxc":
            file_name = "gnome-mime-application-vnd.sun.xml.calc"
        elif exten == "xml":
            file_name = "gnome-mime-text-xml"
        elif exten == "py":
            file_name = "gnome-mime-application-x-python"
        elif exten == "pyc":
            file_name = "gnome-mime-application-x-python-bytecode"
        else:
            file_name = "gnome-mime-application"

        try:
            dirIcon = icon_theme.load_icon(file_name,
                                                24,
                                                gtk.ICON_LOOKUP_FORCE_SVG)

        except gobject.GError, msg:
            try:
                dirIcon = icon_theme.load_icon("gnome-fs-regular",
                                                24,
                                                gtk.ICON_LOOKUP_FORCE_SVG)

            except gobject.GError, msg:
                try:
                    dirIcon = icon_theme.load_icon(file_name,
                                                    24,
                                                    gtk.ICON_LOOKUP_NO_SVG)

                except gobject.GError, msg:
                    try:
                        dirIcon = icon_theme.load_icon("gnome-fs-regular",
                                                        24,
                                                        gtk.ICON_LOOKUP_NO_SVG)
                    except     gobject.GError, msg:
                        print "exeption "+msg

        return dirIcon

def section_frame (label):
    frame = gtk.Frame()
    frame_label = gtk.Label()
    frame_label.set_markup ('<span weight="bold">'+label+'</span>')
    frame.set_label_widget(frame_label)
    frame.set_shadow_type(gtk.SHADOW_NONE)

    return frame

def radio_buttons_box (label,radio_labels,active,comment = None):
        frame_label = gtk.Label()
        frame_label.set_markup ('<span weight="bold">'+label+'</span>')
        frame = gtk.Frame()
        frame.set_label_widget(frame_label)
        frame.set_shadow_type(gtk.SHADOW_NONE)

        vbox_frame = gtk.VBox(False,0)
        vbox_frame.set_border_width (10)

        radio_button = {}
        radio_button[radio_labels[0]] = gtk.RadioButton(None, radio_labels[0])

        sub_radio_labels = radio_labels[1:]

        for radio_label in radio_labels:
            radio_button[radio_label] = gtk.RadioButton(radio_button[radio_labels[0]],radio_label)
            vbox_frame.pack_start(radio_button[radio_label],False,True)

        if comment != None:
            label = gtk.Label(comment)
            label.set_line_wrap(True)
            vbox_frame.pack_start(label,False,False)

        frame.add(vbox_frame)
        radio_button[radio_labels[int(active)]].set_active(True)
        return frame,radio_button

def check_boxes_box (label,check_labels,activated,comment = None):
        frame = gtk.Frame()
        frame_label = gtk.Label()
        frame_label.set_markup ('<span weight="bold">'+label+'</span>')
        frame.set_label_widget(frame_label)
        frame.set_shadow_type(gtk.SHADOW_NONE)

        vbox_frame = gtk.VBox(False,0)
        vbox_frame.set_border_width (10)

        check_button = {}

        for check_label in check_labels:
            check_button[check_label] = gtk.CheckButton(check_label)
            vbox_frame.pack_start(check_button[check_label],False,True)

        if comment != None:
            label = gtk.Label(comment)
            label.set_line_wrap(True)
            vbox_frame.pack_start(label,False,False)

        frame.add(vbox_frame)

        for active in activated:
            check_button[check_labels[int(active)]].set_active(True)
        return frame,check_button


def devices_options_box (options):

    devices_treestore = gtk.TreeStore(gobject.TYPE_STRING,
                                      gobject.TYPE_STRING)

    keys = options[0]
    dict = options [1]
    for key in keys:
        sub_sub_iter = devices_treestore.append(None)
        devices_treestore.set (sub_sub_iter,0,key+"\t",1,dict[key])


    devices_treeview = gtk.TreeView (devices_treestore)
    devices_treeview.set_rules_hint(True)
    devices_treeview.set_headers_visible(False)

    column1 = gtk.TreeViewColumn()
    cell_pixbuf = gtk.CellRendererPixbuf()
    column1.pack_start(cell_pixbuf,False)
    #column1.set_cell_data_func(cell_pixbuf, self.gui_control.cb_propw_change_pixbuf)

    cell_text = gtk.CellRendererText()
    column1.pack_start(cell_text,True)
    column1.add_attribute(cell_text,'markup',0)

    column2 = gtk.TreeViewColumn()
    cell_text = gtk.CellRendererText()
    column2.pack_start(cell_text,True)
    column2.add_attribute(cell_text,'text',1)

    devices_treeview.append_column(column1)
    devices_treeview.append_column(column2)
    devices_treeview.expand_all()

    sw = gtk.ScrolledWindow()
    sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    sw.add (devices_treeview)

    setup_hbox =  gtk.HBox (True,10)
    setup_hbox.set_border_width(10)
    setup_hbox.pack_start(sw,True,True)

    return setup_hbox

#===============================================================================
# icons type:
#    icons = {"ICONS_DIRECTORY1":"label_icon1",
#             "ICONS_DIRECTORY2":"label_icon2",
#             ...,
#             "ICONS_DIRECTORYN":"label_iconN"
#             }
#
# callback_function:
#    callback when icon clicked
#===============================================================================
def evolution_icon_box (icons, ordered_icons_url, default_label_selected, callback_function):

        frame_event_box = gtk.EventBox()
        frame = gtk.Frame()
        frame_event_box.add(frame)

        frame.set_shadow_type(gtk.SHADOW_IN)

        frame__vbox = gtk.VBox(False,0)
        frame__vbox.set_size_request(120,-1)
        frame.add(frame__vbox)
        frame_event_box.modify_bg (gtk.STATE_NORMAL,frame_event_box.get_colormap().alloc_color('white'))
        icon_boxes = []

        for image_url in ordered_icons_url:
            label = icons[image_url]
            event_box = gtk.EventBox()
            vbox = gtk.VBox (False,0)
            vbox.set_size_request(-1,75)
            event_box.add (vbox)
            event_box.modify_bg (gtk.STATE_NORMAL,event_box.get_colormap().alloc_color('white'))
            event_box.modify_bg (gtk.STATE_SELECTED,event_box.get_colormap().alloc_color('#7b96ac'))
            event_box.set_events(gtk.gdk.ALL_EVENTS_MASK)
            #event_box.connect("button_press_event", callback_function,icons)
            if label == default_label_selected:
                event_box.set_state(gtk.STATE_SELECTED)

            image = gtk.Image()
            image.set_from_file(image_url)
            label = gtk.Label (label)

            vbox.pack_start(image,False,True)
            vbox.pack_start(label,False,True)

            icon_boxes.append (event_box)

        for icon_box in icon_boxes:
            frame__vbox.pack_start (icon_box,False,False)
            icon_box.connect("button_press_event", callback_function,icon_boxes)

        return frame_event_box

def error_window (parent_window,error_msg):
    errorwindow = gtk.MessageDialog(
                        parent_window,
                        flags=0,
                        type=gtk.MESSAGE_ERROR,
                        buttons=gtk.BUTTONS_CLOSE,
                        message_format=error_msg
                        )
    errorwindow.connect ("response",dialwin_ok)
    errorwindow.run()

def dialwin_ok (dialog, id, data=None):
        dialog.hide()

def dialwin_destroy (dialog, id, data=None):
        dialog.destroy()

def cursor_watch(window):
        cursor = gtk.gdk.Cursor(gtk.gdk.WATCH)
        window.window.set_cursor(cursor)
        while gtk.events_pending():
            gtk.main_iteration()

def cursor_left_arrow (window):
        cursor = gtk.gdk.Cursor(gtk.gdk.TOP_LEFT_ARROW)
        window.window.set_cursor(cursor)
        while gtk.events_pending():
            gtk.main_iteration()


class bubbledisk_progressbar:
    # Progress Bar
    progressbar = None
    graduationbar = None
    red_progressbar = None
    graduation_type = None

    media_type = None
    grad_unit = "mo"

    def __init__ (self,graduation_type,media_type):
        self.graduation_type = graduation_type
        self.media_type = media_type

        self.progress_frame = gtk.Frame()
        self.progress_frame.set_shadow_type(gtk.SHADOW_ETCHED_IN)

        prog_grad_vbox = gtk.VBox(False,0)

        vbox_progressbar = gtk.VBox(False,0)
        hbox_graduationbar = gtk.HBox(False,0)
        hbox_graduationbar.set_border_width(0)
        hbox_graduationbar.set_size_request(-1,16)

        self.progressbar = self.progressbar_box()
        self.graduationbar = self.graduationbar_box()
        prog_grad_vbox.pack_start(self.progressbar,False,True)
        prog_grad_vbox.pack_start(self.graduationbar,False,True)

        #self.progress_frame.set_border_width(2)
        self.progress_frame.add(prog_grad_vbox)

    def progressbar_box (self):
        progressbar = gtk.ProgressBar(adjustment=None)
        progressbar.set_fraction(0.0)
        progressbar.set_size_request(-1,20)
        progressbar.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)

        if self.media_type == "cdrom":
            if self.graduation_type == "mo":
                progressbar.set_text("0 Mo")
            else:
                progressbar.set_text("Available: 78:00 min of 78 min")


        #hbox.pack_start(self.progressbar,False,False)

        return progressbar

    def graduationbar_box (self):
        # Graduation Bar
        grad_box = gtk.HBox(True,0)

        graduation = []
        if self.media_type == "cdrom":
            if self.graduation_type == "mo":
                graduation = ["0","100","200","300","400","500","600","700","800","900"]
            else:
                graduation = ["0","10","20","30","40","50","60","70","80","90"]
        elif self.media_type == "dvd_one_layer":
            graduation = ["0","500","1000","1500","2000","2500","3000","3500","4000","4500"]
        elif self.media_type == "dvd_two_layer":
            graduation = ["0","1000","2000","3000","4000","5000","6000","7000","8000","9000"]

        for grad in graduation:
            text = '|' + grad
            label = gtk.Label(text)
            #label.show()
            hbox = gtk.HBox(False,0)
            hbox.pack_start(label,False,True)
            #hbox.show()
            grad_box.pack_start(hbox,True,True)

        return grad_box

    def get(self):
        return self.progress_frame

    """
    @value: project's size in Kb if data Project OR in Sec if Audio project
    """
    def set_fraction (self,value):
        if self.media_type == "cdrom":
            if self.graduation_type == "mo":
                self.progressbar.set_fraction (float(value)/(1024*1024))
            else:
                self.progressbar.set_fraction (float(value)/6000000)
        elif self.media_type == "dvd_one_layer":
            self.progressbar.set_fraction (float(value)/(4500*1024*1024))
        elif self.media_type == "dvd_two_layer":
            self.progressbar.set_fraction (float(value)/(9000*1024*1024))

    def set_text (self,text):
        self.progressbar.set_text (text)

    def set_audio_free_space (self,(min,sec,milli),total_minutes=80):
        self.progressbar.set_text("Available: %02d:%02d min of %d min"%(min,sec,total_minutes))


def dialog_box (message_type,message,parent_window):
    dialog = gtk.MessageDialog(parent_window,
                                 gtk.DIALOG_DESTROY_WITH_PARENT,
                                 message_type, gtk.BUTTONS_OK,
                                  message)
    # Close dialog on user response
    return dialog

class bubble_dialogs:
    dialogs = {}

    def add_dialog (self,msg,parent=None):
        dialog_box = gtk.MessageDialog(parent,
                                         gtk.DIALOG_DESTROY_WITH_PARENT,
                                         gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                                          msg)
        self.dialogs[msg] = dialog_box

    def get_dialog (self,msg):
        return self.dialogs[msg]

    def set_dialog (self,msg,dialog_box):
        self.dialogs[msg] = dialog_box

    def del_dialog (self,msg):
        del self.dialogs[msg]