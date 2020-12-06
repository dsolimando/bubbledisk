import gtk
import gobject

from gui_tools import section_frame
from gui_tools import devices_options_box

from bubble_windows import window
from bubble_windows import Read_toc_window

from backends.pyro_threads import Threaded_read_toc

from bd_exceptions.bubbledisk_exceptions import *


class disk_info_window (window):
    gui_control = None

    device_manager = None
    application_manager = None
    cdrdao_tools = None

    window = None
    tocs=[]
    infos= None

    def __init__(self,gui_control,dev_manager,app_manager,cdrdao_tools):
        self.gui_control = gui_control

        self.device_manager = dev_manager
        self.application_manager = app_manager
        self.cdrdao_tools = cdrdao_tools

        try:
            self.infos = self.cdrdao_tools.get_disk_infos()

            self.window = gtk.Window (gtk.WINDOW_TOPLEVEL)
            self.window.set_size_request (650,250)
            self.window.set_title ("Disk informationS")
            #self.window.connect("delete_event",self.gui_control.cb_pw_hide_window)

            main_box = gtk.VBox (False,0)
            main_box.set_border_width(10)

            frame = section_frame("Disk Informations")
            infos_hbox = devices_options_box (self.infos)
            frame.add(infos_hbox)

            hbox = gtk.HBox (False,0)
            hbox.set_border_width (10)
            close_button = gtk.Button ("Close",gtk.STOCK_CLOSE,True)
            close_button.connect ("pressed",self.gui_control.cb_hide_di_window,self.window)

            hbox.pack_end (close_button,False,False)

            main_box.pack_start(frame,True,True,2)
            if self.infos[1]["CD-R empty"] != "yes":
                self.window.set_size_request (650,550)
                toc_frame = self.toc_infos_frame()
                main_box.pack_start(toc_frame,True,True,2)

            main_box.pack_start(gtk.HSeparator(),False,False,2)

            main_box.pack_start(hbox,False,False)

            self.window.add (main_box)
            if self.infos[1]["CD-R empty"] != "yes":
                self.__read_tocs()


        except DeviceEmptyError:
            print "no disk in the device"

    def __read_tocs (self):
        read_toc_window = Read_toc_window(self.device_manager,self.infos[1]["Last Track"])
        self.toc_treeview.set_sensitive(False)
        read_toc_window.window.set_transient_for(self.window)
        read_toc_thread = Threaded_read_toc(self,self.cdrdao_tools,read_toc_window)
        read_toc_thread.start()

    def toc_infos_frame(self):

        toc_infos_frame = section_frame ("TOC Details")

        self.toc_treeview = gtk.TreeView ()
        self.toc_treeview.set_rules_hint(True)
        #devices_treeview.set_headers_visible(False)

        column1 = gtk.TreeViewColumn("Track")
        cell_pixbuf = gtk.CellRendererPixbuf()
        column1.pack_start(cell_pixbuf,False)
        column1.set_cell_data_func(cell_pixbuf, self.gui_control.cb_di_change_pixbuf)

        cell_text = gtk.CellRendererText()
        cell_text.xpad=3
        column1.pack_start(cell_text,True)
        column1.add_attribute(cell_text,'markup',0)

        column2 = gtk.TreeViewColumn("Start")
        cell_text = gtk.CellRendererText()
        cell_text.xpad=3
        column2.pack_start(cell_text,True)
        column2.add_attribute(cell_text,'text',1)

        column3 = gtk.TreeViewColumn("Length")
        cell_text = gtk.CellRendererText()
        cell_text.xpad=3
        column3.pack_start(cell_text,True)
        column3.add_attribute(cell_text,'text',2)

        column4 = gtk.TreeViewColumn("Mode")
        cell_text = gtk.CellRendererText()
        cell_text.xpad=3
        column4.pack_start(cell_text,True)
        column4.add_attribute(cell_text,'text',3)

        self.toc_treeview.append_column(column1)
        self.toc_treeview.append_column(column2)
        self.toc_treeview.append_column(column3)
        self.toc_treeview.append_column(column4)
        self.toc_treeview.expand_all()

        sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw.add (self.toc_treeview)

        toc_hbox =  gtk.HBox (True,10)
        toc_hbox.set_border_width(10)
        toc_hbox.pack_start(sw,True,True,20)
        toc_infos_frame.add(toc_hbox)

        return toc_infos_frame

    def insert_toc(self,tocs):
        toc_treestore = gtk.TreeStore(gobject.TYPE_STRING,
                                              gobject.TYPE_STRING,
                                              gobject.TYPE_STRING,
                                              gobject.TYPE_STRING)
        iter =  toc_treestore.append(None)
        toc_treestore.set (iter,0,"Disk",1,"",2,"",3,"AUDIO")

        for toc in tocs:
            sub_iter = toc_treestore.append(iter)
            toc_treestore.set (sub_iter,0,"Session %d (%s)"%(toc.session,toc.type),1,"",2,"",3,toc.type)
            for track in toc.tracks:
                sub_sub_iter = toc_treestore.append(sub_iter)
                toc_treestore.set (sub_sub_iter,0,"Track %d"%track.number,
                                       1,"%s (%s)"%(track.file_start,track.file_start_sectors),
                                       2,"%s (%s)"%(track.file_length,track.file_length_sectors),
                                       3,track.type)
        self.toc_treeview.set_model(toc_treestore)

