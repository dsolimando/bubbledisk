import gtk
import os
import gnome
import threading
import gobject
import gnomevfs

from re import compile,match

from backends.pyro_threads import *
from backends.audio.ToolBox import *
from backends.project_creation_tools import *
from backends.tool_box import Track
from backends.tool_box import Cd_text

from backends.audio.artwork.Loader import *
from backends.audio.artwork.CoverSearch import CoverSearch

from bd_exceptions.bubbledisk_exceptions import *

from gui.gui_tools import *
from gui.choose_writer_window import choose_writer_window
from gui.bubble_windows import import_session_window,cdtext_track_window
from gui.writing_window import writing_window
from gui.disk_info_window import disk_info_window
from gui.properties_window import  properties_window
from gui.blankdisk_window import blankdisk_window
from gui.projects_window import *
from gui.copying_window import copying_window
from gui.burning_window import burning_window
from gui.audio_burning_window import audio_burning_window

from constants.config import *

from string import *

from backends.config_serializer import ConfigSerializer


class bubbledisk_gui_control:
    gui_model = None
    gui_view = None

    __fs_cbid_drag_motion = None
    __fs_cbid_drag_end = None

    __npfs_cbid_drag_motion = None
    __npfs_cbid_drag_end = None

    # Current working project
    current_project = -1
    # Projects Pool
    burning_projects = []
    # Window's Projects Pool
    win_burning_projects = []
    toolbox = None
    vfs = None
    isofs_tool = None
    cdrecord_tool = None
    cdrdao_tools = None
    audio_player = None

    app_manager = None
    dev_manager = None

    config_handler = None

    root_projects = None

    icon_theme = gtk.icon_theme_get_for_screen(gtk.gdk.screen_get_default())

    project_file_name = None

    def __init__ (self,
                  toolbox,
                  vfs,
                  isofs_tool,
                  cdrecord_tool,
                  app_manager,
                  dev_manager,
                  config_handler,
                  cdrdao_tools,
                  root_projects,
                  audio_player):

        self.toolbox = toolbox
        self.vfs = vfs
        self.isofs_tool = isofs_tool
        self.cdrecord_tool = cdrecord_tool
        self.app_manager = app_manager
        self.dev_manager = dev_manager
        self.config_handler = config_handler
        self.cdrdao_tools = cdrdao_tools
        self.root_projects = root_projects
        self.audio_player = audio_player
        self.common_dialog = gtk.MessageDialog(None,
                                         gtk.DIALOG_DESTROY_WITH_PARENT,
                                         gtk.MESSAGE_INFO, gtk.BUTTONS_OK,
                                          '')
        self.cover_search = CoverSearch ()

        self.audio_project_update_id = -1
        self.audio_project_changed_id = -1
        self.audio_p_duration = -1

    def __cursor_watch(self,window):
        cursor = gtk.gdk.Cursor(gtk.gdk.WATCH)
        window.window.set_cursor(cursor)
        while gtk.events_pending():
            gtk.main_iteration()

    def __cursor_left_arrow (self,window):
        cursor = gtk.gdk.Cursor(gtk.gdk.TOP_LEFT_ARROW)
        window.window.set_cursor(cursor)
        while gtk.events_pending():
            gtk.main_iteration()

    def set_model (self,model):
        self.gui_model = model

    def set_view (self,view):
        self.gui_view = view

    #############################################################################
    # Main Window callback functions
    #############################################################################
    def cb_exit_bubbledisk (self,widget,event,config):
        width,height = widget.get_size ()
        pos_x,pos_y = widget.get_position()
        config.set ("view/window_height",height)
        config.set ("view/window_width", width)
        config.set ("view/window_position_x",pos_x)
        config.set ("view/window_position_y",pos_y)
        gtk.main_quit()

    def __vertical_browsing (self):
        self.gui_view.set_explorers_direction(self.gui_view.VERTICAL,self.gui_view.get_current_vfs_position())

    def __horizontal_browsing (self):
        self.gui_view.set_explorers_direction(self.gui_view.HORIZONTAL,self.gui_view.get_current_vfs_position())

    def __fs_left (self):
        self.gui_view.set_explorers_direction(self.gui_view.get_current_explorers_direction(),self.gui_view.VFS_LEFT)

    def __fs_right (self):
        self.gui_view.set_explorers_direction(self.gui_view.get_current_explorers_direction(),self.gui_view.VFS_RIGHT)

    def cb_change_sense (self,action,current,config):
        if current.get_current_value() == self.gui_view.VERTICAL:
            config.set ("view/explorer_view","vertical")
            self.__vertical_browsing()
        else:
            config.set ("view/explorer_view","horizontal")
            self.__horizontal_browsing()

    def __refresh_frames (self):
        if self.gui_view.get_current_explorers_direction()== self.gui_view.VERTICAL:
            self.__horizontal_browsing()
        else:
            self.__vertical_browsing()

        if self.gui_view.get_current_explorers_direction()== self.gui_view.HORIZONTAL:
            self.__vertical_browsing()
        else:
            self.__horizontal_browsing()

    def cb_show_main_projects_window(self,widget):
        self.gui_model.projects_window.show()

    def cb_show_projects_window (self,widget):
        self.win_burning_projects[self.current_project].window.show_all()
        self.win_burning_projects[self.current_project].hide_widgets_after_iso_creation(self.gui_view.project_media)
        self.win_burning_projects[self.current_project].ok_button.show()
        self.win_burning_projects[self.current_project].create_button.hide()
        self.win_burning_projects[self.current_project].cancel_button.hide()


    def cb_finalize_compilation (self,action):
        self.win_burning_projects[self.current_project].window.set_property('modal',True)
        self.win_burning_projects[self.current_project].window.show_all()
        self.win_burning_projects[self.current_project].hide_widgets_after_iso_creation(self.gui_view.project_media)


    def cb_change_fs_place (self,action,current,config):
        print current.get_current_value()
        if current.get_current_value() == self.gui_view.LEFT:
            self.__fs_left()
            config.set("view/explorer_sense","left")
        else:
            self.__fs_right()
            config.set("view/explorer_sense","right")


    def cb_refresh_explorer (self,action):
        listmodel = self.gui_model.explorer.directory_liststore_factory(self.gui_view.current_fs_dir_browsed)
        self.gui_model.explorer.fs_list_treeview.set_model(listmodel)

    def cb_eject_disk (self,action):
        self.dev_manager.eject_disk()

    def cb_gconf_change_size (self,window, event,config):
        width,height = window.get_size ()
        #config.set ("view/window_height",height)
        #config.set ("view/window_width", width)
        #view = config.get("view/explorer_view")
        #print self.gui_view.current_paned

#        if view == "horizontal":
#            gobject.idle_add(self.gui_view.current_paned.set_position,(int(width/2)))
#        else:
#            gobject.idle_add(self.gui_view.current_paned.set_position,(int(width/2)))

    ##################################################################################
    # MyLittleNautilus Callback functions
    ##################################################################################

    def __drag_check_end(self):
        self.gui_model.explorer.fs_list_treeview.disconnect(self.__fs_cbid_drag_motion)
        self.gui_model.explorer.fs_list_treeview.disconnect(self.__fs_cbid_drag_end)
        self.__fs_cbid_drag_motion = None
        self.__fs_cbid_drag_end = None

    def cb_fs_liststore_explore(self, treeview, path, column):
        # Retrieve the treemodel of the treeview
        model = treeview.get_model()

        # Get the row pointed
        iter = model.get_iter(path)

        # Get the absolute directory to show
        dirname = model.get_value(iter,2)
        self.gui_view.current_fs_dir_browsed = dirname
        if os.path.isdir(dirname):
            if dirname.endswith('/..'):
                (head,tail) = os.path.split(dirname)
                (head,tail) = os.path.split(head)
                dirname = head
            listmodel = self.gui_model.explorer.directory_liststore_factory(dirname)
            self.gui_model.explorer.fs_list_treeview.set_model(listmodel)

#    def get_drag_selection (self,treeview, context, selection, info, timestamp):
#        tree_selection = treeview.get_selection()
#        model = treeview.get_model()
#        (model2,selected_rows) = tree_selection.get_selected_rows(model)

    def cb_fs_foreach_row_selected (self,treemodel,path,iter):
        return

    def cb_fs_button_pressed (self,widget,data):
        path = widget.get_path_at_pos(int(data.x), int(data.y))

        widget.get_selection().selected_foreach(self.cb_fs_foreach_row_selected)

        if data.button == 1 and data.type == gtk.gdk._2BUTTON_PRESS and path != None:
            iter = widget.get_model().get_iter(path[0])
            widget.emit("row-activated", widget.get_model().get_path(iter),widget.get_column(0))

        elif self.__fs_cbid_drag_motion == None and path != None:
            self.__fs_cbid_drag_motion = self.gui_model.explorer.fs_list_treeview.connect("motion_notify_event", self.cb_fs_drag_motion, data.copy() )
            self.__fs_cbid_drag_end = self.gui_model.explorer.fs_list_treeview.connect("button_release_event", self.cb_fs_button_release, data.copy() )
            return True

    def cb_fs_button_release(self, widget, data, userdata = None):
        self.gui_model.explorer.fs_list_treeview.emit("button_press_event", userdata)
        self.__drag_check_end()

    def cb_fs_drag_motion(self, widget, data, userdata = None):
        self.gui_view.moving_cell_path = widget.get_path_at_pos(int(userdata.x), int(userdata.y-20))
        if widget.drag_check_threshold(int(userdata.x), int(userdata.y), int(data.x), int(data.y)) == True:
            self.__drag_check_end()
            self.gui_model.explorer.fs_list_treeview.drag_begin( (("text/plain", gtk.TARGET_SAME_APP | gtk.TARGET_SAME_WIDGET, 0), ), gtk.gdk.ACTION_COPY, userdata.button, userdata)

    def cb_fs_tree_cursor_changed(self, treeview, path=None, column=None):
        # Retrieve the treemodel and iter of the treeview
        (model,iter) = treeview.get_selection().get_selected()

        # Get the absolute directory to show
        dirname = model.get_value(iter,1)
        self.gui_view.current_fs_dir_browsed = dirname

        listmodel = self.gui_model.explorer.directory_liststore_factory(dirname)
        self.gui_model.explorer.fs_list_treeview.set_model(listmodel)



    def cb_fs_gen_subdir (self, treeview, iter, path):
        model = treeview.get_model()
        dirname = model.get_value(iter,1)

        child_iter = model.iter_children (iter)
        while child_iter != None:
            if model.iter_children (child_iter) == None:
                subdirname = model.get_value(child_iter,1)
                try:
                    for dir in gnome.vfs.open_directory(subdirname):
                        if (dir.name.find(".") != 0 and dir.type == 2):
                            self.gui_model.explorer.treestore.append(child_iter,[dir.name , os.path.join(subdirname,dir.name)])
                except gnome.vfs.AccessDeniedError,error:
                    error
            child_iter = model.iter_next(child_iter)

    def cb_fs_pixbuf_type(self,column,cell,model,iter):
        filename = model.get_value(iter,2)

        no_file = not os.path.isdir(filename)
        no_dir = not os.path.isfile(filename)
        no_abs = not os.path.isabs(filename)
        no_link = not os.path.islink (filename)
        no_mount = not os.path.ismount (filename)

        if no_file and no_dir  and no_link and no_mount:
            small_icon = dirIcon = self.icon_theme.load_icon("emblem-important",
                                                24,
                                                gtk.ICON_LOOKUP_FORCE_SVG)
        elif os.path.isdir(filename):
            small_icon = dirIcon = self.icon_theme.load_icon("gnome-fs-directory",
                                                24,
                                                gtk.ICON_LOOKUP_FORCE_SVG)
        else:
            exten = filename.split('.')
            small_icon = get_icon (exten[-1],self.icon_theme)

        cell.set_property('pixbuf', small_icon)

    def cb_fs_change_tree_icon (self,column,cell,model,iter):
        if model.get_value(iter,0) == 'Home':
            small_icon = self.icon_theme.load_icon("gnome-fs-home",
                                                24,
                                                gtk.ICON_LOOKUP_FORCE_SVG)
        elif model.get_value(iter,0) == 'File System':
            small_icon = self.icon_theme.load_icon("gnome-dev-harddisk",
                                                24,
                                                gtk.ICON_LOOKUP_FORCE_SVG)
        else:
            small_icon = self.icon_theme.load_icon("gnome-fs-directory",
                                                    24,
                                                    gtk.ICON_LOOKUP_FORCE_SVG)
        cell.set_property('pixbuf', small_icon)


    ##################################################################################
    # New Project Explorers Callback functions
    ##################################################################################

    def npfs_drag_end (self,selected_iters,drop_dest_widget):
        #Updating the lisstore with new files
        #self.vfs.print_xml()
        self.burning_projects[0].set_current_dir(self.parent_dropped_dir)
        updated_liststore = self.gui_model.project_treeview.directory_liststore_factory (self.burning_projects[0].get_current_dir())
        self.gui_model.project_treeview.list_treeview.set_model(updated_liststore)
        self.gui_model.project_treeview.populate_treestore_iter_with_files (
                                            self.gui_model.project_treeview.treestore,
                                            self.gui_view.current_treeiter
                                            )
        self.gui_model.project_treeview.treeview.expand_to_path (
            self.gui_model.project_treeview.treeview.get_model().get_path(self.gui_view.current_treeiter)
            )

        #for iter in selected_iters:
        self.gui_model.progressbar.set_fraction(self.burning_projects[0].get_used_percent())
        self.gui_model.progressbar.set_text(self.burning_projects[0].get_project_size_inM())


        return


#    def cb_npfs_drag_motion (self,widget, drag_context, x, y, timestamp):
#        path = widget.get_path_at_pos(int(x), int(y-20))
#        if path != None:
#            self.moving_cell_path = path[0]
#        else:
#            self.moving_cell_path = None

    def cb_npfs_drag_drop (self,widget, drag_context, x, y, timestamp):
        path = widget.get_path_at_pos(int(x), int(y-20))
        self.parent_dropped_dir = self.burning_projects[0].get_current_dir()

        if path != None:
            if self.vfs.get_file_type(widget.get_model().get_value(widget.get_model().get_iter(path[0]),1)) == "directory":
                self.burning_projects[0].set_current_dir(
                    widget.get_model().get_value(widget.get_model().get_iter(path[0]), 1)
                                                         )

        # Retrieves row inserted
        source_treeview = drag_context.get_source_widget()
        source_selection = source_treeview.get_selection()
        (model,selected_rows_paths) = source_selection.get_selected_rows()

        selected_files = []
        for path in selected_rows_paths:
            selected_files.append(model.get_value(model.get_iter(path),2))

        # Temp Listore during copying operation
        temp_liststore = self.gui_model.project_treeview.temp_liststore_factory()
        self.gui_model.project_treeview.list_treeview.set_model (temp_liststore)

        if widget == self.gui_model.project_treeview.list_treeview:
            # Adding files to the project
            thread = threaded_copy (self,
                                    self.burning_projects[0],
                                    model,
                                    selected_files,
                                    drag_context,
                                    source_treeview,
                                    widget,
                                    None
                                    )
            thread.start()

    def cb_npfs_change_tree_icon (self,column,cell,model,iter):
        if model.get_value(iter,0) == self.gui_model.project_treeview.PROJECT_NAME:
            small_icon = self.icon_theme.load_icon("gnome-dev-cdrom",
                                                24,
                                                gtk.ICON_LOOKUP_FORCE_SVG)
        else :
            small_icon = self.icon_theme.load_icon("gnome-fs-directory",
                                                    24,
                                                    gtk.ICON_LOOKUP_FORCE_SVG)
        cell.set_property('pixbuf', small_icon)

    def cb_npfs_change_list_icon (self,column,cell,model,iter):
        if model.get_value(iter,5) != "0":
            cell.set_property("sensitive",False)
        else:
            cell.set_property("sensitive",True)
        filename =  model.get_value(iter,1)
        try:
            file_type = self.vfs.get_file_type (filename)
        except IndexError:
            file_type = "nodir"
        except gnomevfs.NotSupportedError:
            file_type = "nodir"

        if  file_type == "directory" and model.get_path(iter) == self.gui_view.moving_cell_path :
            print "ok"
            small_icon = self.icon_theme.load_icon("gnome-fs-directory-accept",
                                                24,
                                                gtk.ICON_LOOKUP_FORCE_SVG)
        elif file_type == "directory" :
            small_icon = self.icon_theme.load_icon("gnome-fs-directory",
                                                24,
                                                gtk.ICON_LOOKUP_FORCE_SVG)
        else:
            exten = split(filename,'.')
            small_icon = get_icon (exten[-1],self.icon_theme)

        cell.set_property('pixbuf', small_icon)

    def cb_npfs_change_filename (self,column,cell,model,iter):
        if model.get_value(iter,5) != "0":
            cell.set_property("sensitive",False)
        else:
            cell.set_property("sensitive",True)
        cell.set_property('text',model.get_value(iter,0))
        return

    def cb_npfs_change_url (self,column,cell,model,iter):
        if model.get_value(iter,5) != "0":
            cell.set_property("sensitive",False)
        else:
            cell.set_property("sensitive",True)
        cell.set_property('text',model.get_value(iter,2))
        return

    def cb_npfs_change_size (self,column,cell,model,iter):
        if model.get_value(iter,5) != "0":
            cell.set_property("sensitive",False)
        else:
            cell.set_property("sensitive",True)
        cell.set_property('text',model.get_value(iter,3))
        return

    def cb_npfs_change_mode (self,column,cell,model,iter):
        if model.get_value(iter,5) != "0":
            cell.set_property("sensitive",False)
        else:
            cell.set_property("sensitive",True)
        cell.set_property('text',model.get_value(iter,4))
        return

    def cb_npfs_row_expended (self, treeview, iter, path):
        cursor = gtk.gdk.Cursor(gtk.gdk.WATCH)
        gobject.idle_add(self.gui_model.window.window.set_cursor,cursor)
        model = treeview.get_model()
        child_iter = model.iter_children (iter)
        #Boucle pas bonne
        while child_iter != None:
            if model.iter_children (child_iter) == None:
                self.gui_model.project_treeview.populate_treestore_iter_with_files (model,child_iter)
            child_iter = model.iter_next(child_iter)
        cursor = gtk.gdk.Cursor(gtk.gdk.TOP_LEFT_ARROW)
        gobject.idle_add(self.gui_model.window.window.set_cursor,cursor)

    def cb_npfs_cursor_changed (self, treeview, path=None, column=None):
        cursor_watch(self.gui_model.window)
        (model,iter) = treeview.get_selection().get_selected()

        # Change the value of the global iter attribute
        self.gui_view.current_treeiter = iter

        # Get the absolute directory to show
        dirname = model.get_value(iter,1)
        self.burning_projects[0].set_current_dir (dirname)
        print "building list"

        # Adds file nodes to xml tree if needed
        self.vfs.explore_dir2 (dirname)

        liststore = self.gui_model.project_treeview.directory_liststore_factory (dirname)
        print "list build"
        self.liststore = liststore
        self.current_liststore = liststore
        self.gui_model.project_treeview.list_treeview.set_model (liststore)
        cursor = gtk.gdk.Cursor(gtk.gdk.WATCH)
        self.gui_model.window.window.set_cursor(cursor)
        cursor = gtk.gdk.Cursor(gtk.gdk.TOP_LEFT_ARROW)
        gobject.idle_add(self.gui_model.window.window.set_cursor,cursor)

    def cb_npfs_drag_data_get (self,treeview, context, selection,target_id,etime):
        tree_selection = treeview.get_selection()
        model,iter = tree_selection.get_selected()

        if model.get_value(iter,5) != "0":
            return

        data = model.get_value(iter,0)
        selection.set (selection.target,8,data)

    def cb_npfs_drag_drop_in_treeview (self,widget, drag_context, x, y, timestamp):
        source_widget = drag_context.get_source_widget()
        if widget == self.gui_model.project_treeview.treeview:
            source_selection = source_widget.get_selection()
            (source_model,selected_rows_paths) = source_selection.get_selected_rows()

            dest_model = widget.get_model()
            drop_info = widget.get_dest_row_at_pos(x,y)

            if drop_info:
                dest_path,position = drop_info
                iter = dest_model.get_iter (dest_path)

                regexp_trunc_url = compile(self.vfs.get_url_pattern())
                trunced_url = regexp_trunc_url.match (dest_model.get_value(iter,1))
                # if source directory different from dest dir
                if self.burning_projects[0].get_current_dir() != trunced_url.group(0):
                    for path in selected_rows_paths:
                        file_to_copy = source_model.get_value(source_model.get_iter(path),1)
                        print file_to_copy
                        self.burning_projects[0].move_file (file_to_copy,trunced_url.group(0))

                    self.gui_model.project_treeview.populate_treestore_iter_with_files (
                             dest_model,
                             self.gui_model.project_treeview.root_iter
                             )

                    self.gui_model.project_treeview.treeview.expand_to_path(dest_path)
                    dirname = dest_model.get_value(dest_model.get_iter(dest_path),1)
                    liststore = self.gui_model.project_treeview.directory_liststore_factory (dirname)
                    self.gui_model.project_treeview.list_treeview.set_model(liststore)
                    self.gui_view.current_treeiter = iter

            else:
                for path in selected_rows_paths:
                    file_to_copy = source_model.get_value(source_model.get_iter(path),1)
                    self.burning_projects[0].move_file (file_to_copy,self.burning_projects[0].get_base_dir())

                self.gui_model.project_treeview.populate_treestore_iter_with_files (
                            dest_model,
                            self.gui_model.project_treeview.root_iter
                            )
                liststore = self.gui_model.project_treeview.directory_liststore_factory (
                            self.burning_projects[0].get_base_dir()
                            )

                self.gui_model.project_treeview.list_treeview.set_model(liststore)
                self.gui_view.current_treeiter = self.gui_model.project_treeview.root_iter

    def cb_npfs_drag_data_received (self,treeview, context, x,y, selection, info,etime):
        source_widget = context.get_source_widget()
        if source_widget != self.gui_model.project_treeview.treeview:
            return

        else:
            model = treeview.get_model()
            data = selection.data
            drop_info = treeview.get_dest_row_at_pos(x,y)
            self.drag_drop_cancel = False
            if drop_info:
                path,position = drop_info
                iter = model.get_iter (path)

                regexp_trunc_url = compile("(/.*/)(.*)")
                trunced_url = regexp_trunc_url.match (model.get_value(iter,1))

                if self.burning_projects[0].get_current_dir() != trunced_url.group(0):
                    model.append(iter,[data,trunced_url.group(0)+os.path.sep+data])
                    self.burning_projects[0].move_file (self.burning_projects[0].get_current_dir(),trunced_url.group(0))
                    self.burning_projects[0].set_current_dir(trunced_url.group(0))
                    updated_liststore = self.gui_model.project_treeview.directory_liststore_factory (self.burning_projects[0].get_current_dir())
                    self.liststore = updated_liststore
                    self.current_liststore = updated_liststore
                    self.gui_model.project_treeview.list_treeview.set_model (self.current_liststore)
                    #self.current_treeiter = iter
                else:
                    self.drag_drop_cancel = True

            if context.action == gtk.gdk.ACTION_MOVE:
                if not self.drag_drop_cancel:
                    print "no cancel"
                    context.finish(True,True,etime)
                else:
                    print "cancel"

    def cb_npfs_foreach_row_selected (self,treemodel,path,iter):
        #print self.list_treeview_selection.get_selected_rows()
        self.gui_view.files_selected_list.append (path)

    def cb_npfs_button_pressed (self,widget,data):
        path = widget.get_path_at_pos(int(data.x), int(data.y))
        widget.get_selection().selected_foreach(self.cb_npfs_foreach_row_selected)

        if data.button == 3:
            if path != None:
                self.gui_model.edit_menu.get_submenu().popup (None,None,None,data.button,data.time)
            else:
                self.gui_model.edit_menu2.get_submenu().popup (None,None,None,data.button,data.time)

        if data.button == 1 and data.type == gtk.gdk._2BUTTON_PRESS and path != None:
            try:
                iter = widget.get_model().get_iter(path[0])
                self.gui_view.current_treeiter = self.gui_model.project_treeview.get_current_iter_children (
                    self.gui_model.project_treeview.treeview.get_model(),
                    self.gui_view.current_treeiter,
                    widget.get_model().get_value(iter,0)
                    )
            except TypeError,err:
                return
            if (self.gui_view.current_treeiter != None):
                self.gui_model.project_treeview.treeview.expand_to_path(
                    self.gui_model.project_treeview.treeview.get_model().get_path(
                        self.gui_view.current_treeiter)
                    )
            widget.emit("row-activated", widget.get_model().get_path(iter),widget.get_column(0))

        elif data.button == 1 and self.__npfs_cbid_drag_motion == None and path != None:
            self.gui_model.project_treeview.list_treeview.unset_rows_drag_dest()
            self.__npfs_cbid_drag_motion = self.gui_model.project_treeview.list_treeview.connect("motion_notify_event", self.cb_npfs_drag_motion, data.copy() )
            self.__npfs_cbid_drag_end = self.gui_model.project_treeview.list_treeview.connect("button_release_event", self.cb_npfs_button_release, data.copy() )
            return True

    def cb_npfs_button_release(self, widget, data, userdata = None):
        self.gui_model.project_treeview.list_treeview.emit("button_press_event", userdata)
        self.__npfs_drag_check_end()

    def cb_npfs_drag_motion(self, widget, data, userdata = None):
        self.gui_model.project_treeview.list_treeview.enable_model_drag_dest ([("text/plain",0,0)],
                                                   gtk.gdk.ACTION_DEFAULT)
        if widget.drag_check_threshold(int(userdata.x), int(userdata.y), int(data.x), int(data.y)) == True:
            self.__npfs_drag_check_end()
            self.gui_model.project_treeview.list_treeview.drag_begin( (("LIST2TREE", gtk.TARGET_SAME_APP | gtk.TARGET_SAME_WIDGET, 0), ), gtk.gdk.ACTION_COPY, userdata.button, userdata)

    def __npfs_drag_check_end(self):
        self.gui_model.project_treeview.list_treeview.enable_model_drag_dest ([("text/plain",0,0)],
                                                   gtk.gdk.ACTION_DEFAULT)
        self.gui_model.project_treeview.list_treeview.disconnect(self.__npfs_cbid_drag_motion)
        self.gui_model.project_treeview.list_treeview.disconnect(self.__npfs_cbid_drag_end)
        self.__npfs_cbid_drag_motion = None
        self.__npfs_cbid_drag_end = None

    def cb_npfs_liststrore_explore_subdir(self, treeview, path, column):
        model = treeview.get_model()
        # Get the row pointed
        iter = model.get_iter(path)
        # Get the absolute directory to show
        dirname = model.get_value(iter,1)
        if self.vfs.get_file_type(dirname) == "directory":
            self.burning_projects[0].set_current_dir(dirname)

            # explore file system to fill xml tree if necessary
            self.vfs.explore_dir2(dirname)

            listmodel = self.gui_model.project_treeview.directory_liststore_factory(dirname)
            self.gui_model.project_treeview.list_treeview.set_model(listmodel)

    def cb_npfs_delete_files (self,action):
        cursor_watch(self.gui_model.window)
        model,selected_paths = self.gui_model.project_treeview.list_treeview_selection.get_selected_rows()



        if len(selected_paths) > 0:
            files_to_delete = []

            for path in selected_paths:
                files_to_delete.append(model.get_value(model.get_iter(path),1))

            self.burning_projects[0].remove_files(files_to_delete)
            self.gui_model.progressbar.set_fraction(self.burning_projects[0].get_used_percent())
            self.gui_model.progressbar.set_text(self.burning_projects[0].get_project_size_inM())
            self.gui_model.project_treeview.populate_treestore_iter_with_files (
                        self.gui_model.project_treeview.treestore,
                        self.gui_view.current_treeiter
                        )
            current_path = self.gui_model.project_treeview.treestore.get_path (self.gui_view.current_treeiter)
            self.gui_model.project_treeview.treeview.expand_to_path(current_path)
            liststore = self.gui_model.project_treeview.directory_liststore_factory (
                self.gui_model.project_treeview.treestore.get_value(self.gui_view.current_treeiter,1)
                )
            self.gui_model.project_treeview.list_treeview.set_model (liststore)
        cursor = gtk.gdk.Cursor(gtk.gdk.TOP_LEFT_ARROW)
        gobject.idle_add(self.gui_model.window.window.set_cursor,cursor)

    def cb_npfs_create_folder (self,action):
        self.gui_model.mkdir_window.show_window()
        return

    ##################################################################################
    # Create Directory Window Callback function
    ##################################################################################
    def cb_mkdir_create_dir (self,button):
        dirname = self.gui_model.mkdir_window.textbox.get_text()
        if dirname != "":
            self.burning_projects[0].create_dir (dirname)
            self.gui_model.mkdir_window.hide_window()
            liststore = self.gui_model.project_treeview.directory_liststore_factory (
                    self.burning_projects[0].get_current_dir()
                    )
            self.gui_model.project_treeview.populate_treestore_iter_with_files (
                                            self.gui_model.project_treeview.treestore,
                                            self.gui_view.current_treeiter
                                            )
            self.gui_model.project_treeview.list_treeview.set_model(liststore)
            self.gui_model.project_treeview.treeview.expand_to_path (
                    self.gui_model.project_treeview.treeview.get_model().get_path(self.gui_view.current_treeiter)
            )
        else:
            return

    def cb_mkdir_cancel_creation (self,button):
        self.gui_model.mkdir_window.hide_window()
        return

    ###################################################################################
    # Projects Selection Window Callback Function
    ###################################################################################
    def cb_pw_on_the_fly (self,togglebutton,project_id):
        if project_id == -1:
            # Main Project Window signal
            self.root_projects[COPY_CD_PROJECT].on_the_fly = togglebutton.get_active()
            print self.root_projects[COPY_CD_PROJECT].on_the_fly
        else:
            # Sub Project window Signal
            self.burning_projects[project_id].iso9660_tool.on_the_fly = togglebutton.get_active()

    def cb_pw_reader_device (self,combobox,reader_keys,project_id):
        model = combobox.get_model()
        hbox = combobox.get_parent()
        speed_combobox = hbox.get_children()[1]
        active_index = combobox.get_active()

        if project_id == -1:
            self.root_projects[COPY_CD_PROJECT].reader_device = reader_keys[active_index]
        else:
            self.burning_projects[project_id].reader_device = reader_keys[active_index]

        self.cdrdao_tools.reader_device = reader_keys[active_index]

        speed_combobox.destroy()

        speed_combobox = gtk.combo_box_new_text()
        speed_combobox.append_text("Auto")

        device_features = self.dev_manager.get_drive_features(reader_keys[active_index])
        for speed in device_features.cd_speeds:
            speed_combobox.append_text(speed)
        speed_combobox.set_active(0)

        hbox.pack_start(speed_combobox,False,False,5)
        speed_combobox.show()

    def cb_pw_switch_icon_boxes(self,combobox):

        if self.gui_model.proj_window is None:
            return

        model = combobox.get_model()
        active_iter = combobox.get_active_iter()
        if model.get_value (active_iter,0) == "CD":
            self.gui_model.proj_window.switch_icon_boxes("cd")
            self.gui_view.project_media = "cd"
        else:
            self.gui_model.proj_window.switch_icon_boxes("dvd")
            self.gui_view.project_media = "dvd"

    def cb_pw_iconbox_clicked (self,widget,event,icon_boxes):
        for icon_box in icon_boxes:
            icon_box.set_state(gtk.STATE_NORMAL)

        widget.set_state(gtk.STATE_SELECTED)
        label_selected = widget.get_child().get_children()[1].get_label()
        print label_selected
        self.gui_model.proj_window.current_project_selected = label_selected
        self.gui_model.proj_window.modify_tabs(label_selected)

    #
    # This function is called when 'create' button in pressed
    # It results a new burning project is created
    #
    def cb_pw_choose_image_dir (self,button,entry,window):
        filew = gtk.FileChooserDialog ("Choose Directory",window,gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        filew.connect ("response",self.cb_dialwin_file_choosen,entry)
        filew.run()

    def cb_pw_cdtext_title_lose_focus (self,widget,event):
        self.burning_projects[self.current_project].toc.global_cd_text.title = widget.get_text()

    def cb_pw_cdtext_performer_lose_focus (self,widget,event):
        self.burning_projects[self.current_project].toc.global_cd_text.performer = widget.get_text()

    def cb_pw_cdtext_arranger_lose_focus (self,widget,event):
        self.burning_projects[self.current_project].toc.global_cd_text.arranger = widget.get_text()

    def cb_pw_cdtext_songwriter_lose_focus (self,widget,event):
        self.burning_projects[self.current_project].toc.global_cd_text.songwriter = widget.get_text()

    def cb_pw_cdtext_composer_lose_focus (self,widget,event):
        self.burning_projects[self.current_project].toc.global_cd_text.composer = widget.get_text()

    def cb_pw_cdtext_upc_lose_focus (self,widget,event):
        self.burning_projects[self.current_project].toc.global_cd_text.upc_ean = widget.get_text()

    def cb_pw_cdtext_diskid_lose_focus (self,widget,event):
        self.burning_projects[self.current_project].toc.global_cd_text.disk_id = widget.get_text()

    def cb_pw_cdtext_message_lose_focus (self):
        self.burning_projects[self.current_project].toc.global_cd_text.message = widget.get_text()


    """
    Callback function that initiate the data project creation process
    """
    def __init_dataCD_project (self):
        # Create New Project window properties
        self.win_burning_projects.append(Projects_window (self,self.gui_view,self.current_project))

        projects_window = self.win_burning_projects[self.current_project].get_window()
        projects_window.set_transient_for(self.gui_model.window)
        projects_window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)

        self.win_burning_projects[self.current_project].modify_tabs ("Data CD (iso9660)")

        # Add the progressbar to the main window
        self.bubble_progressbar = bubbledisk_progressbar("mo","cdrom")
        progress_frame = self.bubble_progressbar.get()
        self.gui_model.progressbar = self.bubble_progressbar.progressbar
        self.gui_model.progressbar_hbox.pack_start(progress_frame,True,True)
        self.gui_model.progressbar_hbox.show_all()

        # Create new project
        self.burning_projects.append (iso9660_project ("bubbledisk",
                                                       "700000",
                                                       "800000",
                                                       self.isofs_tool,
                                                       self.cdrecord_tool,
                                                       self.config_handler.get ("misc/tempdir"),
                                                       self.vfs,self.dev_manager,
                                                       self.cdrdao_tools
                                                       )
                                     )
        self.gui_model.build_project_treeview (self.burning_projects[0])

        multisessornot = self.burning_projects[self.current_project-1].burning_tool.multisess

        if multisessornot == "Continue a multisession Disk" or multisessornot == "Finish a multisession Disk":
            try:
                cursor_watch(self.gui_model.window)
                self.dev_manager.mount_current_writer()
                time.sleep(5)
                self.__cursor_left_arrow(self.gui_model.window)

                self.burning_projects[self.current_project-1].iso9660_tool.multisess = True
                infos = self.cdrdao_tools.get_disk_infos()
                self.burning_projects[self.current_project-1].iso9660_tool.last_sess_start = infos[1]["Start of last session"]
                self.burning_projects[self.current_project-1].iso9660_tool.next_sess_start = infos[1]["Start of new session"]
                self.parent_dropped_dir = self.burning_projects[self.current_project-1].current_dir
                import_sess_window = bubble_windows.import_session_window(self.dev_manager)
                import_sess_window.get_window().set_transient_for(self.gui_model.window)
                import_sess_thread = Threaded_import_session(self.burning_projects[self.current_project-1],
                                                              self,
                                                              import_sess_window
                                                              )
                import_sess_thread.start()

            except DeviceNotFoundError:
                print "DeviceNotFoundError"
                self.burning_projects[self.current_project-1].burning_tool = "No multisession Disk"

        self.gui_model.projects_window.hide()
        self.gui_view.set_data_project_view()

#####################################################################
#    Copy cd callbacks
#####################################################################
    def __init_copyCD_project (self,project_id):
        # Create new project

        print threading.currentThread()
        # TODO: assign a copy of the object
        copy_cd_project = self.root_projects[COPY_CD_PROJECT]

        self.burning_projects.append (copy_cd_project)

        self.gui_model.projects_window.hide()

        # Copying window
        ww = copying_window(self,copy_cd_project)
        ww.window.set_transient_for(self.gui_model.window)
        ww.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        ww.show_window()
        ww.close_button.hide()
        ww.analysing_disk_notification()


        # Error dialog boxes
        dialog1 = gui_tools.dialog_box(gtk.MESSAGE_ERROR,
                                            'Please insert a disk in the writer device',
                                            self.gui_model.projects_window)

        # Checks there is a disk in the media tray and the type of disk
        self.check_ok = False

        while not self.check_ok:
            self.__checks_device_non_empty_for_reading(copy_cd_project)

        if copy_cd_project.type == self.cdrdao_tools.DATA_DISK or copy_cd_project.type == self.cdrdao_tools.AUDIO_DISK:
            # Checks copy on the fly
            if not copy_cd_project.on_the_fly:
                dialog1.connect ("response", self.cb_write_after_reading,ww,copy_cd_project)

                # Starts reading disk and store image on hard disk
                reading_thread = Threaded_copy_reading (copy_cd_project,ww,dialog1,self)
                reading_thread.start()
            else:
                # TODO
                pass
        elif copy_cd_project.type == self.cdrdao_tools.EXTRA_DISK:
            print "Extra Disk"
            pass

        # Multi session disk
        else:
            dialog1.connect ("response", self.cb_multisess_write_after_reading,ww,copy_cd_project)
            # Starts reading disk and store image on hard disk
            reading_thread = Threaded_multisess_copy_reading (copy_cd_project,ww,dialog1,self)
            reading_thread.start()
            pass


    def after_reading_dialog (self,dialog):
        dialog.show()

    def cb_close_copy_reading (self,action,copying_window):
        copying_window.window.destroy()

    def cb_cancel_copy_reading (self,action,copying_window):
        copying_window.abort_process()
        try:
            os.kill(copying_window.pid+1,15)
        except OSError:
            os.kill(copying_window.pid+2,15)

        copying_window.window.destroy()

    def cb_multisess_write_after_reading (self, window,r,writing_window,copy_cd_project):
        window.destroy()

        #self.gui_model.window.set_sensitive(True)
        # Checks there is a disk in the media tray of writer device
        self.check_ok = False
        while not self.check_ok:
            self.__checks_device_non_empty_for_writing(copy_cd_project)

        # Checks there is a blank disk in the media tray
        self.check_ok = False
        while not self.check_ok:
            self.__checks_blank_disk(copy_cd_project)

        # Init window for copy
        writing_window.begin_copy_writing_disk_notification()

        writing_thread = Threaded_multisess_copy_writing (copy_cd_project,writing_window)
        writing_thread.start()

    def cb_write_after_reading (self, window,r,writing_window,copy_cd_project):
        window.destroy()

        #self.gui_model.window.set_sensitive(True)
        # Checks there is a disk in the media tray of writer device
        self.check_ok = False
        while not self.check_ok:
            self.__checks_device_non_empty_for_writing(copy_cd_project)

        # Checks there is a blank disk in the media tray
        self.check_ok = False
        while not self.check_ok:
            self.__checks_blank_disk(copy_cd_project)

        # Init window for copy
        writing_window.begin_copy_writing_disk_notification()

        writing_thread = Threaded_copy_writing (copy_cd_project,writing_window)
        writing_thread.start()

    #
    # Checks there is a disk in the media tray of reader device
    #
    def __checks_device_non_empty_for_reading (self,project):
        try:
            print "Checks disk not mounted"
            # Checks disk not mounted
            if self.dev_manager.is_current_writer_mounted():
                print "I'm going to unmount current reader"
                self.dev_manager.unmount_current_writer()

            cursor_watch(self.gui_model.window)
            project.check_cd_type()
            gui_tools.cursor_left_arrow(self.gui_model.window)
            self.check_ok = True
        except DeviceEmptyError:
            dialog = gui_tools.dialog_box(gtk.MESSAGE_ERROR,
                                            'Please insert a disk in the reader device and press Ok',
                                            self.gui_model.projects_window)
            dialog.connect ("response", self.__cb_device_empty_for_reading)
            dialog.run()

    def __cb_device_empty_for_reading (self, window,r):
        window.destroy()

    #
    # Checks there is a disk in the media tray of writer device
    #
    def __checks_device_non_empty_for_writing (self,project):
        try:
            # Checks disk not mounted
            if self.dev_manager.is_current_writer_mounted():
                print "I'm going to unmount current reader"
                self.dev_manager.unmount_current_writer()

            cursor_watch(self.gui_model.window)
            self.dev_manager.media_in_current_writer()
            gui_tools.cursor_left_arrow(self.gui_model.window)
            self.check_ok = True

        except NoMediaInDeviceError:
            dialog = gui_tools.dialog_box(gtk.MESSAGE_ERROR,
                                            'Please insert a disk in the writer device and press Ok',
                                            self.gui_model.projects_window)
            dialog.connect ("response", self.__cb_device_empty_for_writing)
            dialog.run()

    def __cb_device_empty_for_writing (self, window,r):
        window.destroy()

    def __checks_blank_disk (self,project):
        try:
            # Checks disk not mounted
            if self.dev_manager.is_current_writer_mounted():
                print "I'm going to unmount current reader"
                self.dev_manager.unmount_current_writer()

            cursor_watch(self.gui_model.window)
            keys,infos = self.cdrdao_tools.get_disk_infos()
            gui_tools.cursor_left_arrow(self.gui_model.window)

            if infos ["CD-R empty"] != "yes":
                raise NonBlankDiskError

            self.check_ok = True

        except NonBlankDiskError:
            dialog = gui_tools.dialog_box(gtk.MESSAGE_ERROR,
                                            'Please insert a blank disk in the writer device and press Ok',
                                            self.gui_model.projects_window)
            dialog.connect ("response", self.__cb_not_blank_disk)
            dialog.run()

    def __cb_not_blank_disk (self, window ,copy_cd_project):
        window.destroy()

    def __cb_destroy_dialog_box (self, window,r,copy_cd_project,project_id):
        window.destroy()
        self.__init_copyCD_thread(copy_cd_project,project_id)


    def cb_pw_hide_window (self,widget,project_id):
        self.current_project+=1

        """
        self.win_burning_projects.append(Projects_window (self,self.gui_view,self.current_project))

        projects_window = self.win_burning_projects[self.current_project].get_window()
        projects_window.set_transient_for(self.gui_model.window)
        projects_window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)

        self.win_burning_projects[self.current_project].hide_widgets_after_iso_creation("cd","Copy CD")
        self.win_burning_projects[self.current_project].modify_tabs ("Copy CD")
        self.__refresh_frames ()
        """

        if self.gui_model.proj_window.get_current_project_selected() == "Data CD (iso9660)":
            self.__init_dataCD_project()

        elif self.gui_model.proj_window.get_current_project_selected() == "Copy CD":
            self.__init_copyCD_project(self.current_project)

        elif self.gui_model.proj_window.get_current_project_selected() == "Audio CD":
            self.__init_audioCD_project(self.current_project)



#===============================================================================
#    def cb_pw_hide_window_cancel (self,widget,data=None):
#        self.gui_model.window.set_sensitive(True)
#        self.gui_model.projects_window.hide_all()
#        col = gtk.gdk.color_parse("#FF00AA")
#        self.gui_model.oversized_status.modify_bg(gtk.STATE_NORMAL,col)
#===============================================================================

    def cb_pw_hide_window_cancel (self,widget,project_id):
        #self.gui_model.window.set_sensitive(True)
        if project_id == -1:
            # we are modifying the root's isofs params object
            self.gui_model.projects_window.hide()
        else:
            # we are modifying one of the isofs params object identified by project_id
            self.win_burning_projects[project_id].window.hide()

        self.gui_model.window.set_sensitive(True)

    def cb_pw_isoparam_toggled(self, cell, path, model,project_id):
        if project_id == -1:
            # we are modifying the root's isofs params object
            isofs_tool = self.isofs_tool
        else:
            # we are modifying one of the isofs params object identified by project_id
            isofs_tool = self.burning_projects[project_id].iso9660_tool

        iter = model.get_iter((int(path),))
        fixed = model.get_value(iter, 0)
        fixed = not fixed
        model.set(iter, 0, fixed)

        first_iter = model.get_iter((0,))
        first_fixed = model.get_value(first_iter, 0)

        if int(path) == 0:
            if fixed:
                model.set(model.get_iter(1), 0, True)
                isofs_tool.relaxed_filenames = fixed
                model.set(model.get_iter(2), 0, True)
                isofs_tool.allow_31_char_fn = fixed
                model.set(model.get_iter(3), 0, True)
                isofs_tool.no_iso_translate = fixed
                model.set(model.get_iter(4), 0, True)
                isofs_tool.allow_leading_dots = fixed
                model.set(model.get_iter(5), 0, True)
                isofs_tool.allow_lowercase = fixed
                model.set(model.get_iter(6), 0, True)
                isofs_tool.allow_multidot = fixed
                model.set(model.get_iter(7), 0, True)
                isofs_tool.omit_trailing_period = fixed
                model.set(model.get_iter(8), 0, True)
                isofs_tool.omit_version_number = fixed

            isofs_tool.allow_untranslated_filenames = fixed

        elif int(path) == 1:
            if first_fixed:
                model.set(model.get_iter(0), 0, False)
                isofs_tool.allow_untranslated_filenames = False
            isofs_tool.relaxed_filenames = fixed
        elif int(path) == 2:
            if first_fixed:
                model.set(model.get_iter(0), 0, False)
                isofs_tool.allow_untranslated_filenames = False
            isofs_tool.allow_31_char_fn = fixed
        elif int(path) == 3:
            if first_fixed:
                model.set(model.get_iter(0), 0, False)
                isofs_tool.allow_untranslated_filenames = False
            isofs_tool.no_iso_translate = fixed
        elif int(path) == 4:
            if first_fixed:
                model.set(model.get_iter(0), 0, False)
                isofs_tool.allow_untranslated_filenames = False
            isofs_tool.allow_leading_dots = fixed
        elif int(path) == 5:
            if first_fixed:
                model.set(model.get_iter(0), 0, False)
                isofs_tool.allow_untranslated_filenames = False
            isofs_tool.allow_lowercase = fixed
        elif int(path) == 6:
            if first_fixed:
                model.set(model.get_iter(0), 0, False)
                isofs_tool.allow_untranslated_filenames = False
            isofs_tool.allow_multidot = fixed
        elif int(path) == 7:
            if first_fixed:
                model.set(model.get_iter(0), 0, False)
                isofs_tool.allow_untranslated_filenames = False
            isofs_tool.omit_trailing_period = fixed
        elif int(path) == 8:
            if first_fixed:
                model.set(model.get_iter(0), 0, False)
                isofs_tool.allow_untranslated_filenames = False
            isofs_tool.omit_version_number = fixed
        elif int(path) == 9:
            isofs_tool.max_iso9660_filenames = fixed
        elif int(path) == 10:
            isofs_tool.gen_transbl = fixed
        elif int(path) == 11:
            isofs_tool.hide_joliet_trans_tbl = fixed

    def cb_pw_on_the_fly_toggled (self,togglebutton,project_id,tempdir_hbox,reader_hbox):
            # Main Project Window signal
            #self.burning_proj.on_the_fly = togglebutton.get_active()
            tempdir_hbox.set_sensitive (not togglebutton.get_active())
            if project_id == -1:
                self.root_projects[COPY_CD_PROJECT].on_the_fly = togglebutton.get_active()

            else:
                # Sub Project window Signal
                self.burning_projects[project_id].on_the_fly = togglebutton.get_active()

    def cb_pw_simulate_copying (self,togglebutton,project_id):
        if project_id == -1:
            self.root_projects[COPY_CD_PROJECT].simulate = togglebutton.get_active()
        else:
            self.burning_projects[project_id].simulate = togglebutton.get_active()

    def cb_pw_ignore_read_errors (self,togglebutton,project_id):
        if project_id == -1:
            self.root_projects[COPY_CD_PROJECT].ignore_read_errors = togglebutton.get_active()
        else:
            self.burning_projects[project_id].ignore_read_errors = togglebutton.get_active()

    def cb_pw_read_sectors_in_raw_mode (self,togglebutton,project_id):
        if project_id == -1:
            self.root_projects[COPY_CD_PROJECT].raw_mode = togglebutton.get_active()
        else:
            self.burning_projects[project_id].raw_mode = togglebutton.get_active()

    def cb_pw_fasttok (self,togglebutton,project_id):
        if project_id == -1:
            self.root_projects[COPY_CD_PROJECT].fasttoc = togglebutton.get_active()
        else:
            self.burning_projects[project_id].fasttoc = togglebutton.get_active()

    def cb_pw_useCDDB (self,togglebutton,project_id):
        if project_id == -1:
            self.root_projects[COPY_CD_PROJECT].useCDDB = togglebutton.get_active()
        else:
            self.burning_projects[project_id].useCDDB = togglebutton.get_active()

    def cb_pw_buffer_underrun (self,togglebutton,project_id):
        if project_id == -1:
            self.root_projects[COPY_CD_PROJECT].buffer_underrun_protection = togglebutton.get_active()
        else:
            self.burning_projects[project_id].buffer_underrun_protection = togglebutton.get_active()

    def cb_pw_write_speed_control (self,togglebutton,project_id):
        if project_id == -1:
            self.root_projects[COPY_CD_PROJECT].write_speed_control = togglebutton.get_active()
        else:
            self.burning_projects[project_id].write_speed_control = togglebutton.get_active()

    def cb_pw_copy_speed_changed (self,combobox,project_id):
        if project_id == -1:
            # Main Project Window signal
            copy_project = self.root_projects[COPY_CD_PROJECT]
        else:
            # Sub Project window Signal
            copy_project = self.burning_projects[project_id]

        model = combobox.get_model()
        active_iter = combobox.get_active_iter()
        if model.get_value (active_iter,0) != "Auto":
            copy_project.writing_speed = model.get_value (active_iter,0)[0:-1]
        else:
            copy_project.writing_speed = model.get_value (active_iter,0)

    def cb_pw_read_speed_changed (self,combobox,project_id):
        if project_id == -1:
            # Main Project Window signal
            copy_project = self.root_projects[COPY_CD_PROJECT]
        else:
            # Sub Project window Signal
            copy_project = self.burning_projects[project_id]

        model = combobox.get_model()
        active_iter = combobox.get_active_iter()
        if model.get_value (active_iter,0) != "Auto":
            copy_project.reading_speed = model.get_value (active_iter,0)[0:-1]
        else:
            cdrecord_tool.reading_speed = model.get_value (active_iter,0)

    def cb_pw_simulation (self,togglebutton,project_id):
        if project_id == -1:
            self.root_projects[COPY_CD_PROJECT].simulate = togglebutton.get_active()
        else:
            self.burning_projects[project_id].simulate = togglebutton.get_active()

    def cb_pw_multisess_copy (self,togglebutton,project_id):
        if project_id == -1:
            self.root_projects[COPY_CD_PROJECT].multisess = not togglebutton.get_active()
        else:
            self.burning_projects[project_id].multisess = not togglebutton.get_active()

    def cb_pw_del_img_after_copy (self,togglebutton,project_id):
        if project_id == -1:
            self.root_projects[COPY_CD_PROJECT].delete_iso_image = togglebutton.get_active()
        else:
            self.burning_projects[project_id].delete_iso_image = togglebutton.get_active()

    def cb_pw_image_entry_lose_focus (self,widget,event,project_id):
        uri = widget.get_text()
        if string.find (uri,":///") != -1:
            uri = gnomevfs.get_local_path_from_uri (uri)

        if project_id == -1:
            self.root_projects[COPY_CD_PROJECT].iso_image = uri
        else:
            self.burning_projects[project_id].iso_image = uri
        widget.set_text(uri)

    def cb_pw_multisess_toggled (self,togglebutton,project_id):
        if project_id == -1:
            # Main Project Window signal
            self.cdrecord_tool.multisess = togglebutton.get_label()
        else:
            # Sub Project window Signal
            self.burning_projects[project_id].burning_tool.multisess = togglebutton.get_label()

    def cb_pw_add_joliet_toggled (self,togglebutton,project_id):
        if project_id == -1:
            # Main Project Window signal
            self.isofs_tool.gen_joliet = togglebutton.get_active()
        else:
            # Sub Project window Signal
            self.burning_projects[project_id].iso9660_tool.gen_joliet = togglebutton.get_active()

    def cb_pw_add_rr_toggled (self,togglebutton,project_id):
        if project_id == -1:
            # Main Project Window signal
            self.isofs_tool.gen_rock_ridge_ext = togglebutton.get_active()
        else:
            # Sub Project window Signal
            self.burning_projects[project_id].iso9660_tool.gen_rock_ridge_ext = togglebutton.get_active()

    def cb_pw_add_udf_toggled (self,togglebutton,project_id):
        if project_id == -1:
            # Main Project Window signal
            self.isofs_tool.udf = togglebutton.get_active()
        else:
            # Sub Project window Signal
            self.burning_projects[project_id].iso9660_tool.udf = togglebutton.get_active()

    def cb_pw_simulate_writing (self,togglebutton,project_id):
        if project_id == -1:
            # Main Project Window signal
            self.cdrecord_tool.simulation = togglebutton.get_active()
        else:
            # Sub Project window Signal
            self.burning_projects[project_id].burning_tool.simulation = togglebutton.get_active()

    def cb_pw_writing (self,togglebutton,project_id):
         if project_id == -1:
            # Main Project Window signal
            self.cdrecord_tool.write = togglebutton.get_active()
         else:
            # Sub Project window Signal
            self.burning_projects[project_id].burning_tool.write = togglebutton.get_active()

    def cb_pw_fixate (self,togglebutton,project_id):
        if project_id == -1:
            # Main Project Window signal
            self.cdrecord_tool.fixating = togglebutton.get_active()
        else:
            # Sub Project window Signal
            self.burning_projects[project_id].burning_tool.fixating = togglebutton.get_active()

    def cb_pw_write_method_changed (self,combobox,project_id):
        model = combobox.get_model()
        active_iter = combobox.get_active_iter()
        if project_id == -1:
            # Main Project Window signal
            self.cdrecord_tool.write_method = model.get_value (active_iter,0)
        else:
            # Sub Project window Signal
            self.burning_projects[project_id].burning_tool.write_method = model.get_value (active_iter,0)

    def cb_pw_dev_speed_changed (self,combobox,project_id):
        if project_id == -1:
            # Main Project Window signal
            burning_tool = self.cdrecord_tool
        else:
            # Sub Project window Signal
            burning_tool = self.burning_projects[project_id].burning_tool
        model = combobox.get_model()
        active_iter = combobox.get_active_iter()
        if model.get_value (active_iter,0) != "Auto":
            burning_tool.speed = model.get_value (active_iter,0)[0:-1]
        else:
            burning_tool.speed = model.get_value (active_iter,0)

    def cb_pw_iso_level_changed (self,combobox,project_id):
        if project_id == -1:
            # Main Project Window signal
            isofs_tool = self.isofs_tool
        else:
            # Sub Project window Signal
            isofs_tool = self.burning_projects[project_id].iso9660_tool
        #self.isofs_tool.iso_level = togglebutton.get_label()[-1]
        model = combobox.get_model()
        active_iter = combobox.get_active_iter()
        iso_level = model.get_value (active_iter,0)
        isofs_tool.iso_level = iso_level[-1]
        print isofs_tool.iso_level

    def cb_pw_trackmode_changed (self,combobox,project_id):
        if project_id == -1:
            # Main Project Window signal
            cdrecord_tool = self.cdrecord_tool
        else:
            # Sub Project window Signal
            cdrecord_tool = self.burning_projects[project_id].burning_tool
        model = combobox.get_model()
        active_iter = combobox.get_active_iter()
        track_mode = model.get_value (active_iter,0)
        cdrecord_tool.track_mode = track_mode
        print cdrecord_tool.track_mode

    def cb_pw_volname_lose_focus (self,widget,event,project_id):
        if project_id == -1:
            self.isofs_tool.volume_id = widget.get_text()
        else:
            self.burning_projects[project_id].iso9660_tool.volume_id = widget.get_text()

    def cb_pw_sysname_lose_focus (self,widget,event,project_id):
        if project_id == -1:
            self.isofs_tool.sys_id = widget.get_text()
        else:
            self.burning_projects[project_id].iso9660_tool.sys_id = widget.get_text()

    def cb_pw_volset_lose_focus (self,widget,event,project_id):
        if project_id == -1:
            self.isofs_tool.volset = widget.get_text()
        else:
            self.burning_projects[project_id].iso9660_tool.volset = widget.get_text()

    def cb_pw_publisher_lose_focus (self,widget,event,project_id):
        if project_id == -1:
            self.isofs_tool.publisher = widget.get_text()
        else:
            self.burning_projects[project_id].iso9660_tool.publisher = widget.get_text()

    def cb_pw_preparer_lose_focus (self,widget,event,project_id):
        if project_id == -1:
            self.isofs_tool.preparer = widget.get_text()
        else:
            self.burning_projects[project_id].iso9660_tool.preparer = widget.get_text()

    def cb_pw_application_lose_focus (self,widget,event,project_id):
        if project_id == -1:
            self.isofs_tool.application_id = widget.get_text()
        else:
            self.burning_projects[project_id].iso9660_tool.application_id = widget.get_text()

    def cb_pw_copyright_lose_focus (self,widget,event,project_id):
        if project_id == -1:
            self.isofs_tool.copyright = widget.get_text()
        else:
            self.burning_projects[project_id].iso9660_tool.copyright = widget.get_text()

    def cb_pw_biblio_lose_focus (self,widget,event,project_id):
        if project_id == -1:
            self.isofs_tool.biblio = widget.get_text()
        else:
            self.burning_projects[project_id].iso9660_tool.biblio = widget.get_text()

    def cb_pw_charset_changed (self,combobox,project_id):
        if project_id == -1:
            # Main Project Window signal
            isofs_tool = self.isofs_tool
        else:
            # Sub Project window Signal
            isofs_tool = self.burning_projects[project_id].iso9660_tool
        model = combobox.get_model()
        active_iter = combobox.get_active_iter()
        charset = model.get_value (active_iter,0)
        isofs_tool.input_charset = charset

    def cb_pw_finalize_project (self,widget,project_id):

        if self.gui_model.proj_window.get_current_project_selected() == "Data CD (iso9660)":
            self.win_burning_projects[project_id].window.hide()
            ww = burning_window(self,self.burning_projects[0])
            ww.window.set_transient_for(self.gui_model.window)
            ww.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
            writing_thread = Threaded_writing (self.burning_projects[0],ww)
            writing_thread.start()

        elif self.gui_model.proj_window.get_current_project_selected() == "Audio CD":
            self.win_burning_projects[project_id].window.hide()
            ww = audio_burning_window(self,self.burning_projects[0])
            ww.window.set_transient_for(self.gui_model.window)
            ww.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
            ww.show_window()
            self.burning_projects[0].convert(ww)


    def cb_pw_hide_window_ok(self,widget,data=None):
        self.win_burning_projects[self.current_project].window.hide()


    def cb_pw_cdtext_title_lose_focus (self,widget,event,project_id):
        if project_id != -1:
            self.burning_projects[project_id].toc.get_default_global_cd_text().title = widget.get_text()

    def cb_pw_cdtext_performer_lose_focus (self,widget,event,project_id):
        if project_id != -1:
            self.burning_projects[project_id].toc.get_default_global_cd_text().performer = widget.get_text()

    def cb_pw_cdtext_arranger_lose_focus (self,widget,event,project_id):
        if project_id != -1:
            self.burning_projects[project_id].toc.get_default_global_cd_text().arranger = widget.get_text()

    def cb_pw_cdtext_songwriter_lose_focus (self,widget,event,project_id):
        if project_id != -1:
            self.burning_projects[project_id].toc.get_default_global_cd_text().songwriter = widget.get_text()

    def cb_pw_cdtext_composer_lose_focus (self,widget,event,project_id):
        if project_id != -1:
            self.burning_projects[project_id].toc.get_default_global_cd_text().composer = widget.get_text()

    def cb_pw_cdtext_upc_lose_focus (self,widget,event,project_id):
        if project_id != -1:
            self.burning_projects[project_id].toc.get_default_global_cd_text().upc_ean = widget.get_text()

    def cb_pw_cdtext_diskid_lose_focus (self,widget,event,project_id):
        if project_id != -1:
            self.burning_projects[project_id].toc.get_default_global_cd_text().disc_id = widget.get_text()

    def cb_pw_cdtext_message_lose_focus (self,widget,event,project_id):
        if project_id != -1:
            self.burning_projects[project_id].toc.get_default_global_cd_text().message = widget.get_text()


#===============================================================================
#Properties Window Callback Function
#===============================================================================
    def cb_show_properties_window (self,action):
    	self.gui_model.properties_window.show_window()


    def cb_propw_cancel (self,widget,data=None):
        self.gui_model.properties_window.hide_window ()

    def cb_propw_apply (self,widget,data=None):
        return

    def cb_propw_ok (self,widget,data=None):
        self.gui_model.properties_window.hide_window ()

    def cb_propw_change_pixbuf  (self,column,cell,model,iter):
        if model.get_value(iter,0) == "Readers":
            small_icon = self.icon_theme.load_icon("gnome-dev-cdrom",
                                                24,
                                                gtk.ICON_LOOKUP_FORCE_SVG)

        elif model.get_value(iter,0) == "Writers":
            small_icon = gtk.gdk.pixbuf_new_from_file_at_size (ICONS_DIR+"/gnome-dev-dvdram.png",24,24)

        else: small_icon=None

        cell.set_property('pixbuf', small_icon)

    def cb_propw_change_pixbuf_for_backends (self,column,cell,model,iter):
        if model.get_value (iter,2) == "TRUE":
            if model.get_value (iter,0) == '<span foreground="#FF0000">Not installed</span>' :
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (ICONS_DIR+"/stock_cancel_20.png",24,24)
            else:
                pixbuf = gtk.gdk.pixbuf_new_from_file_at_size (ICONS_DIR+"/stock_apply_20.png",24,24)
            cell.set_property('pixbuf', pixbuf)
        else:
            cell.set_property('pixbuf', None)

    def cb_propw_refresh(self,widget,data=None):
        self.app_manager.search_applications()
        self.properties_window.refresh_treestore()
        self.properties_window.backends_treeview.expand_all()

    def cb_propw_enable_local_cddb_check_box_toggled (self,checkbox,config,key):
        if checkbox.get_active():
            config.set(key,True)
        else:
            config.set(key,False)

    def cb_propw_save_cddb_entries_check_box_toggled (self,checkbox,config,key):
        if checkbox.get_active():
            config.set(key,True)
        else:
            config.set(key,False)

    def cb_propw_addcddbdir (self,button,liststore,entry,config,key):
        dir = entry.get_text()
        iter = liststore.append()
        liststore.set(iter,
                        0,dir,
                        )

        dir_list = config.get (key)
        if dir_list == "":
            config.set (key,dir)
        else:
            config.set (key, dir_list+";"+dir)

    def cb_propw_removecddbdir (self,button,treeview,config,key):
        selection = treeview.get_selection()
        model,rows_selected = selection.get_selected_rows()
        if len(rows_selected) is 1:
            selected_iter = model.get_iter(rows_selected[0])
            model.remove (selected_iter)

            iter = model.get_iter_first()
            dir_list = ""
            while iter != None:
                dir_list += "%s;"%model.get_value(iter,0)
                iter = model.iter_next(iter)

            dir_list = dir_list[0:-1]
            config.set (key,dir_list)

    def cb_propw_up_cddbdir (self,button,treeview,config,key):
        selection = treeview.get_selection()
        model,rows_selected = selection.get_selected_rows()
        if len(rows_selected) is 1 and rows_selected[0][0] != 0:
            prev = (rows_selected[0][0]-1,)
            iter_prev = model.get_iter (prev)
            iter = model.get_iter (rows_selected[0])
            model.swap (iter_prev,iter)

            iter = model.get_iter_first()
            dir_list = ""
            while iter != None:
                dir_list += "%s;"%model.get_value(iter,0)
                iter = model.iter_next(iter)

            dir_list = dir_list[0:-1]
            config.set (key,dir_list)

    def cb_propw_down_cddbdir (self,button,treeview,config,key):
        selection = treeview.get_selection()
        model,rows_selected = selection.get_selected_rows()
        if len(rows_selected) is 1 and rows_selected[0][0] != model.iter_n_children(None) -1:
            prev = (rows_selected[0][0]+1,)
            iter_prev = model.get_iter (prev)
            iter = model.get_iter (rows_selected[0])
            model.swap (iter_prev,iter)

            iter = model.get_iter_first()
            dir_list = ""
            while iter != None:
                dir_list += "%s;"%model.get_value(iter,0)
                iter = model.iter_next(iter)

            dir_list = dir_list[0:-1]
            config.set (key,dir_list)

    def cb_propw_enable_cddb_check_box_toggled (self,checkbox,config,key):
        if checkbox.get_active():
            config.set(key,True)
        else:
            config.set(key,False)

    def cb_propw_addcddbserver (self,button,liststore,protocol_combo,entry,port_spin,config,key):
        server = entry.get_text()

        model = protocol_combo.get_model()
        iter = protocol_combo.get_active_iter()
        protocol = model.get_value (iter,0)

        port = int(port_spin.get_value())

        iter = liststore.append()
        liststore.set(iter,
                        0,protocol,
                        1,server,
                        2,port,
                        )

        server_list = config.get (key)
        config.set (key, server_list+",%s://%s:%s"%(protocol,server,port))

    def cb_propw_removecddbserver (self,button,treeview,config,key):
        selection = treeview.get_selection()
        model,rows_selected = selection.get_selected_rows()
        if len(rows_selected) is 1:
            selected_iter = model.get_iter(rows_selected[0])
            model.remove (selected_iter)

            iter = model.get_iter_first()
            servers_list = ""
            while iter != None:
                servers_list += "%s://%s:%s,"%(model.get_value(iter,0),
                                               model.get_value(iter,1),
                                               model.get_value(iter,2))
                iter = model.iter_next(iter)
            servers_list = servers_list[0:-1]
            config.set (key,servers_list)


    def cb_propw_up_cddbserver (self,button,treeview,config,key):
        selection = treeview.get_selection()
        model,rows_selected = selection.get_selected_rows()
        if len(rows_selected) is 1 and rows_selected[0][0] != 0:
            prev = (rows_selected[0][0]-1,)
            iter_prev = model.get_iter (prev)
            iter = model.get_iter (rows_selected[0])
            model.swap (iter_prev,iter)

            iter = model.get_iter_first()
            servers_list = ""
            while iter != None:
                servers_list += "%s://%s:%s,"%(model.get_value(iter,0),
                                               model.get_value(iter,1),
                                               model.get_value(iter,2))
                iter = model.iter_next(iter)
            servers_list = servers_list[0:-1]
            config.set (key,servers_list)

    def cb_propw_down_cddbserver (self,button,treeview,config,key):
        selection = treeview.get_selection()
        model,rows_selected = selection.get_selected_rows()
        if len(rows_selected) is 1 and rows_selected[0][0] != model.iter_n_children(None) -1:
            prev = (rows_selected[0][0]+1,)
            iter_prev = model.get_iter (prev)
            iter = model.get_iter (rows_selected[0])
            model.swap (iter_prev,iter)

            iter = model.get_iter_first()
            servers_list = ""
            while iter != None:
                servers_list += "%s://%s:%s,"%(model.get_value(iter,0),
                                               model.get_value(iter,1),
                                               model.get_value(iter,2))
                iter = model.iter_next(iter)
            servers_list = servers_list[0:-1]
            config.set (key,servers_list)


    def cb_propw_add (self,button,liststore,entry,config,key):
        path = entry.get_text()
        if path != "":
            if not os.path.isdir(path):
                errorwindow = gtk.MessageDialog(
                        self.properties_window.window,
                        flags=0,
                        type=gtk.MESSAGE_ERROR,
                        buttons=gtk.BUTTONS_CLOSE,
                        message_format="Path is not a valid directory"
                        )
                errorwindow.connect ("response",self.cb_dialwin_ok)
                errorwindow.run()

            else:
                if not path in self.properties_window.application_manager.path:
                    liststore.append([path])
                    self.properties_window.application_manager.path.append(path)
                    full_path = self.properties_window.application_manager.path
                    path_as_string = self.toolbox.create_correct_path (full_path)
                    config.set (key,path_as_string)

    def cb_propw_remove (self,button,treeview,config,key):
        selection = treeview.get_selection()
        model,rows_selected = selection.get_selected_rows()
        if len(rows_selected) is 1:
            selected_iter = model.get_iter(rows_selected[0])
            print self.properties_window.application_manager.path
            self.properties_window.application_manager.path.remove (model.get_value(selected_iter,0))

            full_path = self.properties_window.application_manager.path
            print full_path
            path_as_string = self.toolbox.create_correct_path (full_path)
            config.set (key,path_as_string)
            model.remove (selected_iter)

    def cb_propw_up (self,button,treeview,config,key):
        selection = treeview.get_selection()
        model,rows_selected = selection.get_selected_rows()
        if len(rows_selected) is 1 and rows_selected[0][0] != 0:
            prev = (rows_selected[0][0]-1,)
            iter_prev = model.get_iter (prev)
            iter = model.get_iter (rows_selected[0])
            model.swap (iter_prev,iter)

            path_a = model.get_value(iter_prev,0)
            path_b = model.get_value(iter,0)
            self.toolbox.swap_paths (path_a,path_b,self.properties_window.application_manager.path)

            full_path = self.properties_window.application_manager.path
            path_as_string = self.toolbox.create_correct_path (full_path)
            config.set (key,path_as_string)


    def cb_propw_down (self,button,treeview,config,key):
        selection = treeview.get_selection()
        model,rows_selected = selection.get_selected_rows()
        if len(rows_selected) is 1 and rows_selected[0][0] != len (self.properties_window.application_manager.path) -1:
            prev = (rows_selected[0][0]+1,)
            iter_prev = model.get_iter (prev)
            iter = model.get_iter (rows_selected[0])
            model.swap (iter_prev,iter)

            path_a = model.get_value(iter_prev,0)
            path_b = model.get_value(iter,0)
            self.toolbox.swap_paths (path_a,path_b,self.properties_window.application_manager.path)

            full_path = self.properties_window.application_manager.path
            path_as_string = self.toolbox.create_correct_path (full_path)
            config.set (key,path_as_string)

    def cb_propw_open_file   (self,button,entry,project_id):
        if project_id == -1:
            window = self.gui_model.proj_window.window
        else:
            window = self.win_burning_projects[self.current_project].window

        filew = gtk.FileChooserDialog ("Choose Directory",window,gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
        filew.connect ("response",self.cb_dialwin_file_choosen,entry)
        filew.run()

    def cv_propw_spinbutton1_changed (self,spin1,spin2,spin3,config):
        value1 = (int)(spin1.get_value())
        value2 = (int)(spin2.get_value())
        value3 = (int)(spin3.get_value())

        gconf_value = str(value1)+str(value2)+str(value3)
        config.set ("writing/pregap",gconf_value)

    def cv_propw_spinbutton2_changed (self,spin2,spin1,spin3,config):
        value1 = (int)(spin1.get_value())
        value2 = (int)(spin2.get_value())
        value3 = (int)(spin3.get_value())

        gconf_value = str(value1)+str(value2)+str(value3)
        config.set ("writing/pregap",gconf_value)

    def cv_propw_spinbutton3_changed (self,spin3,spin1,spin2,config):
        value1 = (int)(spin1.get_value())
        value2 = (int)(spin2.get_value())
        value3 = (int)(spin3.get_value())

        gconf_value = str(value1)+str(value2)+str(value3)
        config.set ("writing/pregap",gconf_value)

    def cb_propw_check_box_toggled (self,checkbox,config,key):
        if checkbox.get_active():
            config.set(key,True)
        else:
            config.set(key,False)

    def cb_propw_entry_lose_focus (self,widget,event,config,key):
        uri = widget.get_text()
        if key == "misc/tempdir" and string.find (uri,":///") != -1:
            uri = gnomevfs.get_local_path_from_uri (uri)
        config.set(key,uri)
        widget.set_text(uri)

    def cb_dialwin_ok (self, dialog, id, data=None):
        dialog.hide()

    def cb_dialwin_file_choosen(self, dialog, id, entry):
        entry.set_text(gnomevfs.get_local_path_from_uri(dialog.get_uri()))
        entry.grab_focus()
        dialog.hide()

#===============================================================================
#About Window Callback Function
#===============================================================================
    def cb_about (self,action):
        self.gui_model.about_window.show_all()
        return

#===============================================================================
#Blank Disk Window
#===============================================================================
    def cb_show_blankdisk_window (self,action):
        cursor_watch(self.gui_model.window)
        self.blankdisk_window = blankdisk_window (self,
                                                                      self.gui_view,
                                                                      self.dev_manager,
                                                                      self.app_manager,
                                                                      self.config_handler)
        self.blankdisk_window.window.set_transient_for(self.gui_model.window)
        self.blankdisk_window.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.blankdisk_window.show_window("notNone")
        self.__cursor_left_arrow(self.gui_model.window)

    def cb_hide_blankdisk_window (self,action):
        self.blankdisk_window.hide_window("notNone")
        del self.blankdisk_window

    def cb_blankdisk_window_blank (self,button,device_combo_box,speed_combo_box,blank_mode_combo_box,window):
        blank_project = Blank_disk_project (self.gui_model.app_manager,self.dev_manager,self.cdrdao_tools)

        model = device_combo_box.get_model()
        iter = device_combo_box.get_active_iter()
        device = model.get_value (iter,0)

        model = speed_combo_box.get_model()
        iter = speed_combo_box.get_active_iter()
        speed = model.get_value (iter,0)

        model = blank_mode_combo_box.get_model()
        iter = blank_mode_combo_box.get_active_iter()
        blank_mode = model.get_value (iter,0)

        blank_project.set_device (window.devices[device])
        blank_project.set_speed (speed)
        blank_project.set_blank_mode (blank_mode)

        # Checks disk not mounted
        if self.dev_manager.is_current_writer_mounted():
            print "I'm going to unmount current reader"
            self.dev_manager.unmount_current_writer()

        blank_thread = Threaded_blanking (blank_project,window)
        blank_thread.start()

#===============================================================================
#Choose Recorder Window
#===============================================================================
    def cb_cw_window (self,action):
        cursor_watch(self.gui_model.window)
        self.choose_writer_window = choose_writer_window (
                                        self,
                                        self.gui_view,
                                        self.dev_manager,
                                        self.app_manager)

        self.choose_writer_window.window.set_transient_for (self.gui_model.window)
        self.choose_writer_window.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.choose_writer_window.show_window()
        self.__cursor_left_arrow(self.gui_model.window)

    def cb_hide_cw_window (self,action):
        self.choose_writer_window.hide_window()
        del self.choose_writer_window

    def cb_choose_writer_window_change_writer (self,combobox,frame,writers):
        active = combobox.get_active()
        frame.remove(self.choose_writer_window.setup_hbox)
        current_writer_options = self.dev_manager.get_drive_features(writers[active].get_cdrecord_id()).print_friendly_devices_params ()
        self.choose_writer_window.setup_hbox = gui_tools.devices_options_box(current_writer_options)
        frame.add(self.choose_writer_window.setup_hbox)
        frame.show_all()
        self.dev_manager.used_device = active

#===============================================================================
#Writing Window
#===============================================================================
    def cb_writing_window_change_pixbuf(self,column,cell,model,iter):
        if model.get_value(iter,0).find("WARNING") != -1:
            small_icon = self.icon_theme.load_icon("dialog-warning",
                                                22,
                                                gtk.ICON_LOOKUP_FORCE_SVG)

        elif model.get_value(iter,0).find("ERROR") != -1:
            small_icon = self.icon_theme.load_icon("dialog-information",
                                                22,
                                                gtk.ICON_LOOKUP_FORCE_SVG)
        else:
            small_icon = self.icon_theme.load_icon("dialog-information",
                                                22,
                                                gtk.ICON_LOOKUP_FORCE_SVG)


        cell.set_property('pixbuf', small_icon)

#===============================================================================
#Disk Info Window
#===============================================================================
    def cb_hide_di_window (self,action,window):
        window.hide_all()
        window.destroy()
        del window

    def cb_show_di_window (self,action):
        try:
           if self.dev_manager.media_in_current_writer():
                cursor_watch(self.gui_model.window)
                self.dev_manager.unmount_current_writer()

                window = disk_info_window(self,self.dev_manager,self.app_manager,self.cdrdao_tools)
                window.get_window().set_transient_for(self.gui_model.window)
                window.get_window().set_position(gtk.WIN_POS_CENTER_ON_PARENT)
                window.show_window()
                self.__cursor_left_arrow(self.gui_model.window)
        except NoMediaInDeviceError:
            gui_tools.error_window(self.gui_model.window,"Please insert a Disk")

    def cb_di_change_pixbuf (self,column,cell,model,iter):
        if model.get_value(iter,3) == "AUDIO":
            small_icon = self.icon_theme.load_icon("gnome-dev-cdrom-audio",
                                                    24,
                                                    gtk.ICON_LOOKUP_FORCE_SVG)
        else:
            small_icon = self.icon_theme.load_icon("gnome-dev-cdrom",
                                                    24,
                                                    gtk.ICON_LOOKUP_FORCE_SVG)



        cell.set_property('pixbuf', small_icon)

#===============================================================================
#Audio Browser Callbacks
#===============================================================================
    """
    Callback function that initiate the audio project creation process
    """
    def __init_audioCD_project (self,project_id):
        projects_window = Projects_window (self,self.gui_view,self.current_project, AUDIO_CD)
        projects_window.get_window().set_transient_for(self.gui_model.window)
        projects_window.get_window().set_position(gtk.WIN_POS_CENTER_ON_PARENT)

        self.win_burning_projects.append(projects_window)

        self.gui_model.build_audio_project_widgets ()

        audio_cd_project = AudioCdProject(self.toolbox,self.dev_manager,self.app_manager,self.config_handler,self.cdrdao_tools)
        self.burning_projects.append(audio_cd_project)

        # Add the progressbar t the main window
        self.bubble_progressbar = bubbledisk_progressbar("min","cdrom")
        progress_frame = self.bubble_progressbar.get()
        self.gui_model.progressbar = self.bubble_progressbar.progressbar
        self.gui_model.progressbar_hbox.pack_start(progress_frame,True,True)
        self.gui_model.progressbar_hbox.show_all()

        self.gui_model.projects_window.hide()
        self.gui_model.uiManager.get_widget('/ToolBar/WriteCd').show()


    def cb_ab_drop (self,widget, drag_context, x, y, timestamp):
        # Retrieves row inserted
        source_treeview = drag_context.get_source_widget()
        source_selection = source_treeview.get_selection()
        (model,selected_rows_paths) = source_selection.get_selected_rows()

        selected_files = []
        for path in selected_rows_paths:
            selected_files.append(model.get_value(model.get_iter(path),2))

        audio_project = self.burning_projects[self.current_project]

        songs = []

        for file in selected_files:
            song = Song()
            song.filename = file
            songs.append(song)

        audio_project.add_songs (songs)

        metadataRetriever = MetadataRetriever(songs,self.cb_ab_song_discovered)
        metadataRetriever.discover_songs_metadata()


    def cb_ab_song_discovered (self,song,infos,all_discovered):

        if all_discovered:
            # We can create the liststore
            audio_liststore = gtk.ListStore(str,str,str,str,str)
            i=0
            for song in self.burning_projects[self.current_project].get_songs():
                audio_liststore.append([
                               i,
                               song.artist,
                               song.title,
                               song.length,
                               song.filename])
                i+=1
            self.gui_model.audio_tracks_box.tracks_treeview.set_model (audio_liststore)
        else:
            song_id,artist,title,length,filename = infos

            # Update CD Text data with id3 tags retrievied from song file
            self.burning_projects[self.current_project].toc.tracks.append(Track())
            self.burning_projects[self.current_project].toc.tracks[int(song_id)].get_default_cdText().title = title
            self.burning_projects[self.current_project].toc.tracks[int(song_id)].get_default_cdText().performer = artist

            m,s,ms = length.split(":")

            # Update project size
            self.burning_projects[self.current_project].current_size += int(ms)+1000*int(s)+60000*int(m)

            # Update progressbar status
            self.bubble_progressbar.set_fraction(self.burning_projects[self.current_project].get_current_size())
            self.bubble_progressbar.set_audio_free_space(
                                             self.burning_projects[self.current_project].get_free_space_in_Min_Sec(),
                                             self.burning_projects[self.current_project].get_disk_size_in_Min())

    def cb_ab_cursor_changed (self,treeview):
        # Retrieve the treemodel and iter of the treeview
        (model,iter) = treeview.get_selection().get_selected()

        # Get the absolute directory to show
        song_num = model.get_value(iter,0)

        song = self.burning_projects[self.current_project].songs[int(song_num)]

        self.audio_player.set_current_song(song)

        self.burning_projects[self.current_project].current_selected_song_index = int(song_num)

        self.gui_model.audio_tracks_box.artist_name.set_text(song.artist)
        self.gui_model.audio_tracks_box.artist_title.set_text(song.title)
        self.gui_model.audio_tracks_box.artist_genre.set_text(song.genre)
        self.gui_model.audio_tracks_box.artist_album.set_text(song.album)
        self.gui_model.audio_tracks_box.artist_length.set_text(song.length)

        self.cover_search.get_pixbuf (song, self.cb_amazon_result)


    def cb_ab_number_changed (self,column,cell,model,iter):
        cell.set_property('text',model.get_value(iter,0))
        return

    def cb_ab_artist_changed (self,column,cell,model,iter):
        cell.set_property('text',model.get_value(iter,1))
        return

    def cb_ab_title_changed (self,column,cell,model,iter):
        cell.set_property('text',model.get_value(iter,2))
        return

    def cb_ab_length_changed (self,column,cell,model,iter):
        cell.set_property('text',model.get_value(iter,3))
        return

    def cb_ab_filename_changed (self,column,cell,model,iter):
        cell.set_property('text',model.get_value(iter,4))
        return

    def cb_ab_play_pressed (self,button):
        model,selected_paths = self.gui_model.audio_tracks_box.tracks_treeview.get_selection().get_selected_rows()

        try:
            file = model.get_value(model.get_iter(selected_paths[0]),4)
        except IndexError:
            if (button.get_label() == gtk.STOCK_MEDIA_PAUSE):
                self.audio_player.pause ()
            return

        if button.get_label() == gtk.STOCK_MEDIA_PLAY:
            self.audio_player.start (file)
            button.set_label (gtk.STOCK_MEDIA_PAUSE)
            if self.audio_project_update_id == -1:
                self.audio_project_update_id = gobject.timeout_add(self.gui_model.audio_tracks_box.UPDATE_INTERVAL,
                                                     self.cb_ab_update_scale_cb)
        else:
            self.audio_player.pause (file)
            button.set_label (gtk.STOCK_MEDIA_PLAY)

    def cb_ab_stop_pressed (self,button,play):
        self.audio_player.stop ()

        if (play.get_label() == gtk.STOCK_MEDIA_PAUSE):
                play.set_label (gtk.STOCK_MEDIA_PLAY)

    def cb_amazon_result (self,pixbuf,song):
        if pixbuf != None:
            song.cover = pixbuf
            self.gui_model.audio_tracks_box.cd_sleeve.set_from_pixbuf (song.cover)
        else:
            self.gui_model.audio_tracks_box.cd_sleeve.set_from_file(ICONS_DIR + "/bubble_disk2.png")

    def cb_ab_delete_song (self,action):
        model,selected_paths = self.gui_model.audio_tracks_box.tracks_treeview.get_selection().get_selected_rows()

        try:
            song_index = model.get_value(model.get_iter(selected_paths[0]),0)

            self.burning_projects[self.current_project].remove_song(int(song_index))

            # Update liststore
            liststore = gtk.ListStore(str,str,str,str,str)

            audio_project = self.burning_projects[self.current_project]

            for i in range(audio_project.get_num_songs()):
                liststore.append([
                           i,
                           audio_project.songs[i].artist,
                           audio_project.songs[i].title,
                           audio_project.songs[i].length,
                           audio_project.songs[i].filename])
                self.gui_model.audio_tracks_box.tracks_treeview.set_model(liststore)

            self.bubble_progressbar.set_fraction(self.burning_projects[self.current_project].get_current_size())
            self.bubble_progressbar.set_audio_free_space(
                                             self.burning_projects[self.current_project].get_free_space_in_Min_Sec(),
                                             self.burning_projects[self.current_project].get_disk_size_in_Min())

        except IndexError:
            return

    def cb_ab_button_pressed  (self,widget,data):
        path = widget.get_path_at_pos(int(data.x), int(data.y))
        widget.get_selection().selected_foreach(self.cb_npfs_foreach_row_selected)

        if data.button == 3:
            if path != None:
                self.gui_model.audio_menu.get_submenu().popup (None,None,None,data.button,data.time)
            else:
                self.gui_model.audio_menu.get_submenu().popup (None,None,None,data.button,data.time)

        elif data.button == 1 and data.type == gtk.gdk._2BUTTON_PRESS:
            toc_window = cdtext_track_window(self,self.current_project)

            toc_window.cd_text_entries["Title"].set_text(self.burning_projects[self.current_project].get_current_selected_track().get_default_cdText().title)
            toc_window.cd_text_entries["Performer"].set_text(self.burning_projects[self.current_project].get_current_selected_track().get_default_cdText().performer)
            toc_window.cd_text_entries["Arranger"].set_text(self.burning_projects[self.current_project].get_current_selected_track().get_default_cdText().arranger)
            toc_window.cd_text_entries["Songwriter"].set_text(self.burning_projects[self.current_project].get_current_selected_track().get_default_cdText().songwriter)
            toc_window.cd_text_entries["Composer"].set_text(self.burning_projects[self.current_project].get_current_selected_track().get_default_cdText().composer)
            toc_window.cd_text_entries["ISRC"].set_text(self.burning_projects[self.current_project].get_current_selected_track().get_default_cdText().isrc)
            toc_window.cd_text_entries["Message"].set_text(self.burning_projects[self.current_project].get_current_selected_track().get_default_cdText().message)

            gtk_window = toc_window.get_window()
            gtk_window.set_transient_for(self.gui_model.window)
            gtk_window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
            toc_window.show_window()


    def cb_ab_scale_format_value_cb(self, scale, value):
        if self.audio_p_duration == -1:
            real = 0
        else:
            real = value * self.audio_p_duration / 100

        seconds = real / gst.SECOND

        return "%02d:%02d" % (seconds / 60, seconds % 60)

    def cb_ab_scale_button_press_cb(self, widget, event):
        # see seek.c:start_seek
        gst.debug('starting seek')

        self.was_playing = self.audio_player.is_playing()
        if self.was_playing:
            self.audio_player.pause()

        # don't timeout-update position during seek
        if self.audio_project_update_id != -1:
            gobject.source_remove(self.audio_project_update_id)
            self.audio_project_update_id = -1

        # make sure we get changed notifies
        if self.audio_project_changed_id == -1:
            self.audio_project_changed_id = widget.connect('value-changed',
                self.cb_ab_scale_value_changed_cb)

    def cb_ab_scale_value_changed_cb(self, scale):

        real = long(scale.get_value() * self.audio_p_duration / 100) # in ns
        self.audio_player.seek(real)


    def cb_ab_scale_button_release_cb(self, widget, event):
        # see seek.cstop_seek
        widget.disconnect(self.audio_project_changed_id)
        self.audio_project_changed_id = -1

        if self.was_playing:
            print "restart"
            self.audio_player.start()

        if self.audio_project_update_id != -1:
            raise "Had a previous update timeout id'"
        else:
            self.audio_project_update_id = gobject.timeout_add(self.gui_model.audio_tracks_box.UPDATE_INTERVAL,
                self.cb_ab_update_scale_cb)

    def cb_ab_update_scale_cb(self):
        '''
        @return True if Timeout must be continued, False if timeout use to be shutdown
        '''
        self.audio_p_position, self.audio_p_duration = self.audio_player.query_position()

        if self.audio_p_position != -1 and self.audio_p_position <= self.audio_p_duration:
            value = self.audio_p_position * 100.0 / self.audio_p_duration
            self.gui_model.audio_tracks_box.scale_adjustment.set_value(value)

            return True
        else:
            # Stop the timeout!
            return False

#===============================================================================
#CDTEXT Track Editing Window
#===============================================================================

    def cb_tw_cdtext_arranger_lose_focus (self,widget,event,project_id):
        if project_id != -1:

            # get current song index from project
            track_index = self.burning_projects[project_id].current_selected_song_index

            if track_index != -1:
                language_index = self.burning_projects[project_id].toc.default_language
                track = self.burning_projects[project_id].toc.tracks[track_index]
                track.cd_text[language_index].arranger = widget.get_text()

    def cb_tw_cdtext_title_lose_focus (self,widget,event,project_id):
        if project_id != -1:

            # get current song index from project
            track_index = self.burning_projects[project_id].current_selected_song_index

            if track_index != -1:
                language_index = self.burning_projects[project_id].toc.default_language
                track = self.burning_projects[project_id].toc.tracks[track_index]
                track.cd_text[language_index].title = widget.get_text()

    def cb_tw_cdtext_performer_lose_focus (self,widget,event,project_id):
        if project_id != -1:

            # get current song index from project
            track_index = self.burning_projects[project_id].current_selected_song_index

            if track_index != -1:
                language_index = self.burning_projects[project_id].toc.default_language
                track = self.burning_projects[project_id].toc.tracks[track_index]
                track.cd_text[language_index].performer = widget.get_text()

    def cb_tw_cdtext_songwriter_lose_focus (self,widget,event,project_id):
        if project_id != -1:

            # get current song index from project
            track_index = self.burning_projects[project_id].current_selected_song_index

            if track_index != -1:
                language_index = self.burning_projects[project_id].toc.default_language
                track = self.burning_projects[project_id].toc.tracks[track_index]
                track.cd_text[language_index].songwriter = widget.get_text()

    def cb_tw_cdtext_composer_lose_focus (self,widget,event,project_id):
        if project_id != -1:

            # get current song index from project
            track_index = self.burning_projects[project_id].current_selected_song_index

            if track_index != -1:
                language_index = self.burning_projects[project_id].toc.default_language
                track = self.burning_projects[project_id].toc.tracks[track_index]
                track.cd_text[language_index].composer = widget.get_text()

    def cb_tw_cdtext_isrc_lose_focus (self,widget,event,project_id):
        if project_id != -1:

            # get current song index from project
            track_index = self.burning_projects[project_id].current_selected_song_index

            if track_index != -1:
                language_index = self.burning_projects[project_id].toc.default_language
                track = self.burning_projects[project_id].toc.tracks[track_index]
                track.cd_text[language_index].isrc = widget.get_text()

    def cb_tw_cdtext_message_lose_focus (self,widget,event,project_id):
        if project_id != -1:

            # get current song index from project
            track_index = self.burning_projects[project_id].current_selected_song_index

            if track_index != -1:
                language_index = self.burning_projects[project_id].toc.default_language
                track = self.burning_projects[project_id].toc.tracks[track_index]
                track.cd_text[language_index].message = widget.get_text()
    def cb_tw_close_window (self,widget,window):
        window.get_window().destroy()

#===============================================================================
#        Main Window
#===============================================================================

    def cb_main_save_project (self,widget):
        if self.project_file_name == None:
            self.cb_main_save_as_project(widget)
        else:
            f = open (self.project_file_name,"w")
            config_serializer = ConfigSerializer()
            xml = config_serializer.serialize(self.burning_projects[self.current_project])
            f.write (xml)
            f.close()


    def cb_main_save_as_project (self,widget):
        chooser = gtk.FileChooserDialog(title="Save Project...",
                                        action=gtk.FILE_CHOOSER_ACTION_SAVE,
                                        buttons=(gtk.STOCK_CANCEL,
                                                 gtk.RESPONSE_CANCEL,
                                                 gtk.STOCK_SAVE,
                                                 gtk.RESPONSE_OK))

        chooser.set_current_name("project.bd")
        chooser.set_transient_for(self.gui_model.window)
        chooser.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        chooser.set_current_folder(os.environ.get("HOME"))

        response = chooser.run()

        if response == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            self.project_file_name = filename
            f = open (filename,"w")
            config_serializer = ConfigSerializer()
            xml = config_serializer.serialize(self.burning_projects[self.current_project])
            f.write (xml)
            f.close()

        chooser.destroy()
