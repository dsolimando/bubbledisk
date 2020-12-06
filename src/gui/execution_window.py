import gtk
import gobject
import time
import os.path

from re import compile,match
from bubble_windows import window
from constants.config import *
from backends.tool_box import Common_tools

class execution_window (window):

    #Gui attributes
    window  = None
    bannerLabel1 = None
    bannerLabel2 = None
    infos_treestore = None
    track_label = None
    track_label_inMB = None
    track_progressbar = None
    overal_label = None
    overal_label_inMB = None
    overal_progressbar = None
    banner_frame = None
    close_button = None
    cancel_button = None
    show_debug_button = None
    bufsizespeed_hbox = None
    device_name_label = None

    speed = ''

    gui_control = None

    project = None

    def __init__(self,gui_control, project):
        self.gui_control = gui_control

        self.icon_theme = gtk.icon_theme_get_for_screen(gtk.gdk.screen_get_default())

        self.window = gtk.Window (gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request (600,700)
        self.window.set_resizable(False)
        self.window.set_title ("Writing")
        #self.window.connect("delete_event",self.gui_control.cb_pw_hide_window)

        self.project = project

        mainBox = gtk.VBox (False,7)
        mainBox.set_border_width(10)

#===============================================================================
#        Top Banner
#===============================================================================

        self.banner_frame  = gtk.Frame()
#===============================================================================
#        Info TreeView
#===============================================================================
        info_frame = gtk.Frame()
        info_frame.set_size_request(-1,220)
        info_frame.set_shadow_type(gtk.SHADOW_IN)
        info_hbox = gtk.HBox (True,0)
        #info_hbox.set_border_width (10)
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

        info_hbox.pack_start (sw,False,True)

#===============================================================================
#        Middle Banner
#===============================================================================
        middle_banner_frame = gtk.Frame()
        middle_banner_frame.set_shadow_type(gtk.SHADOW_IN)
        event_box = gtk.EventBox()
        middle_banner_frame.add(event_box)
        bannerBox = gtk.HBox (False,0)
        event_box.add(bannerBox)
        event_box.modify_bg(gtk.STATE_NORMAL,event_box.get_colormap().alloc_color('white'))
        bannerBox.set_size_request(-1,70)

        image = gtk.Image ()
        image.set_from_file(ICONS_DIR + "/banner_middle_right.png")
        #bannerBox.pack_start(image,False,False)

        label_vbox = gtk.VBox(False,0)
        label1_hbox = gtk.HBox(False,0)
        label2_hbox = gtk.HBox(False,0)
        ## nice view workaround
        #bannerLabel0 = gtk.Label(' ')
        ##
        self.middle_bannerLabel1 = gtk.Label()
        label1_hbox.pack_start(self.middle_bannerLabel1,False,False,10)
        self.middle_bannerLabel2 = gtk.Label()
        label2_hbox.pack_start(self.middle_bannerLabel2,False,False,10)
        self.middle_bannerLabel1.set_markup ('<span weight="bold" size="large"></span>')
        self.middle_bannerLabel2.set_markup ('<span></span>')
        label_vbox.pack_start(label1_hbox,False,False,10)
        label_vbox.pack_start(label2_hbox,False,False)

        bannerBox.pack_start(label_vbox,False,False)
        bannerBox.pack_end(image,False,False)

        self.track_label,self.track_label_inMB,self.track_progressbar,track_box = self.__labeled_progessbar("","0","0")
        self.overal_label,self.overal_label_inMB,self.overal_progressbar,overal_box = self.__labeled_progessbar("Overal progress","0","0")
        self.bufsize_label,not_used,self.bufsize_progressbar,bufsize_box = self.__labeled_progessbar("Buffer status",barsize=400)

#===============================================================================
#        Writer Name Frame
#===============================================================================
        writer_frame = gtk.Frame()
        writer_frame.set_shadow_type(gtk.SHADOW_IN)
        event_box = gtk.EventBox()
        writer_frame.add(event_box)
        writerBox = gtk.HBox (False,0)
        event_box.add(writerBox)
        event_box.modify_bg(gtk.STATE_NORMAL,event_box.get_colormap().alloc_color('white'))
        writerBox.set_size_request(-1,20)
        label_vbox = gtk.VBox(False,8)
        self.device_name_label = gtk.Label()
        label_vbox.pack_start(self.device_name_label,False,False,2)
        writerBox.pack_start(label_vbox,False,False,5)

#===============================================================================
#        Writing Speed Frame
#===============================================================================
        speed_vbox = gtk.VBox (False,0)
        speed_vbox.pack_start(gtk.Label("Estimated writing speed:"),False,False,5)
        speed_hbox = gtk.HBox (False,0)
        self.speed = "0 KB/s (0.0x)"
        self.speed_label = gtk.Label (self.speed)
        speed_hbox.pack_end(self.speed_label,False,False)
        speed_vbox.pack_start(speed_hbox,False,False,5)

#===============================================================================
#        Buffer size progressBar + separacancel_buttontor + Writing Speed Frame
#===============================================================================
        self.bufsizespeed_hbox = gtk.HBox (False,0)
        self.bufsizespeed_hbox.pack_start(bufsize_box,False,True)
        self.bufsizespeed_hbox.pack_start(gtk.VSeparator(),False,False,2)
        self.bufsizespeed_hbox.pack_start(speed_vbox,False,False,2)

#===============================================================================
#        Buttons Frame
#===============================================================================
        buttons_hbox = gtk.HBox(False,0)
        self.close_button = gtk.Button (stock=gtk.STOCK_CLOSE)
        self.close_button.connect ("pressed",self.gui_control.cb_close_copy_reading,self )
        hide_button = gtk.Button("      Hide      ")
        self.cancel_button = gtk.Button (stock=gtk.STOCK_CANCEL)
        self.cancel_button.connect ("pressed",self.gui_control.cb_cancel_copy_reading,self )
        self.show_debug_button = gtk.Button(stock = gtk.STOCK_DIALOG_INFO)
        buttons_hbox.pack_end(self.close_button,False,False,5)
        #buttons_hbox.pack_end(hide_button,False,False,5)
        buttons_hbox.pack_end(self.cancel_button,False,False,5)
        buttons_hbox.pack_end(self.show_debug_button,False,False,5)

        mainBox.pack_start(self.banner_frame,False,False)
        mainBox.pack_start(info_frame,False,False)
        mainBox.pack_start(middle_banner_frame,False,False)
        mainBox.pack_start(track_box,False,False)
        mainBox.pack_start(overal_box,False,False)
        mainBox.pack_start(writer_frame,False,False)
        mainBox.pack_start(self.bufsizespeed_hbox,False,False)
        mainBox.pack_start(gtk.HSeparator(),False,False)
        mainBox.pack_start(buttons_hbox,False,False)

        self.window.add (mainBox)
        #self.window.show_all()

    def gen_top_banner (self,project_name,banner_left,file_sys):
        banner_frame = gtk.Frame()
        banner_frame.set_shadow_type(gtk.SHADOW_IN)
        event_box = gtk.EventBox()
        banner_frame.add(event_box)
        bannerBox = gtk.HBox (False,0)
        event_box.add(bannerBox)
        event_box.modify_bg(gtk.STATE_NORMAL,event_box.get_colormap().alloc_color('white'))
        bannerBox.set_size_request(-1,80)

        image = gtk.Image ()
        image.set_from_file(banner_left)
        image2 = gtk.Image ()
        image2.set_from_file(ICONS_DIR + "/banner_right.png")
        bannerBox.pack_start(image,False,False)

        label_vbox = gtk.VBox(False,5)
        ## nice view workaround
        bannerLabel0 = gtk.Label(' ')
        ##
        self.bannerLabel1 = gtk.Label()
        self.bannerLabel2 = gtk.Label()
        self.bannerLabel1.set_markup ('<span weight="bold">'+project_name+'</span>')
        self.bannerLabel2.set_markup ('<span>'+file_sys+'</span>')
        label_vbox.pack_start(bannerLabel0,False,False)
        label_vbox.pack_start(self.bannerLabel1,False,False)
        label_vbox.pack_start(self.bannerLabel2,False,False)

        bannerBox.pack_start(label_vbox,False,False)
        bannerBox.pack_end(image2,False,False)

        return banner_frame

    def cb_blanking_window_change_pixbuf (self):
        pass

    def __labeled_progessbar (self, label,current=-1,total=-1, barsize=-1):
        vbox = gtk.VBox (False,0)
        hbox = gtk.HBox (False,0)
        hbox2 = gtk.HBox (False,0)
        label = gtk.Label (label)
        hbox.pack_start(label,False,False,3)
        if current !=-1 and total != -1:
            label2 = gtk.Label ("%s of %s MB Written"%(current,total))
        else:
            label2 = gtk.Label ("")
        hbox.pack_end(label2,False,False,3)
        pb = gtk.ProgressBar()
        pb.set_text ('0 %')

        vbox.pack_start(hbox,False,False,3)

        if barsize !=-1:
            pb.set_size_request(barsize,-1)
            hbox2.pack_start(pb,False,False,3)
            vbox.pack_start(hbox2,False,False,3)
        else:
            hbox2.pack_start(pb,True,True,3)
            vbox.pack_start(hbox2,True,True,3)
        return label,label2,pb,vbox

    def update (self,output):
        pass
