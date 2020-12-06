import gtk
import time

from gui.bubbledisk_gui_model import bubbledisk_gui_model
from gui.bubbledisk_gui_view import bubbledisk_gui_view
from gui.bubbledisk_gui_control import bubbledisk_gui_control

from backends.application_manager import application_manager
from backends.device_manager import bubble_device_manager
from backends.tool_box import Common_tools
from backends.tool_box import Cdrdao
from backends.tool_box import mkisofs
from backends.tool_box import cdrecord
from backends.config_manager import Config
from backends.bubblevfs import xmlfs
from backends.project_creation_tools import *
from backends.audio.AudioPlayer import *

from bd_exceptions.bubbledisk_exceptions import *

from constants.config import *


class application:

    cmdline_tools = None
    config_handler = None
    vfs = None
    burning_projects = []
    application_manager = None
    device_manager = None
    isofs_tool = None
    copy_cd_root_project = None
    cdrdao_tools = None
    root_projects = {}

    def execute (self):
        gtk.threads_init()

        self.cmdline_tools = Common_tools ()
        self.config_handler = Config(self.cmdline_tools)

        if self.config_handler.get ("misc/show_splashscreen"):
            window = gtk.Window (gtk.WINDOW_TOPLEVEL)
            image = gtk.Image ()
            image.set_from_file (THEMES_DIR+"/standard/bubbledis.svg")
            window.add (image)

            window.set_decorated(False)
            gtk.gdk.screen_width()
            window.move(gtk.gdk.screen_width()/2-200,gtk.gdk.screen_height()/2-200)
            window.show_all()
            window.realize()
            while gtk.events_pending():
                gtk.main_iteration()

        # Utilities Backends
        self.vfs = xmlfs(self.cmdline_tools,"bubbledisk")

        while gtk.events_pending():
                gtk.main_iteration()

        self.application_manager = application_manager(self.config_handler)

        while gtk.events_pending():
                gtk.main_iteration()

        self.audio_player = AudioPlayer()

        while gtk.events_pending():
                gtk.main_iteration()

        self.device_manager = bubble_device_manager (self.cmdline_tools,self.application_manager)

        while gtk.events_pending():
                gtk.main_iteration()

        self.cdrdao_tools = Cdrdao(self.cmdline_tools,self.application_manager,self.device_manager,self.config_handler)

        while gtk.events_pending():
                gtk.main_iteration()

        self.isofs_tool = mkisofs (self.application_manager)

        while gtk.events_pending():
                gtk.main_iteration()

        self.cdrecord_tool = cdrecord(self.application_manager,self.device_manager)

        while gtk.events_pending():
                gtk.main_iteration()

        self.readcd_tools = readcd (self.cmdline_tools,self.application_manager,self.device_manager,self.config_handler)

        # Init root projects
        # TODO: Adapat to all projects
        self.root_projects[COPY_CD_PROJECT] = Copy_cd_project (self.cmdline_tools,self.device_manager,self.application_manager,self.cdrdao_tools,self.config_handler,self.readcd_tools,self.cdrecord_tool)
        while gtk.events_pending():
                gtk.main_iteration()


        # Graphical User Interface
        gui_view = bubbledisk_gui_view(self.config_handler)

        while gtk.events_pending():
                gtk.main_iteration()
        gui_control = bubbledisk_gui_control(self.cmdline_tools,
                                            self.vfs,
                                            self.isofs_tool,
                                            self.cdrecord_tool,
                                            self.application_manager,
                                            self.device_manager,
                                            self.config_handler,
                                            self.cdrdao_tools,
                                            self.root_projects,
                                            self.audio_player)

        gui_model = bubbledisk_gui_model(gui_control,gui_view,self.application_manager,self.device_manager,self.config_handler,self.vfs)

        while gtk.events_pending():
                gtk.main_iteration()

        gui_view.set_model (gui_model)

        gui_control.set_view (gui_view)
        gui_control.set_model (gui_model)

        if self.config_handler.get ("misc/show_splashscreen"):
            window.destroy()

        gui_model.build_model()
        gui_view.set_initial_view()

        gtk.main()

#################### Main ####################
app = application()
app.execute()
