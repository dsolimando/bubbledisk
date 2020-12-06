import os
import gtk
import time

from gui.execution_window import execution_window
from constants.config import *
from re import match,compile
from backends.tool_box import Common_tools

class audio_burning_window (execution_window):
    STATE_CONVERTING = 0
    STATE_WRITING = 1

    total_size = None
    state = None
    num_tracks = None

    curent_track = 1
    track_lengths_in_msec = {}
    delta = 0
    current_in_mb =0

    def __init__(self,gui_control, project):
        execution_window.__init__(self,gui_control,project)
        self.bufsizespeed_hbox.destroy()

        self.banner_frame.add(self.gen_top_banner(project.name, ICONS_DIR+os.path.sep+DATA_CD_BANNER, project.file_system))
        self.banner_frame.set_border_width (0)
        self.banner_frame.show()

        self.window.set_size_request(600,630)

    def init_for_convertion (self):
        self.middle_bannerLabel1.set_markup ('<span weight="bold" size="large">Converting tracks</span>')

        self.state = self.STATE_CONVERTING

        app_manager = self.gui_control.app_manager
        iter = self.infos_treestore.append(None)
        self.infos_treestore.set (iter,0,"Begin converting tracks in WAV format...")

        self.overal_progressbar.set_fraction(0.)
        self.overal_progressbar.set_text ("0 %")

        self.track_progressbar.set_fraction(0.)
        self.track_progressbar.set_text ("0 %")

        self.overal_label_inMB.set_text("")
        self.track_label_inMB.set_text("")

        self.track_label.set_text("Convertion Progression")

        self.device_name_label.set_markup ('<span weight="bold">'+self.gui_control.dev_manager.get_current_writer_display_name()+'</span>')

    def init_for_writing (self):
        print "Init for writing"
        self.state = self.STATE_WRITING

        self.middle_bannerLabel1.set_markup ('<span weight="bold" size="large">Writing Audio CD</span>')

        app_manager = self.gui_control.app_manager
        cdrdao_infos = app_manager.get_application_infos("cdrdao")

        iter = self.infos_treestore.append(None)
        self.infos_treestore.set (iter,0,"Begin writing audio disk ...")
        iter = self.infos_treestore.append(None)
        self.infos_treestore.set (iter,0,"using %s %s"% (cdrdao_infos[0],cdrdao_infos[2]))

        self.overal_progressbar.set_fraction(0.5)
        self.overal_progressbar.set_text ("50 %")

        self.track_progressbar.set_fraction(0.)
        self.track_progressbar.set_text ("0 %")

        self.track_label.set_text("Writing Track...")

        self.device_name_label.set_markup ('<span weight="bold">'+self.gui_control.dev_manager.get_current_writer_display_name()+'</span>')

    def update_convertion_state (self,current_track, numtrack,position,song_title):
        tmp = current_track/float(numtrack)
        tmp2 = position/numtrack

        self.overal_progressbar.set_fraction(float(tmp+tmp2)/float(2))
        self.overal_progressbar.set_text ("%d "%int((float(tmp+tmp2)/float(2))*100)+"%")

        self.track_progressbar.set_fraction(position)
        self.track_progressbar.set_text ("%d "%int((position*100))+"%")

        if len(song_title) >40:
            self.track_label.set_text("Converting Track %d:\t'%s...'"%(current_track+1,song_title[0:40]))
        else:
            self.track_label.set_text("Converting Track %d:\t'%s'"%(current_track+1,song_title))

    def __update_copy_writing_progress_bar(self,current,total):

        track_fraction = float(Common_tools.ko_2_msec((int(current)-self.delta)*1024))/self.track_lengths_in_msec[str(self.curent_track)]
        if track_fraction > 1:
            track_fraction = 1
        self.track_progressbar.set_fraction(track_fraction)
        self.track_progressbar.set_text ("%s "%int(track_fraction*100)+"%")

        overal_fraction = 0.5+((float(current)/float(total))/2.)
        self.overal_progressbar.set_fraction(float(overal_fraction))
        self.overal_progressbar.set_text ("%s "%(int(overal_fraction*100))+"%")

    def update (self,output):
        regexp = compile (".*Cdrdao version.*")
        matched = regexp.match(output)
        if matched is not None :
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0).strip())
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile(".*SCSI interface.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0).strip())
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)


        regexp = compile("Starting write at speed.*")
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


        regexp = compile("WARNING:.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("Writing track (\d+).*")
        matched = regexp.match(output)
        if matched is not None:
            self.delta=int(self.current_in_mb)
            self.curent_track = str(int(matched.group(1)))
            self.track_label.set_text("Writing track %s"%matched.group(1))

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

        regexp = compile("Turning BURN-Proof on.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("Enabling JustLink.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0))
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)

        regexp = compile("Wrote (\d+) of (\d+) MB \(Buffers (\d+)\%\s+(\d+).*")
        matched = regexp.match(output)
        if matched is not None:
            self.current_in_mb = matched.group(1)
            self.total_in_mb = matched.group(2)
            self.__update_copy_writing_progress_bar(self.current_in_mb,self.total_in_mb)

        regexp = compile("Wrote (\d+) blocks.*")
        matched = regexp.match(output)
        if matched is not None:
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"Write finished...")
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,matched.group(0).strip())
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)
            iter = self.infos_treestore.append(None)
            self.infos_treestore.set (iter,0,"Flushing Cache...")
            path = self.infos_treestore.get_path(iter)
            self.infos_treeview.scroll_to_cell(path)


