import gtk
import gobject

from bubble_windows import window
from constants.config import *

class properties_window (window):

    gui_control = None
    gui_view = None

    device_manager = None
    application_manager = None

    icon_theme = None
    icons = {"Writing":"gnome-dev-cdrom",
             "Devices":"gnome-fs-blockdev",
             "Applications":"gnome-fs-executable",
             "CDDB":"gnome-fs-bookmark",
             "Misc":"gnome-dev-symlink"}

    icons_list = ["Writing","Devices","Applications","CDDB","Misc"]

    window = None
    icon_boxes = []
    options_frames = {"Writing":None,
                      "Devices":None,
                      "Applications":None,
                      "CDDB":None,
                      "Misc":None}
    banner_image = {}

    backends_treeview = None

    config_handler = None

    common_tools = None

    def __init__(self,gui_control,gui_view,dev_manager,app_manager,config_handler,common_tools):
        self.gui_control = gui_control
        self.gui_view = gui_view

        self.config_handler = config_handler
        self.common_tools = common_tools

        self.device_manager = dev_manager
        self.application_manager = app_manager

        self.icon_theme = gtk.icon_theme_get_for_screen(gtk.gdk.screen_get_default())

        self.window = gtk.Window (gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request (700,550)
        self.window.set_title ("Preferences")
        #self.window.connect("delete_event",self.gui_control.cb_pw_hide_window)

        self.get_images ()

        mainBox = gtk.VBox (False,0)

        mainBox_north = gtk.HBox (False,10)
        mainBox_north.set_border_width (10)
        frame_event_box = self.evolution_icon_box (self.icons_list,self.icons)

        mainBox_south = self.action_butons_box ()
        mainBox_south.set_border_width (10)


        mainBox_north.pack_start (frame_event_box,False,False)

        self.options_frames["Writing"] = self.writing_options_frame()
        self.options_frames["Devices"] = self.devices_options_frame()
        self.options_frames["Applications"] = self.apps_options_frame()
        self.options_frames["CDDB"] = self.cddb_options_frame()
        self.options_frames["Misc"] = self.misc_options_frame()

        for keys in self.options_frames.keys():
            mainBox_north.pack_start (self.options_frames[keys],True,True)



        mainBox.pack_start(mainBox_north,True,True)
        mainBox.pack_start(gtk.HSeparator(),False,False)
        mainBox.pack_start(mainBox_south,False,False)

        self.window.add(mainBox)

    def show_frame (self,frame):
        for keys in self.options_frames.keys():
            self.options_frames[keys].hide_all()

        self.options_frames[frame].show_all()

    def get_images (self):
        self.banner_image["writing"] = gtk.Image()
        self.banner_image["writing"].set_from_file (THEMES_DIR + "/standard/writing_banner.svg")

        self.banner_image["Devices"] = gtk.Image()
        self.banner_image["Devices"].set_from_file (THEMES_DIR + "/standard/devices_banner.svg")

        self.banner_image["Applications"] = gtk.Image()
        self.banner_image["Applications"].set_from_file (THEMES_DIR + "/standard/apps_banner.svg")

        self.banner_image["CDDB"] = gtk.Image()
        self.banner_image["CDDB"].set_from_file (THEMES_DIR + "/standard/cddb_banner.svg")

        self.banner_image["Misc"] = gtk.Image()
        self.banner_image["Misc"].set_from_file (THEMES_DIR + "/standard/misc_banner.svg")

    def action_butons_box (self):
        hbox = gtk.HBox(False,10)
        close_button = gtk.Button ("Ok",gtk.STOCK_CLOSE,True)
        close_button.connect ("pressed",self.gui_control.cb_propw_ok)

        hbox.pack_end(close_button,False,False)

        return hbox

    def evolution_icon_box (self,option_list,icon_list):
        frame_event_box = gtk.EventBox()
        frame = gtk.Frame()
        frame_event_box.add(frame)

        frame.set_shadow_type(gtk.SHADOW_IN)
        frame__vbox = gtk.VBox(False,0)
        frame__vbox.set_size_request(110,-1)
        frame.add(frame__vbox)
        frame_event_box.modify_bg (gtk.STATE_NORMAL,frame_event_box.get_colormap().alloc_color('white'))

        for option in option_list:
            event_box = gtk.EventBox()
            vbox = gtk.VBox (False,0)
            vbox.set_size_request(-1,75)
            event_box.add (vbox)
            event_box.modify_bg (gtk.STATE_NORMAL,event_box.get_colormap().alloc_color('white'))
            event_box.modify_bg (gtk.STATE_SELECTED,event_box.get_colormap().alloc_color('#7b96ac'))
            event_box.set_events(gtk.gdk.ALL_EVENTS_MASK)
            event_box.connect("button_press_event", self.__cb_modify_position )
            if option == "Writing":
                event_box.set_state(gtk.STATE_SELECTED)

            icon= self.icon_theme.load_icon(icon_list[option],
                                                    48,
                                                    gtk.ICON_LOOKUP_NO_SVG)
            label = gtk.Label (option)
            image = gtk.Image()
            image.set_from_pixbuf(icon)
            vbox.pack_start(image,False,True)
            vbox.pack_start(label,False,True)

            self.icon_boxes.append (event_box)

        for icon_box in self.icon_boxes:
            frame__vbox.pack_start (icon_box,False,False)

        return frame_event_box

    def writing_options_frame (self):
        frame = gtk.Frame ()
        main_vbox = gtk.VBox (False,10)

        banner_frame = self.banner_box("writing")
        audio_frame = self.section_frame ("Audio Project")
        audio_hbox = gtk.HBox (False,0)
        label = gtk.Label ("Default pregap:")

        value_from_gconf = self.config_handler.get ("writing/pregap")
        value_as_string = str(value_from_gconf)

        spin_adj1 = gtk.Adjustment(value=int(value_as_string[0]), lower=0, upper=10, step_incr=1, page_incr=0, page_size=0)
        spin_button1 = gtk.SpinButton (spin_adj1)
        spin_adj2 = gtk.Adjustment(value=int(value_as_string[1]), lower=0, upper=60, step_incr=1, page_incr=0, page_size=0)
        spin_button2 = gtk.SpinButton (spin_adj2)
        spin_adj3 = gtk.Adjustment(value=int(value_as_string[2]), lower=0, upper=60, step_incr=1, page_incr=0, page_size=0)
        spin_button3 = gtk.SpinButton (spin_adj3)

        spin_button1.connect ("value-changed",self.gui_control.cv_propw_spinbutton1_changed,spin_button2,spin_button3,self.config_handler)
        spin_button2.connect ("value-changed",self.gui_control.cv_propw_spinbutton2_changed,spin_button1,spin_button3,self.config_handler)
        spin_button3.connect ("value-changed",self.gui_control.cv_propw_spinbutton3_changed,spin_button1,spin_button2,self.config_handler)

        audio_hbox.set_border_width (10)
        audio_hbox.pack_start (label,False,False)
        audio_hbox.pack_end (spin_button3,False,False,5)
        audio_hbox.pack_end (spin_button2,False,False,5)
        audio_hbox.pack_end (spin_button1,False,False,5)

        audio_frame.add (audio_hbox)

        data_frame = self.section_frame ("Data Project")

        selected_boxes = []
        if self.config_handler.get ("writing/addhiddenfiles"):
            selected_boxes.append(0)
        if self.config_handler.get ("writing/addsystemfiles"):
            selected_boxes.append(1)

        data_frame,data_opt_boxes = self.check_boxes_box ("Data Project",["Add hidden files",
                                                                   "Add system files"],selected_boxes)

        data_opt_boxes["Add hidden files"].connect ("toggled",self.gui_control.cb_propw_check_box_toggled,self.config_handler,"writing/addhiddenfiles")
        data_opt_boxes["Add system files"].connect ("toggled",self.gui_control.cb_propw_check_box_toggled,self.config_handler,"writing/addsystemfiles")

        selected_boxes = []
        if self.config_handler.get ("writing/overburning"):
            selected_boxes.append(0)
        if self.config_handler.get ("writing/eject"):
            selected_boxes.append(1)
        if self.config_handler.get ("writing/blankcdrw"):
            selected_boxes.append(2)
        if self.config_handler.get ("writing/bufferunderrun"):
            selected_boxes.append(3)
        if self.config_handler.get ("writing/writespeedcontrol"):
            selected_boxes.append(3)

        misc_frame,misc_opt_boxes = self.check_boxes_box ("Miscellaneous",["Allow overburning",
                                                                   "Eject disk after write process",
                                                                   "Automatically blank CD-RW's and DVD-RW's",
                                                                   "Enable buffer under run protection",
                                                                   "Enable writing speed control"],selected_boxes)
        misc_opt_boxes["Allow overburning"].connect ("toggled",self.gui_control.cb_propw_check_box_toggled,self.config_handler,"writing/overburning")
        misc_opt_boxes["Eject disk after write process"].connect ("toggled",self.gui_control.cb_propw_check_box_toggled,self.config_handler,"writing/eject")
        misc_opt_boxes["Automatically blank CD-RW's and DVD-RW's"].connect ("toggled",self.gui_control.cb_propw_check_box_toggled,self.config_handler,"writing/blankcdrw")
        misc_opt_boxes["Enable buffer under run protection"].connect ("toggled",self.gui_control.cb_propw_check_box_toggled,self.config_handler,"writing/bufferunderrun")
        misc_opt_boxes["Enable writing speed control"].connect ("toggled",self.gui_control.cb_propw_check_box_toggled,self.config_handler,"writing/writespeedcontrol")

        main_vbox.pack_start(banner_frame,False,True)
        main_vbox.pack_start(audio_frame,False,True,5)
        main_vbox.pack_start(data_frame,False,True)
        main_vbox.pack_start(misc_frame,False,True,5)
        frame.add (main_vbox)

        return frame

    def devices_options_frame (self):
        frame = gtk.Frame ()
        main_vbox = gtk.VBox (False,10)

        banner_frame = self.banner_box("Devices")
        setup_frame = self.section_frame ("CD/DVD Drives")


        main_vbox.pack_start(banner_frame,False,True)
        main_vbox.pack_start(setup_frame,True,True,5)

        devices_treestore = gtk.TreeStore(gobject.TYPE_STRING,
                                          gobject.TYPE_STRING)
        iter =  devices_treestore.append(None)
        devices_treestore.set (iter,0,"Readers",1,"")

        for dev in self.device_manager.devices.values():
            device = self.device_manager.get_drive_features(dev.get_device_path())
            if not device.write_cdr:
                sub_iter = devices_treestore.append(iter)
                devices_treestore.set (sub_iter,0,device.vendor+" "+device.identifikation,1,"")

                keys,dict = device.print_friendly_devices_params ()

                for key in keys:
                    sub_sub_iter = devices_treestore.append(sub_iter)
                    devices_treestore.set (sub_sub_iter,0,key,1,dict[key])

        iter =  devices_treestore.append(None)
        devices_treestore.set (iter,0,"Writers",1,"")
        for dev in self.device_manager.writers:
            device = self.device_manager.get_drive_features(dev.get_device())
            sub_iter = devices_treestore.append(iter)
            devices_treestore.set (sub_iter,0,'<span weight="bold">'+device.vendor+" "+device.identifikation+'</span>',1,"")


            keys,dict = device.print_friendly_devices_params ()
            for key in keys:
                sub_sub_iter = devices_treestore.append(sub_iter)
                devices_treestore.set (sub_sub_iter,0,key,1,dict[key])


        devices_treeview = gtk.TreeView (devices_treestore)
        devices_treeview.set_rules_hint(True)
        devices_treeview.set_headers_visible(False)

        column1 = gtk.TreeViewColumn()
        cell_pixbuf = gtk.CellRendererPixbuf()
        column1.pack_start(cell_pixbuf,False)
        column1.set_cell_data_func(cell_pixbuf, self.gui_control.cb_propw_change_pixbuf)

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
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add (devices_treeview)

        setup_hbox =  gtk.HBox (True,10)
        setup_hbox.set_border_width(10)
        setup_hbox.pack_start(sw,True,True,20)
        setup_frame.add(setup_hbox)

        frame.add (main_vbox)

        return frame

    def __build_backends_treestore (self):
        backends_treestore = gtk.TreeStore(gobject.TYPE_STRING,
                                           gobject.TYPE_STRING,
                                           gobject.TYPE_STRING)

        for app in self.application_manager.applications_needed:
            iter = backends_treestore.append (None)
            backends_treestore.set (iter,0,'<span weight="bold">'+app+'</span>',1,"",2,"FALSE")

            infos = self.application_manager.get_application_infos (app)

            sub_iter = backends_treestore.append (iter)
            if infos:
                backends_treestore.set (sub_iter,0,infos[1],1,infos[2],2,"TRUE")
            else:
                backends_treestore.set (sub_iter,0,'<span foreground="#FF0000">Not installed</span>',1,"",2,"TRUE")

        return backends_treestore

    def refresh_treestore (self):
        model = self.__build_backends_treestore()
        self.backends_treeview.set_model (model)


    def apps_options_frame (self):
        frame = gtk.Frame ()
        main_vbox = gtk.VBox (False,5)


        banner_frame = self.banner_box("Applications")

        notebook = gtk.Notebook()
        notebook.set_scrollable(True)
        notebook.set_tab_pos (gtk.POS_TOP)

        prog_details_box = self.section_frame("Backends details")
        prog_details_vbox = gtk.VBox (True,0)
        prog_details_vbox.pack_start (prog_details_box,True,True,10)

        backend_treestore = self.__build_backends_treestore ()

        ###########
        self.backends_treeview = gtk.TreeView (backend_treestore)
        self.backends_treeview.set_rules_hint(True)

        column1 = gtk.TreeViewColumn("Path")
        cell_pixbuf = gtk.CellRendererPixbuf()
        column1.pack_start(cell_pixbuf,False)
        column1.set_cell_data_func(cell_pixbuf, self.gui_control.cb_propw_change_pixbuf_for_backends)

        cell_text = gtk.CellRendererText()
        column1.pack_start(cell_text,True)
        column1.add_attribute(cell_text,'markup',0)
        column1.set_min_width(200)

        column2 = gtk.TreeViewColumn("Version")
        cell_text = gtk.CellRendererText()
        column2.pack_start(cell_text,True)
        column2.add_attribute(cell_text,'text',1)
        column2.set_max_width(220)

        self.backends_treeview.append_column(column1)
        self.backends_treeview.append_column(column2)
        self.backends_treeview.expand_all()

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add (self.backends_treeview)

        setup_hbox =  gtk.HBox (True,10)
        setup_hbox.set_border_width(15)
        setup_hbox.pack_end(sw,True,True)

        vbox = gtk.VBox (False,5)
        vbox.pack_start (setup_hbox,True,True)


        prog_details_box.add (vbox)
        ###########
        search_paths_box = self.section_frame ("Search Path")

        path_form_vbox = gtk.VBox (False,0)
        new_path_entry = gtk.Entry()
        paths_list_hbox = gtk.HBox(False,5)

        path_form_vbox.pack_start(new_path_entry,False,False)
        path_form_vbox.pack_start(paths_list_hbox,True,True,10)
        path_form_vbox.set_border_width(10)
        search_paths_box.add (path_form_vbox)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        paths_list_hbox.pack_start(sw,True,True)

        self.path_list_liststore = gtk.ListStore(gobject.TYPE_STRING)
        path_list_treeview = gtk.TreeView(self.path_list_liststore)

        for dir in self.application_manager.path:
            iter = self.path_list_liststore.append()
            self.path_list_liststore.set(iter,
                0,dir
                )

        path_list_treeview.set_rules_hint(True)
        path_list_treeview.set_headers_visible(False)
        sw.add(path_list_treeview)
        self.paths_column_textrenderer = gtk.CellRendererText()
        tvcolumn = gtk.TreeViewColumn ("text",self.paths_column_textrenderer,text=0)
        path_list_treeview.append_column(tvcolumn)


        search_paths_box_vbox = gtk.VBox (True,0)
        search_paths_box_vbox.pack_start (search_paths_box,False,True,15)

        notebook.append_page (prog_details_vbox,gtk.Label("Backends"))
        notebook.append_page (search_paths_box_vbox,gtk.Label("Search Path"))

        notebook_hbox = gtk.HBox (True,0)
        notebook_hbox.pack_start (notebook,False,True,10)
        notebook_hbox.set_border_width(10)

        buttons_vbox = gtk.VBox(False,0)

        button_add = gtk.Button ("Add",gtk.STOCK_ADD,True)
        button_add.connect ("pressed",self.gui_control.cb_propw_add,self.path_list_liststore,new_path_entry,self.config_handler,"apps/path")

        button_remove = gtk.Button ("Remove",gtk.STOCK_DELETE,True)
        button_remove.connect ("pressed",self.gui_control.cb_propw_remove,path_list_treeview,self.config_handler,"apps/path")

        button_up = gtk.Button ("Up",gtk.STOCK_GO_UP,True)
        button_up.connect ("pressed",self.gui_control.cb_propw_up,path_list_treeview,self.config_handler,"apps/path")

        button_down = gtk.Button ("Down",gtk.STOCK_GO_DOWN,True)
        button_down.connect ("pressed",self.gui_control.cb_propw_down,path_list_treeview,self.config_handler,"apps/path")
        buttons_vbox.pack_start (button_add,False,False,3)
        buttons_vbox.pack_start (button_remove,False,False,3)
        buttons_vbox.pack_start (button_up,False,False,3)
        buttons_vbox.pack_start (button_down,False,False,3)
        paths_list_hbox.pack_start(buttons_vbox,False,False)

        main_vbox.pack_start(banner_frame,False,True)
        main_vbox.pack_start(notebook_hbox,True,True)
        refresh_hbox = gtk.HBox (False,0)
        refresh_button  = gtk.Button ("Refresh",gtk.STOCK_REFRESH,True)
        refresh_button.connect ("pressed",self.gui_control.cb_propw_refresh)
        #refresh_hbox.set_border_width(10)
        refresh_hbox.pack_end (refresh_button,False,False,20)
        main_vbox.pack_start (refresh_hbox,False,False,10)

        frame.add (main_vbox)

        return frame

    def cddb_options_frame (self):
        frame = gtk.Frame ()
        main_vbox = gtk.VBox (False,5)

        banner_frame = self.banner_box("CDDB")

        notebook = gtk.Notebook()
        notebook.set_scrollable(True)
        notebook.set_tab_pos (gtk.POS_TOP)

#===============================================================================
#        Remote CDDB Tab
#===============================================================================
        remote_cddb_options_frame,boxes = self.check_boxes_box ("Enable Remote CDDB",["retrieve CDDB CD-TEXT data while copying"],[0])
        boxes["retrieve CDDB CD-TEXT data while copying"].connect ("toggled",
                                                                    self.gui_control.cb_propw_enable_cddb_check_box_toggled,
                                                                    self.config_handler,
                                                                    "cddb/use_cddb_servers")

        cddb_servers_box = self.section_frame ("CDDB Servers")

        server_form_vbox = gtk.VBox (False,0)
        url_entry = gtk.Entry()
        server_list_hbox = gtk.HBox(False,5)

        server_params_hbox = gtk.HBox(False,5)
        server_label = gtk.Label("Server:")

        protocol_combobox = gtk.combo_box_new_text()
        protocol_combobox.append_text("http")
        protocol_combobox.set_active(0)

        spin_adj1 = gtk.Adjustment(value=80, lower=0, upper=10000, step_incr=1, page_incr=0, page_size=0)
        spin_button1 = gtk.SpinButton (spin_adj1)

        server_params_hbox.pack_start(server_label,False,False)
        server_params_hbox.pack_start(protocol_combobox,False,False,5)
        server_params_hbox.pack_start(url_entry,True,True,5)
        server_params_hbox.pack_start(spin_button1,False,True,5)

        server_form_vbox.pack_start(server_params_hbox,False,False)
        server_form_vbox.pack_start(server_list_hbox,True,True,10)
        server_form_vbox.set_border_width(10)
        cddb_servers_box.add (server_form_vbox)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        server_list_hbox.pack_start(sw,True,True)

        self.server_list_liststore = gtk.ListStore(gobject.TYPE_STRING,
                                                    gobject.TYPE_STRING,
                                                    gobject.TYPE_STRING)

        server_list_treeview = gtk.TreeView(self.server_list_liststore)

        servers = self.config_handler.get ("cddb/servers")
        server_list_temp = servers.split(",")
        server_list = []
        for server in server_list_temp:
            server_list.append(self.common_tools.split_url(server))

        for server in server_list:
            iter = self.server_list_liststore.append()
            self.server_list_liststore.set(iter,
                0,server[0],
                1,server[1],
                2,server[2],
                )

        server_list_treeview.set_rules_hint(True)
        #server_list_treeview.set_headers_visible(False)
        sw.add(server_list_treeview)

        self.server_protocol_textrenderer = gtk.CellRendererText()
        self.server_url_textrenderer = gtk.CellRendererText()
        self.server_port_textrenderer = gtk.CellRendererText()

        tvcolumn1 = gtk.TreeViewColumn ("Protocol",self.server_protocol_textrenderer,text=0)
        tvcolumn2 = gtk.TreeViewColumn ("Server Hostname",self.server_url_textrenderer,text=1)
        tvcolumn3 = gtk.TreeViewColumn ("Port",self.server_port_textrenderer,text=2)

        server_list_treeview.append_column(tvcolumn1)
        server_list_treeview.append_column(tvcolumn2)
        server_list_treeview.append_column(tvcolumn3)

        cddb_servers_box_vbox = gtk.VBox (False,0)
        cddb_servers_box_vbox.pack_start (remote_cddb_options_frame,False,False,15)
        cddb_servers_box_vbox.pack_start (cddb_servers_box,True,True)

        notebook.append_page (cddb_servers_box_vbox,gtk.Label("Remote"))

        notebook_hbox = gtk.HBox (True,0)
        notebook_hbox.pack_start (notebook,False,True,10)
        notebook_hbox.set_border_width(10)

        buttons_vbox = gtk.VBox(False,0)

        button_add = gtk.Button ("Add",gtk.STOCK_ADD,True)
        button_add.connect ("pressed",
                             self.gui_control.cb_propw_addcddbserver,
                             self.server_list_liststore,
                             protocol_combobox,
                             url_entry,
                             spin_button1,
                             self.config_handler,
                             "cddb/servers")

        button_remove = gtk.Button ("Remove",gtk.STOCK_DELETE,True)
        button_remove.connect ("pressed",
                                self.gui_control.cb_propw_removecddbserver,
                                server_list_treeview,
                                self.config_handler,
                                "cddb/servers")

        button_up = gtk.Button ("Up",gtk.STOCK_GO_UP,True)
        button_up.connect ("pressed",
                            self.gui_control.cb_propw_up_cddbserver,
                            server_list_treeview,
                            self.config_handler,
                            "cddb/servers")

        button_down = gtk.Button ("Down",gtk.STOCK_GO_DOWN,True)
        button_down.connect ("pressed",
                              self.gui_control.cb_propw_down_cddbserver,
                              server_list_treeview,
                              self.config_handler,
                              "cddb/servers")

        buttons_vbox.pack_start (button_add,False,False,3)
        buttons_vbox.pack_start (button_remove,False,False,3)
        buttons_vbox.pack_start (button_up,False,False,3)
        buttons_vbox.pack_start (button_down,False,False,3)
        server_list_hbox.pack_start(buttons_vbox,False,False)

#===============================================================================
#        Local CDDB Tab
#===============================================================================
        local_cddb_options_frame,boxes = self.check_boxes_box ("Enable Remote CDDB",
                                                                ["Use local CDDB directory","Save entries in local directory (first of the list)"],
                                                                [0,1])
        boxes["Use local CDDB directory"].connect ("toggled",
                                                    self.gui_control.cb_propw_enable_local_cddb_check_box_toggled,
                                                    self.config_handler,
                                                    "cddb/use_local_cddb")

        boxes["Save entries in local directory (first of the list)"].connect ("toggled",
                                                    self.gui_control. cb_propw_save_cddb_entries_check_box_toggled,
                                                    self.config_handler,
                                                    "cddb/save_cddb_entries")

        cddb_directories_box = self.section_frame ("Local CDDB directories")

        local_form_vbox = gtk.VBox (False,0)
        url_entry = gtk.Entry()
        dir_list_hbox = gtk.HBox(False,5)

        dir_params_hbox = gtk.HBox(False,5)
        dir_label = gtk.Label("Directory:")

        dir_params_hbox.pack_start(dir_label,False,False)
        dir_params_hbox.pack_start(url_entry,True,True,5)

        local_form_vbox.pack_start(dir_params_hbox,False,False)
        local_form_vbox.pack_start(dir_list_hbox,True,True,10)
        local_form_vbox.set_border_width(10)
        cddb_directories_box.add (local_form_vbox)

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        dir_list_hbox.pack_start(sw,True,True)

        self.dir_list_liststore = gtk.ListStore(gobject.TYPE_STRING)

        dir_list_treeview = gtk.TreeView(self.dir_list_liststore)

        directories = self.config_handler.get ("cddb/cddb_dirs")
        directory_list = directories.split(";")

        for directory in directory_list:
            iter = self.dir_list_liststore.append()
            self.dir_list_liststore.set(iter,
                                        0,directory,
                                        )

        dir_list_treeview.set_rules_hint(True)
        #dir_list_treeview.set_headers_visible(False)
        sw.add(dir_list_treeview)

        self.cddb_dir_textrenderer = gtk.CellRendererText()

        tvcolumn = gtk.TreeViewColumn ("CDDB Directory",self.cddb_dir_textrenderer,text=0)

        dir_list_treeview.append_column(tvcolumn)

        cddb_directories_box_vbox = gtk.VBox (False,0)
        cddb_directories_box_vbox.pack_start (local_cddb_options_frame,False,False,15)
        cddb_directories_box_vbox.pack_start (cddb_directories_box,True,True)

        notebook.append_page (cddb_directories_box_vbox,gtk.Label("Local"))

        buttons_vbox = gtk.VBox(False,0)

        button_add = gtk.Button ("Add",gtk.STOCK_ADD,True)
        button_add.connect ("pressed",
                             self.gui_control.cb_propw_addcddbdir,
                             self.dir_list_liststore,
                             url_entry,
                             self.config_handler,
                             "cddb/cddb_dirs")

        button_remove = gtk.Button ("Remove",gtk.STOCK_DELETE,True)
        button_remove.connect ("pressed",
                                self.gui_control.cb_propw_removecddbdir,
                                dir_list_treeview,
                                self.config_handler,
                                "cddb/cddb_dirs")

        button_up = gtk.Button ("Up",gtk.STOCK_GO_UP,True)
        button_up.connect ("pressed",
                            self.gui_control.cb_propw_up_cddbdir,
                            dir_list_treeview,
                            self.config_handler,
                            "cddb/cddb_dirs")

        button_down = gtk.Button ("Down",gtk.STOCK_GO_DOWN,True)
        button_down.connect ("pressed",
                              self.gui_control.cb_propw_down_cddbdir,
                              dir_list_treeview,
                              self.config_handler,
                              "cddb/cddb_dirs")

        buttons_vbox.pack_start (button_add,False,False,3)
        buttons_vbox.pack_start (button_remove,False,False,3)
        buttons_vbox.pack_start (button_up,False,False,3)
        buttons_vbox.pack_start (button_down,False,False,3)
        dir_list_hbox.pack_start(buttons_vbox,False,False)


        main_vbox.pack_start(banner_frame,False,True)
        main_vbox.pack_start(notebook_hbox,True,True)

        frame.add (main_vbox)

        return frame

    def misc_options_frame (self):
        frame = gtk.Frame ()
        main_vbox = gtk.VBox (False,10)

        temp_dir = self.config_handler.get ("misc/tempdir")
        banner_frame = self.banner_box("Misc")
        tempdir_frame = self.section_frame ("Default Temporary Directory")
        tempdir_hbox = gtk.HBox (False,5)
        tempdir_hbox.set_border_width (10)
        tempdir_entry = gtk.Entry ()
        tempdir_entry.set_text (temp_dir)
        tempdir_entry.connect('focus-out-event',self.gui_control.cb_propw_entry_lose_focus,self.config_handler,"misc/tempdir")

        tempdir_button = gtk.Button ("browse",gtk.STOCK_OPEN,True)
        tempdir_button.connect ("pressed",self.gui_control.cb_propw_open_file,tempdir_entry )
        tempdir_hbox.pack_start(tempdir_entry,True,True)
        tempdir_hbox.pack_start(tempdir_button,False,False)
        tempdir_frame.add (tempdir_hbox)

        selected_boxes = []
        if self.config_handler.get ("misc/check_sysconfig"):
            selected_boxes.append(0)

        system_frame,boxes = self.check_boxes_box ("System",["Check System Configuration"],selected_boxes)
        boxes["Check System Configuration"].connect ("toggled",self.gui_control.cb_propw_check_box_toggled,self.config_handler,"misc/check_sysconfig")

        selected_boxes = []
        if self.config_handler.get ("misc/notification"):
            selected_boxes.append(0)
        if self.config_handler.get ("misc/hide_main_window"):
            selected_boxes.append(1)
        if self.config_handler.get ("misc/show_splashscreen"):
            selected_boxes.append(2)

        gui_settings_frame,boxes = self.check_boxes_box ("GUI Settings",["Show notification in top panel",
                                                                   "Hide main window while writing",
                                                                   "Show Splashscreen"],selected_boxes)
        boxes["Show notification in top panel"].connect ("toggled",self.gui_control.cb_propw_check_box_toggled,self.config_handler,"misc/notification")
        boxes["Hide main window while writing"].connect ("toggled",self.gui_control.cb_propw_check_box_toggled,self.config_handler,"misc/hide_main_window")
        boxes["Show Splashscreen"].connect ("toggled",self.gui_control.cb_propw_check_box_toggled,self.config_handler,"misc/show_splashscreen")

        main_vbox.pack_start(banner_frame,False,True)
        main_vbox.pack_start(tempdir_frame,False,True)
        main_vbox.pack_start(system_frame,False,True)
        main_vbox.pack_start(gui_settings_frame,False,True)
        frame.add (main_vbox)

        return frame

    def banner_box (self,option_name):
        frame = gtk.Frame()
        hbox = gtk.HBox (False,0)
        hbox.pack_start(self.banner_image[option_name],True,True)
        frame.add (hbox)
        return frame


    def section_frame (self,label):
        frame = gtk.Frame()
        frame_label = gtk.Label()
        frame_label.set_markup ('<span weight="bold">'+label+'</span>')
        frame.set_label_widget(frame_label)
        frame.set_shadow_type(gtk.SHADOW_NONE)

        return frame

    def __cb_modify_position (self,widget,event,data=None):
        for icon_box in self.icon_boxes:
            icon_box.set_state(gtk.STATE_NORMAL)

        widget.set_state(gtk.STATE_SELECTED)
        childwidget = widget.get_child().get_children()[1].get_label()
        self.show_frame (childwidget)

    def show_window (self):
        self.window.show_all()
        self.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.show_frame ("Writing")

    def check_boxes_box (self,label,check_labels,activated,comment = None):
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

#win = properties_window(None,None,None,None)
#win.show_window()
#win.show_frame ("Writing")
#gtk.main()
