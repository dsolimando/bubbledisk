import gtk
import gobject
import time
import os.path

from re import compile,match
from bubble_windows import window
from constants.config import *
from backends.tool_box import Common_tools

class writing_window (window):

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

    speed = ''

    gui_control = None
    overal_progress = 0
    iso_size = 0

    def __init__(self,gui_control, project):
        self.gui_control = gui_control

        self.icon_theme = gtk.icon_theme_get_for_screen(gtk.gdk.screen_get_default())

        self.window = gtk.Window (gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request (600,700)
        self.window.set_resizable(False)
        self.window.set_title ("Writing")
        #self.window.connect("delete_event",self.gui_control.cb_pw_hide_window)


        mainBox = gtk.VBox (False,7)
        mainBox.set_border_width(10)

        banner_frame = None
#===============================================================================
#        Top Banner
#===============================================================================
        if project.name == DATA_CD:
            banner_frame  = self.gen_top_banner(project.name, ICONS_DIR+os.path.sep+DATA_CD_BANNER, project.file_system)

        elif project.name == COPY_CD:
            banner_frame  = self.gen_top_banner(project.name, ICONS_DIR+os.path.sep+COPY_CD_BANNER, "")
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

        self.track_label,self.track_label_inMB,self.track_progressbar,track_box = self.__labeled_progessbar("Track 0/10","0","25")
        self.overal_label,self.overal_label_inMB,self.overal_progressbar,overal_box = self.__labeled_progessbar("Overal progress","0","100")
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
        bannerLabel = gtk.Label()
        #device = self.gui_control.dev_manager.devices[self.gui_control.dev_manager.used_device]
        #writer = device.vendor+" "+device.identifikation
        writer = self.gui_control.dev_manager.get_current_writer().get_name_for_display()
        bannerLabel.set_markup ('<span  weight="bold">Writer: '+writer+'</span>')
        label_vbox.pack_start(bannerLabel,False,False,2)
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
#        Buffer size progressBar + separator + Writing Speed Frame
#===============================================================================
        bufsizespeed_hbox = gtk.HBox (False,0)
        bufsizespeed_hbox.pack_start(bufsize_box,False,True)
        bufsizespeed_hbox.pack_start(gtk.VSeparator(),False,False,2)
        bufsizespeed_hbox.pack_start(speed_vbox,False,False,2)

#===============================================================================
#        Buttons Frame
#===============================================================================
        buttons_hbox = gtk.HBox(False,0)
        close_button = gtk.Button (stock=gtk.STOCK_CLOSE)
        hide_button = gtk.Button("      Hide      ")
        cancel_button = gtk.Button (stock=gtk.STOCK_CANCEL)
        show_debug_button = gtk.Button(stock = gtk.STOCK_DIALOG_INFO)
        buttons_hbox.pack_end(close_button,False,False,5)
        #buttons_hbox.pack_end(hide_button,False,False,5)
        #buttons_hbox.pack_end(cancel_button,False,False,5)
        buttons_hbox.pack_end(show_debug_button,False,False,5)

        mainBox.pack_start(banner_frame,False,False)
        mainBox.pack_start(info_frame,False,False)
        mainBox.pack_start(middle_banner_frame,False,False)
        mainBox.pack_start(track_box,False,False)
        mainBox.pack_start(overal_box,False,False)
        mainBox.pack_start(writer_frame,False,False)
        mainBox.pack_start(bufsizespeed_hbox,False,False)
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

    def __update_track (self,current):
        total = self.gui_control.burning_projects[0].numtracks
        self.track_label.set_text("Track %s/%s"%(current,"1"))

    def  __update_track_progressbar(self,current,total):
        self.track_progressbar.set_fraction(float(current)/float(total))
        self.track_progressbar.set_text ("%d"%int((float(current)/float(total))*100)+" %")
        self.track_label_inMB.set_text("%s of %s MB Written"%(current,total))

    def  __update_overal_progressbar(self):
        ratio_progress = float(self.overal_progress)/float(self.total_size)
        self.overal_progressbar.set_fraction(ratio_progress)
        self.overal_progressbar.set_text ("%d "%int(ratio_progress*100)+" %")
        self.overal_label_inMB.set_text("%d of %d MB Written"%(self.overal_progress,self.total_size))

    def  __update_buffer_progressbar(self,size):
        self.bufsize_progressbar.set_fraction(float(size)/100)
        self.bufsize_progressbar.set_text ("%s "%size+"%")

    def __update_speed (self,speed):
        self.speed_label.set_text ("%d KB/s (%sx)"%(150*float(speed),speed))

    def  __update_iso_progressbar(self,size,elapsed_time):
        self.track_progressbar.set_fraction(float(size)/100)
        self.track_progressbar.set_text ("%s "%int(float(size))+"%")
        self.track_label_inMB.set_text("%s"%elapsed_time)

    def  __update_iso_remaining_time(self,finish_time=-1):
        if finish_time != -1:
            current_time = time.localtime()
            current_time_in_s = current_time[3]*3600+current_time[4]*60+current_time[5]
            remaining_time = finish_time-current_time_in_s
            remaining_time = time.gmtime(remaining_time)
            self.middle_bannerLabel2.set_markup ('<span>Remaining Time: %sm %ss</span>'%(remaining_time[4],remaining_time[5]))
        else:
            self.middle_bannerLabel2.set_markup ('<span>Remaining Time: 0m 0s</span>')

    def  __update_writing_remaining_time(self,speed):
        delta = float(self.total_size)/float(self.overal_progress)
        delta = 8192*delta
        rate = 150*float(speed)
        remaining_time = int(delta/rate)
        remaining_time = time.gmtime(remaining_time)
        self.middle_bannerLabel2.set_markup ('<span>Remaining Time: %sm %ss</span>'%(remaining_time[4],remaining_time[5]))


    def __update_copy_reading_progress_bar(self,h,m,s):
        new_val = float (Common_tools.time_2_seconds (h,m,s))/float(self.total_to_read_in_sec)
        self.track_progressbar.set_fraction(float(new_val))
        self.track_progressbar.set_text ("%s "%int(new_val*100)+"%")

        new_val = float (Common_tools.time_2_seconds (h,m,s))/float(self.total_to_read_in_sec)
        self.overal_progressbar.set_fraction(new_val/2)
        self.overal_progressbar.set_text ("%s "%int(new_val/2*100)+"%")

    def __update_copy_writing_progress_bar(self,current,total):
        new_val = (float(current)/float(total))
        print new_val
        self.track_progressbar.set_fraction(float(new_val))
        self.track_progressbar.set_text ("%s "%int(new_val*100)+"%")

        new_val = (float(current)/float(total))
        self.overal_progressbar.set_fraction(0.5+(float(new_val)/2.))
        self.overal_progressbar.set_text ("%s "%(50+(int(new_val*100)/2))+"%")

    def begin_copy_reading_disk_notification (self):
        self.middle_bannerLabel1.set_markup ('<span weight="bold" size="large">Reading CD</span>')
        self.middle_bannerLabel2.set_markup ('<span>Total data:</span>')

        self.track_label.set_text("Reading Progression")
        self.overal_label.set_text("Coying Progression")
        self.track_label_inMB.set_text("")

        app_manager = self.gui_control.app_manager
        cdrdao_infos = app_manager.get_application_infos("cdrdao")
        iter = self.infos_treestore.append(None)
        self.infos_treestore.set (iter,0,"Copying disk")
        iter = self.infos_treestore.append(None)
        self.infos_treestore.set (iter,0,"using %s %s"% (cdrdao_infos[0],cdrdao_infos[2]))
        iter = self.infos_treestore.append(None)
        self.infos_treestore.set (iter,0,"Begin reading disk using...")


    def begin_copy_writing_disk_notification (self):
        self.middle_bannerLabel1.set_markup ('<span weight="bold" size="large">Writing CD</span>')

        app_manager = self.gui_control.app_manager
        iter = self.infos_treestore.append(None)
        self.infos_treestore.set (iter,0,"Begin writing disk using...")

        self.overal_progressbar.set_fraction(0.5)
        self.overal_progressbar.set_text ("50 %")

        self.track_progressbar.set_fraction(0.)
        self.track_progressbar.set_text ("0 %")

        self.track_label.set_text("Writing Progression")

    def begin_iso_notification (self):
        self.middle_bannerLabel1.set_markup ('<span weight="bold" size="large">Making ISO</span>')
        self.middle_bannerLabel2.set_markup ('<span>Remaining Time:</span>')
        self.track_label.set_text("ISO Progression")
        self.track_label_inMB.set_text("")
        app_manager = self.gui_control.app_manager
        mkisofs_infos = app_manager.get_application_infos("mkisofs")
        iter = self.infos_treestore.append(None)
        self.infos_treestore.set (iter,0,"Begin ISO image creation")
        iter = self.infos_treestore.append(None)
        self.infos_treestore.set (iter,0,"using %s %s"% (mkisofs_infos[0],mkisofs_infos[2]))

    def begin_copy_reading_disk_notification (self):
        self.middle_bannerLabel1.set_markup ('<span weight="bold" size="large">Reading CD</span>')
        self.middle_bannerLabel2.set_markup ('<span>Total data:</span>')

        self.track_label.set_text("Reading Progression")
        self.overal_label.set_text("Coying Progression")
        self.track_label_inMB.set_text("")

        app_manager = self.gui_control.app_manager
        cdrdao_infos = app_manager.get_application_infos("cdrdao")
        iter = self.infos_treestore.append(None)
        self.infos_treestore.set (iter,0,"Copying disk")
        iter = self.infos_treestore.append(None)
        self.infos_treestore.set (iter,0,"using %s %s"% (cdrdao_infos[0],cdrdao_infos[2]))
        iter = self.infos_treestore.append(None)
        self.infos_treestore.set (iter,0,"Begin reading disk using...")

    def begin_writing_notification (self):
        self.middle_bannerLabel1.set_markup ('<span weight="bold" size="large">Writing</span>')
        self.middle_bannerLabel2.set_markup ('<span>Remaining Time:</span>')
        self.track_label.set_text("Track...")
        self.track_progressbar.set_fraction(0.0)
        self.track_progressbar.set_text("0 %")
        self.overal_label_inMB.set_text("")

    def begin_simulating_writing_notification (self):
        self.middle_bannerLabel1.set_markup ('<span weight="bold" size="large">Simulate</span>')
        self.middle_bannerLabel2.set_markup ('<span>Remaining Time:</span>')
        self.track_label.set_text("Track...")
        self.track_progressbar.set_fraction(0.0)
        self.track_progressbar.set_text("0 %")
        self.overal_label_inMB.set_text("")


    def update (self,output):
        print output
        regexp = compile (".*(.*)\sCopyright(.*).*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"%s"%(matched.group(0)))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile (".*Starting.*speed\s(\d*)\sin\sdummy.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"Start simulate at %d speed..."%int(matched.group(1)))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile (".*Starting.*speed\s(\d*)\sin\sreal.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"Start writing at %d speed..."%int(matched.group(1)))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile(".*Total size:\s*(\d*).*")
        matched = regexp.match(output)
        if matched is not None:
            self.total_size = int(matched.group(1))

        regexp = compile (".*\s*(\d)\sseconds.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"\t in %s seconds..." % matched.group(1))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile (".*BURN-Free is (.*).*")
        matched = regexp.match(output)
        if matched is not None:
            if matched.group(0) == "OFF":
                burnfree = "enabled"
            else:
                burnfree = "disabled"
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"BurnFree is %s"%burnfree)
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile (".*Performing OPC.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"Performing OPC...")
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile (".*Sending CUE sheet.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"Sending CUE sheet...")
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"Writing...")
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile (".*Track\s(\d*):\s*(\d*)\sof\s*(\d*)\sMB.*buf\s*(\d*)%.*\s(\d*\.\d*)x\..*")
        matched = regexp.match(output)
        if matched is not None:
            track = matched.group(1)
            track_writed = matched.group(2)
            self.overal_progress += 1
            print self.overal_progress
            track_size = matched.group(3)
            buffer_size = matched.group(4)
            writing_speed = matched.group(5)
            self.__update_track(track)
            self.__update_track_progressbar(track_writed, track_size)
            self.__update_buffer_progressbar(buffer_size)
            self.__update_overal_progressbar()
            self.__update_writing_remaining_time(writing_speed)
            self.__update_speed(writing_speed)

        regexp = compile (".*Fixating....*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"Fixating...")
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)
            self.middle_bannerLabel2.set_markup ('<span>Remaining Time: 0m 0s</span>')

        regexp = compile(".*Fixating time:\s*(\d*)\.(\d*)s.*")
        matched = regexp.match(output)
        if matched is not None:
            time = float (matched.group(1)+"."+matched.group(2))
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"Disk fixated in %d s"%time)
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"Writing ends successfully")
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)
            self.overal_progressbar.set_fraction(1.0)
            self.overal_progressbar.set_text ("100 %")
            self.overal_label_inMB.set_text("%d of %d MB Written"%(self.total_size,self.total_size))
            self.middle_bannerLabel1.set_markup ('<span weight="bold" color="green" size="large">Success!</span>')

        regexp = compile (".*(\d\d)\.(\d*)% done.*finish.*\s(\d*):(\d*):(\d*).*")
        matched = regexp.match(output)
        if matched is not None:
            writed = matched.group(1) +"."+ matched.group(1)
            finish_time_h = matched.group(3)
            finish_time_m = matched.group(4)
            finish_time_s = matched.group(5)
            self.__update_iso_remaining_time(int(finish_time_h)*3600+int(finish_time_m)*60+int(finish_time_s))
            self.__update_iso_progressbar(writed, "")

        regexp = compile (".*\sextents\swritten\s\((\d*).*")
        matched = regexp.match(output)
        if matched is not None:
            self.__update_iso_remaining_time(-1)
            self.__update_iso_progressbar("100", "")
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"ISO image created")
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)
            self.iso_size = matched.group(1)

        regexp = compile ("Copying.*length\s(\d\d):(\d\d):(\d\d).*")
        matched = regexp.match(output)
        if matched is not None:
            self.middle_bannerLabel2.set_markup ('<span>Total data : %s:%s:%s</span>'%(matched.group(1),matched.group(2),matched.group(3)))
            self.total_to_read_in_sec = Common_tools.time_2_seconds (
                                                                     int (matched.group(1)),
                                                                     int (matched.group(2)),
                                                                     int (matched.group(3))
                                                                     )

        regexp = compile ("(\d\d):(\d\d):(\d\d)")
        matched = regexp.match(output)
        if matched is not None:
            self.__update_copy_reading_progress_bar(int (matched.group(1)),
                                               int (matched.group(2)),
                                               int (matched.group(3)))

        regexp = compile ("Track\s(\d+).*")
        matched = regexp.match(output)
        if matched is not None:
            self.track_label.set_text("Reading track %s"%matched.group(1))

        regexp = compile (".*Cdrdao version.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile(".*SCSI interface.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile(".*Paranoia DAE library.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("Using driver.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("Starting write at speed.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("Turning BURN-Proof.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("Executing power calibration...")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("Power calibration successful.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("Reading toc and track data.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("PQ sub-channel reading.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("Raw P-W sub-channel reading.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("Cooked R-W sub-channel reading.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("Copying audio tracks")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("CDDB:.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("WARNING:.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("ERROR:.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("Reading of toc and track data.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("Writing track (\d+).*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.track_label.set_text("Writing track %s"%matched.group(1))

        regexp = compile("Wrote (\d+) of (\d+) MB \(Buffers (\d+)\%\s+(\d+).*")
        matched = regexp.match(output)
        if matched is not None:
            current_in_mb = matched.group(1)
            total_in_mb = matched.group(2)
            buffer1 = matched.group(3)
            buffer2 = matched.group(3)

            self.__update_copy_writing_progress_bar(current_in_mb,total_in_mb)











