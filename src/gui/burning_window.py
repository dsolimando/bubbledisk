import os
import gtk
import time

from gui.execution_window import execution_window
from constants.config import *
from re import match,compile
from backends.tool_box import Common_tools

class burning_window (execution_window):

    total_size = None

    def __init__(self,gui_control, project):
        execution_window.__init__(self,gui_control,project)
        self.banner_frame.add(self.gen_top_banner(project.name, ICONS_DIR+os.path.sep+DATA_CD_BANNER, project.file_system))
        self.banner_frame.set_border_width (0)
        self.banner_frame.show()

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
        self.device_name_label.set_markup ('<span weight="bold">'+self.gui_control.dev_manager.get_current_writer_display_name()+'</span>')

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

        regexp = compile(".*Total size:\s*(\d*).*")
        matched = regexp.match(output)
        if matched is not None:
            self.total_size = int(matched.group(1))
