import threading

from bd_exceptions.bubbledisk_exceptions import *
import gtk
import gobject
import time
from gui import gui_tools
from tool_box import Common_tools

class threaded_copy (threading.Thread):
    burning_project = None
    files = []
    window = None
    buffer = ""
    list_treeview = None
    drag_context = None
    model = None
    selected_files = []
    sys_tool = None
    gui_control = None
    source_treeview = None

    def __init__(self,gui_control,project,model,selected_files,list_treeview,drag_context,source_treeview,window = None):
        threading.Thread.__init__(self)
        self.burning_project = project
        self.sys_tool = Common_tools()
        self.window = window
        self.list_treeview = list_treeview
        self.drag_context = drag_context
        self.model = model
        self.selected_files = selected_files
        self.gui_control = gui_control
        self.source_treeview = source_treeview
    def run (self):
        print "thread run"
        for file in self.selected_files:
            #file = self.model.get_value(iter,2)
            if self.window is not None:
                if os.path.isdir(file):
                    self.window.set_numfiles(self.sys_tool.count_numfiles(file))
                else:
                    self.window.set_numfiles(1)
            self.burning_project.add_files([file],self.window)
            if self.window is not None:
                self.window.initialize()

        if self.window != None:
            gobject.idle_add(self.window.hide_window)

        gobject.idle_add(self.gui_control.npfs_drag_end,self.selected_files,self.list_treeview)
        #gobject.idle_add(self.list_treeview.emit,'drag-end',self.drag_context)

class Threaded_blanking (threading.Thread):
    blank_project = None
    window = None

    def __init__(self,blank_project,window):
        threading.Thread.__init__(self)
        self.blank_project = blank_project
        self.window = window

    def run (self):
        self.blank_project.write(self.window)
        gobject.idle_add(self.window.hide_window)

class Threaded_writing (threading.Thread):
    window = None
    burning_project = None

    def __init__(self,burn_project,window):
        threading.Thread.__init__(self)
        self.burning_project = burn_project
        self.window = window

    def run (self):
        self.burning_project.finalize(self.window)


class Threaded_copy_reading(threading.Thread):

    window = None
    burning_project = None
    dialog = None
    gui_control = None

    def __init__(self,burn_project,window,dialog,gui_control):
        threading.Thread.__init__(self)
        self.burning_project = burn_project
        self.window = window
        self.dialog = dialog
        self.gui_control = gui_control

    def run (self):
        self.burning_project.read_data_disk(self.window)
        # Ejects the readed disk
        self.burning_project.device_manager.eject_disk()
        gobject.idle_add (self.gui_control.after_reading_dialog,self.dialog)
        print "hello"

class Threaded_multisess_copy_reading(threading.Thread):

    window = None
    burning_project = None
    dialog = None
    gui_control = None

    def __init__(self,burn_project,window,dialog,gui_control):
        threading.Thread.__init__(self)
        self.burning_project = burn_project
        self.window = window
        self.dialog = dialog
        self.gui_control = gui_control

    def run (self):
        self.burning_project.read_multisess_data_disk(self.window)
        # Ejects the readed disk
        self.burning_project.device_manager.eject_disk()

        if self.window.is_aborted ():
            del self.window
            return

        gobject.idle_add (self.gui_control.after_reading_dialog,self.dialog)

class Threaded_copy_writing(threading.Thread):

    window = None
    burning_project = None

    def __init__(self,burn_project,window):
        threading.Thread.__init__(self)
        self.burning_project = burn_project
        self.window = window

    def run (self):
        self.burning_project.write_data_disk(self.window)
        print 'c fini!'

class Threaded_multisess_copy_writing(threading.Thread):

    window = None
    burning_project = None

    def __init__(self,burn_project,window):
        threading.Thread.__init__(self)
        self.burning_project = burn_project
        self.window = window

    def run (self):
        self.burning_project.write_multisess_data_disk(self.window)
        print 'c fini!'

class Threaded_import_session (threading.Thread):
    window = None
    burning_project = None
    gui_control = None

    def __init__(self,burn_project,gui_control,window):
        threading.Thread.__init__(self)
        self.burning_project = burn_project
        self.window = window
        self.gui_control = gui_control

    def run (self):
        self.burning_project.import_session(self.window)
        gobject.idle_add(self.gui_control.npfs_drag_end,["one elem"],None)
        del self.window

class Threaded_read_toc (threading.Thread):
    window = None
    cdrdao_tools = None
    tocs = None
    di_win = None

    def __init__(self,di_win,cdrdao_tools,window):
        threading.Thread.__init__(self)
        self.cdrdao_tools = cdrdao_tools
        self.window = window
        self.di_win = di_win

    def run (self):
        tocs = self.cdrdao_tools.read_tocs(self.window)
        self.di_win.tocs = tocs
        self.window.hide_window()
        del self.window
        self.di_win.insert_toc(tocs)
        gobject.idle_add(self.di_win.toc_treeview.set_sensitive,True)


