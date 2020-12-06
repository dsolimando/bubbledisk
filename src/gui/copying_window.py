from gui.execution_window import execution_window
from constants.config import *
from re import match,compile
from backends.tool_box import Common_tools

import os
import gtk
import time

class copying_window (execution_window):

    num_sessions = None
    current_session_copied = None
    current_session_size = None
    current_session_first_sector = None

    def __init__(self,gui_control, project):
        execution_window.__init__(self,gui_control,project)
        self.bufsizespeed_hbox.destroy()
        self.banner_frame.add(self.gen_top_banner("Copy CD", ICONS_DIR+os.path.sep+COPY_CD_BANNER, ""))
        self.banner_frame.set_border_width (0)
        self.banner_frame.show()
        self.window.set_size_request(600,630)
        self.num_sessions = 1
        self.current_session_copied = 1

    def show_window (self):
        self.window.show_all()
        self.close_button.hide()

    def set_current_session_copied (self,session_num):
        self.current_session_copied = session_num

    def set_num_session (self,num_sesssions):
        self.num_sessions = num_sesssions

    def set_current_session_size (self,size):
        self.current_session_size =size

    def set_current_session_first_sector (self,sector):
        self.current_session_first_sector = sector

    def __update_copy_reading_progress_bar(self,h,m,s):
        new_val = ((self.current_session_copied-1)/float(self.num_sessions)) + float (Common_tools.time_2_seconds (h,m,s))/float(self.total_to_read_in_sec)/self.num_sessions
        self.track_progressbar.set_fraction(float(new_val))
        self.track_progressbar.set_text ("%s "%int(new_val*100)+"%")

        self.overal_progressbar.set_fraction(new_val/2)
        self.overal_progressbar.set_text ("%s "%int(new_val/2*100)+"%")

    def __update_copy_reading_progress_bar_multisess(self,current,total):
        new_val = ((self.current_session_copied-1)/float(self.num_sessions)) + float((float(current)/float(total))/self.num_sessions)
        self.track_progressbar.set_fraction(float(new_val))
        self.track_progressbar.set_text ("%s "%int(new_val*100)+"%")

        self.overal_progressbar.set_fraction((float(new_val)/2.))
        self.overal_progressbar.set_text ("%s "%((int(new_val*100)/2))+"%")

    def __update_copy_writing_progress_bar(self,current,total):
        new_val = ((self.current_session_copied-1)/float(self.num_sessions)) + float((float(current)/float(total))/self.num_sessions)
        self.track_progressbar.set_fraction(float(new_val))
        self.track_progressbar.set_text ("%s "%int(new_val*100)+"%")

        self.overal_progressbar.set_fraction(0.5+(float(new_val)/2.))
        self.overal_progressbar.set_text ("%s "%(50+(int(new_val*100)/2))+"%")

    def  __update_writing_remaining_time(self,speed,current,total):
        delta = ((self.current_session_copied-1)/float(self.num_sessions)) +float(total)/float(current)
        delta = 8192*delta
        rate = 150*float(speed)
        remaining_time = int(delta/rate)
        remaining_time = time.gmtime(remaining_time)
        self.middle_bannerLabel2.set_markup ('<span>Remaining Time: %sm %ss</span>'%(remaining_time[4],remaining_time[5]))


    def analysing_disk_notification (self):
        iter = self.infos_treestore.append(None)
        self.infos_treestore.set (iter,0,"Analaysing disk...")

    def begin_copy_reading_disk_notification_multisess (self):
        self.middle_bannerLabel1.set_markup ('<span weight="bold" size="large">Reading CD</span>')
        self.middle_bannerLabel2.set_markup ('<span></span>')
        self.track_progressbar.set_fraction(0.)
        self.track_progressbar.set_text ("0 %")
        self.track_label.set_text("Reading Progression")
        self.overal_label.set_text("Coying Progression")
        self.track_label_inMB.set_text("")

        app_manager = self.gui_control.app_manager
        readcd_infos = app_manager.get_application_infos("readcd")
        iter = self.infos_treestore.append(None)
        self.infos_treestore.set (iter,0,"Copying disk...")
        iter = self.infos_treestore.append(None)
        self.infos_treestore.set (iter,0,"Start reading disk using %s %s"% (readcd_infos[0],readcd_infos[2]))
        self.track_label_inMB.set_text ("")
        self.overal_label_inMB.set_text ("")


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
        self.device_name_label.set_markup ('<span weight="bold">'+self.gui_control.dev_manager.devices[self.project.reader_device].get_display_name()+'</span>')
        self.close_button.hide()

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

        self.device_name_label.set_markup ('<span weight="bold">'+self.gui_control.dev_manager.get_current_writer_display_name()+'</span>')
        self.cancel_button.set_sensitive (False)

    def update (self,output):
        print output
        regexp = compile ("Copying.*length\s(\d\d):(\d\d):(\d\d).*")
        matched = regexp.match(output)
        if matched is not None and self.current_session_copied == 1:
            self.middle_bannerLabel2.set_markup ('<span>Total data : %s:%s:%s</span>'%(matched.group(1),matched.group(2),matched.group(3)))
            self.total_to_read_in_sec = Common_tools.time_2_seconds (
                                                                     int (matched.group(1)),
                                                                     int (matched.group(2)),
                                                                     int (matched.group(3))
                                                                     )
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"Start reading...")
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile ("(\d\d):(\d\d):(\d\d)")
        matched = regexp.match(output)
        if matched is not None:
            self.__update_copy_reading_progress_bar(int (matched.group(1)),
                                               int (matched.group(2)),
                                               int (matched.group(3)))

        regexp = compile (".*[T|t]rack\s(\d+).*length (\d\d):(\d\d):(\d\d)")
        matched = regexp.match(output)
        if matched is not None:
            self.track_label.set_text("Reading track %s, Session %d / %d"%(matched.group(1),self.current_session_copied,self.num_sessions))

        regexp = compile (".*Cdrdao version.*")
        matched = regexp.match(output)
        if matched is not None and self.current_session_copied == 1:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0).strip())
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile(".*SCSI interface.*")
        matched = regexp.match(output)
        if matched is not None and self.current_session_copied == 1:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0).strip())
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile(".*Paranoia DAE library.*")
        matched = regexp.match(output)
        if matched is not None and self.current_session_copied == 1:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0).strip())
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("Starting write at speed.*")
        matched = regexp.match(output)
        if matched is not None and self.current_session_copied == 1:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("Reading toc and track data.*")
        matched = regexp.match(output)
        if matched is not None and self.current_session_copied == 1:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("Copying audio tracks")
        matched = regexp.match(output)
        if matched is not None and self.current_session_copied == 1:
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
        if matched is not None and self.current_session_copied == 1:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile ("Time total:\s(\d*)\.(\d*)sec")
        matched = regexp.match(output)
        if matched is not None and self.current_session_copied == 1:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"Finish reading session %d after %s.%s sec"%(self.current_session_copied,matched.group(1),matched.group(2)))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("Writing track (\d+).*")
        matched = regexp.match(output)
        if matched is not None:
            self.track_label.set_text("Writing track %s, Session %d / %d"%(matched.group(1),self.current_session_copied,self.num_sessions))

        regexp = compile("Wrote (\d+) of (\d+) MB \(Buffers (\d+)\%\s+(\d+).*")
        matched = regexp.match(output)
        if matched is not None:
            current_in_mb = matched.group(1)
            total_in_mb = matched.group(2)
            self.__update_copy_writing_progress_bar(current_in_mb,total_in_mb)

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

        regexp = compile("Writing finished successfully.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)
            self.middle_bannerLabel1.set_markup ('<span weight="bold" color="green" size="large">Success!</span>')


        regexp = compile("addr:\s+(\d*)\scnt")
        matched = regexp.match(output)
        if matched is not None:
            self.__update_copy_reading_progress_bar_multisess(int(matched.group(1))-self.current_session_first_sector, self.current_session_size)
            self.track_label.set_text("Reading Session %d / %d"%(self.current_session_copied,self.num_sessions))

        ### CDRECORD OUTPUT ANALYSE ###
        regexp = compile (".*(.*)\sCopyright(.*).*")
        matched = regexp.match(output)
        if matched is not None and self.current_session_copied == 1:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"%s"%(matched.group(0)))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile (".*Starting.*speed\s(\d*).*")
        matched = regexp.match(output)
        if matched is not None:
            self.track_label.set_text("Writing Session %d / %d"%(self.current_session_copied,self.num_sessions))
            if self.current_session_copied == 1:
                iter = self.infos_treestore.append(None)
                self.infos_treestore.set (iter,0,"Start writing at %d speed..."%int(matched.group(1)))
                path = self.infos_treestore.get_path(iter)
                self.infos_treeview.scroll_to_cell(path)


        regexp = compile (".*Track\s(\d*):\s*(\d*)\sof\s*(\d*)\sMB.*buf\s*(\d*)%.*\s(\d*\.\d*)x\..*")
        matched = regexp.match(output)
        if matched is not None:
            track_writed = matched.group(2)
            track_size = matched.group(3)
            writing_speed = matched.group(5)
            self.__update_copy_writing_progress_bar(track_writed, track_size)
            self.bufsize_label.set_text("%s of %s MB Written"%(track_writed,track_size))
            self.overal_label_inMB.set_text("%s of %s MB Written"%(track_writed,track_size))
            writing_speed = matched.group(5)
            self.__update_writing_remaining_time(writing_speed, track_writed,track_size)

        regexp = compile (".*Fixating....*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"Fixating session %s..."%self.current_session_copied)
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)
            self.middle_bannerLabel2.set_markup ('<span>Remaining Time: 0m 0s</span>')

        regexp = compile(".*Fixating time:\s*(\d*)\.(\d*)s.*")
        matched = regexp.match(output)
        if matched is not None and self.current_session_copied == self.num_sessions:
            time = float (matched.group(1)+"."+matched.group(2))
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"Disk fixated in %d s"%time)
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"Writing ends successfully")
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)
            self.overal_progressbar.set_fraction(1.0)
            self.overal_progressbar.set_text ("100 %")
            self.middle_bannerLabel1.set_markup ('<span weight="bold" color="green" size="large">Success!</span>')
            self.close_button.show()
            self.cancel_button.hide()

#cw = copying_window(None,1)
#cw.show_window()
#gtk.main()