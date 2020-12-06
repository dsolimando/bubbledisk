import gtk
import gobject

from re import compile,match

from bubble_windows import window

class blankdisk_window (window):

    gui_control = None
    gui_view = None

    device_manager = None
    application_manager = None

    icon_theme = None

    config_handler = None

    devices = {}

    def __init__(self,gui_control,gui_view,dev_manager,app_manager,config_handler):

        self.gui_control = gui_control
        self.gui_view = gui_view

        self.config_handler = config_handler

        self.device_manager = dev_manager
        self.application_manager = app_manager

        self.window = gtk.Window (gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request (450,350)
        self.window.set_title ("Blank a disK")
        #self.window.connect("delete_event",self.gui_control.cb_pw_hide_window)

        main_box = gtk.VBox (False,0)

        south_box = gtk.HBox (False,0)
        south_box.set_border_width (8)
        main_box.pack_start (south_box,True,True)

        east_box = gtk.VBox (False,0)
        west_box = gtk.VBox(False,10)
        south_box.pack_start (east_box,True,True)
        south_box.pack_start (gtk.VSeparator(),False,True,10)
        south_box.pack_start (west_box,False,False)



        device_frame = self.section_frame("Burning Device")
        east_box.pack_start(device_frame,False,False)
        device_hbox = gtk.HBox (False,0)
        device_hbox.set_border_width (10)
        device_frame.add (device_hbox)

        self.device_combo_box = gtk.ComboBox()
        self.device_combo_box = gtk.combo_box_new_text()

#        for key,dev in self.device_manager.get_disk_devices().items():
#            device = self.device_manager.get_drive_features(key)
#            if device.write_cdr:
#                print device
#                self.devices[dev.get_display_name()] = key
#                self.device_combo_box.append_text(dev.get_display_name())

        for writer in self.device_manager.writers:
            self.devices[writer.get_name_for_display()] = writer.get_device()
            self.device_combo_box.append_text(writer.get_name_for_display())

        self.device_combo_box.set_active(0)

        self.speed_combo_box = gtk.ComboBox()
        self.speed_combo_box = gtk.combo_box_new_text()
        self.speed_combo_box.append_text("Auto")

        device = self.device_manager.get_drive_features(self.device_manager.get_current_writer().get_device())
        for speed in device.cd_speeds:
            self.speed_combo_box.append_text(speed)
        self.speed_combo_box.set_active(0)

        device_hbox.pack_start(self.device_combo_box,True,True,5)
        device_hbox.pack_start(self.speed_combo_box,False,False,5)

        mode_frame = self.section_frame("Blanking Mode")
        east_box.pack_start(mode_frame,False,False)
        mode_hbox = gtk.HBox (False,0)
        mode_hbox.set_border_width (10)
        mode_frame.add (mode_hbox)

        self.mode_combo_box = gtk.ComboBox()
        self.mode_combo_box = gtk.combo_box_new_text()
        self.mode_combo_box.append_text("Minimal")
        self.mode_combo_box.append_text("Full")
        self.mode_combo_box.set_active(0)

        mode_hbox.pack_start(self.mode_combo_box,True,True,5)

        info_frame = self.section_frame("Blanking Process Infos")
        east_box.pack_start(info_frame,True,True)
        info_hbox = gtk.HBox (True,0)
        info_hbox.set_border_width (10)
        info_frame.add (info_hbox)

        self.infos_treestore = gtk.TreeStore(gobject.TYPE_STRING)

        self.infos_treeview = gtk.TreeView (self.infos_treestore)
        self.infos_treeview.set_headers_visible(False)

        column1 = gtk.TreeViewColumn()
        cell_pixbuf = gtk.CellRendererPixbuf()
        column1.pack_start(cell_pixbuf,False)
        column1.set_cell_data_func(cell_pixbuf, self.gui_control.cb_writing_window_change_pixbuf)

        cell_text = gtk.CellRendererText()
        column1.pack_start(cell_text,True)
        column1.add_attribute(cell_text,'markup',0)

        self.infos_treeview.append_column(column1)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add (self.infos_treeview)

        info_hbox.pack_start (sw,False,True,5)

        #west_box.set_border_width (10)
        self.blank_button = gtk.Button ("Blank",gtk.STOCK_CLEAR,True)
        self.blank_button.connect ("pressed",
                                self.gui_control.cb_blankdisk_window_blank,
                                self.device_combo_box,
                                self.speed_combo_box,
                                self.mode_combo_box,
                                self)

        self.close_button = gtk.Button ("Close",gtk.STOCK_CLOSE,True)
        self.close_button.connect ("pressed",self.gui_control.cb_hide_blankdisk_window )
        self.cancel_button = gtk.Button ("Cancel",gtk.STOCK_CANCEL,True)
        self.cancel_button.connect ("pressed",self.gui_control.cb_hide_blankdisk_window )
        west_box.pack_start (self.blank_button,False,False)
        west_box.pack_start (self.cancel_button,False,False)
        west_box.pack_start (self.close_button,False,False)
        self.window.add(main_box)


    def section_frame (self,label):
        frame = gtk.Frame()
        frame_label = gtk.Label()
        frame_label.set_markup ('<span weight="bold">'+label+'</span>')
        frame.set_label_widget(frame_label)
        frame.set_shadow_type(gtk.SHADOW_NONE)

        return frame

    def update (self,output):
        regexp = compile (".*\s*Device\stype\s*:\s*(.*)")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"Checking Device informations...")
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile (".*Using\sgeneric.*(.*)")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"Choosing correct Driver...")
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)


        regexp = compile (".*Starting to write.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"Starting to Blank Disk...")
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile (".*\s*(\d)\sseconds.*")
        matched = regexp.match(output)
        if matched is not None:
            print matched.groups()
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"\t in %s seconds..." % matched.group(1))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile ("Performing.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"Performing OPC...")
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile ("Blanking PMA.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"Blanking Disk...")
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile ("Blanking time:\s*(\d*)\.(\d*)s.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"Disk cleaned successfully in %s,%s seconds"%(matched.group(1),matched.group(2)))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

    def hide_window (self,otheruse=None):
        if otheruse == None:
            self.blank_button.hide()
            self.cancel_button.hide()
            self.close_button.show()
            cursor = gtk.gdk.Cursor(gtk.gdk.TOP_LEFT_ARROW)
            self.window.window.set_cursor(cursor)
        else:
            self.window.hide_all()

    def show_window (self,otheruse=None):
        print otheruse
        if otheruse == None:
            self.blank_button.set_sensitive(False)
            self.cancel_button.set_sensitive(False)
            cursor = gtk.gdk.Cursor(gtk.gdk.WATCH)
            self.window.window.set_cursor(cursor)
        else:
            self.blank_button.set_sensitive(True)
            self.cancel_button.set_sensitive(True)
            self.infos_treestore.clear()
            self.window.show_all()
            self.close_button.hide()
            self.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)