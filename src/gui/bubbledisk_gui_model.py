import gobject
import gtk
import gnome.vfs
import gnome.ui
import os
import constants.config

from gui.bubbledisk_explorers import my_little_nautilus, new_project_treeview, AudioTracksBox
from gui.projects_window import Projects_window
from gui.bubble_windows import *
from gui.gui_tools import bubbledisk_progressbar
from gui.properties_window import properties_window


from constants.config import *


# XML description of the menu
ui_info = \
"""
		<ui>
			<menubar name='MenuBar'>
				<menu name='FileMenu' action='FileMenu'>
					<menuitem action='New' />
					<menuitem action='Open' />
					<menuitem action='Save' />
					<menuitem action='SaveAs' />
					<separator />
					<menuitem action='CompilInfos' />
					<separator />
					<menuitem action='Quit' />
				</menu>
				<menu name='EditMenu' action='EditMenu'>
					<menuitem action='Copy' />
					<menuitem action='Cut' />
					<menuitem action='Paste' />
					<separator />
					<menuitem action='Prefs' />
				</menu>

				<menu name='ProjectMenu' action='ProjectMenu'>
					<menuitem action='CreateFolder' />
					<menuitem action='Delete' />
					<menuitem action='Properties' />
					<separator />
					<menuitem action='SelectAll' />
				</menu>

				<menu name='WindowMenu' action='WindowMenu'>
					<menuitem action='Refresh' />
					<separator />
					<menuitem name='VerticalView' action='VerticalView' />
					<menuitem name='HorizontalView' action='HorizontalView' />
					<separator />
					<menuitem name='FileSystemRight' action='FileSystemRight' />
					<menuitem name='FileSystemLeft' action='FileSystemLeft' />
					<separator />
					<menuitem action='ShowToolBar' />
				</menu>
				<menu name='RecorderMenu' action='RecorderMenu'>
					<menuitem action='ChooseRecorder' />
					<menuitem action='InfoCd' />
					<separator />
					<menuitem action='DeleteCDR' />
					<menuitem action='EjectCD' />
					<separator />
					<menuitem action='WriteCd' />
				</menu>


				<menu name='HelpMenu' action='HelpMenu'>
					<menuitem action='About' />
				</menu>
			</menubar>

			<menubar name='npfs_popup2'>
				<menu name='npfs_popup2_menu' action='npfs_popup2_menu'>
					<menuitem action='npfs_popup2_CreateFolder' />
					<separator />
					<menuitem action='npfs_popup2_SelectAll' />
				</menu>
			</menubar>

			<menubar name='audio_popup'>
				<menu name='audio_popup_menu' action='audio_popup_menu'>
					<menuitem action='audio_popup_Delete' />
				</menu>
			</menubar>

			<toolbar name='ToolBar'>

				<toolitem name='New' action='New' />
				<toolitem name='Open' action='Open' />
				<toolitem name='Save' action='Save' />
				<separator/>
				<toolitem name='ChooseRecorder' action='ChooseRecorder' />
				<toolitem name='InfoCd'  action='InfoCd' />
				<toolitem name='EjectCD' action='EjectCD' />
				<separator/>
				<toolitem name='CompilInfos' action='CompilInfos' />
				<separator />
				<toolitem name='WriteCd' action='WriteCd' />
			</toolbar>
		</ui>
"""

class bubbledisk_gui_model:
	HORIZONTAL = 1
	VERTICAL = 2
	LEFT = 1
	RIGHT = 2
	projects_window = None
	about_window = None
	proj_window = None
	explorer = None
	vfs = None

	ICONS_DIRECTORY = '/home/dsolimando/GPL/Python/bubbledisk/cd_icons'
	ICONS_DIRECTORY2 = '/home/dsolimando/GPL/Python/bubbledisk/icon'
	icons_url = [ICONS_DIRECTORY+"/gnome-dev-cdrw.png",
			 	 ICONS_DIRECTORY+"/cd_copy.png"]
	icons_comments = ["Erase a recordable disk","Copy a disk"]
	icons_ids = ["gnome-dev-cdrw","cd_copy"]
	icon_theme = gtk.icon_theme_get_for_screen(gtk.gdk.screen_get_default())

	gui_view = None
	gui_control = None

	# Widgets
	window = None
	mainBox = None
	vbox_menu = None
	vbox_toolbar = None
	vbox_hpaned = None
	vbox_progressbar = None
	hbox_graduationbar = None
	hbox_status = None
	uiManager = None
	toolBar = None
	menuBar = None
	progressbar = None
	action_group = None
	hpaned = None
	vpaned = None
	dirtree = None
	project_treeview_vbox = None
	bubble_progressbar = None

	copy_window = None
	properties_window = None
	edit_menu = None

	dev_manager = None
	app_manager = None

	config_handler = None

	def __init__(self,gui_control,gui_view,app_manager,dev_manager,config_handler,vfs):
		self.gui_control = gui_control
		self.gui_view = gui_view
		self.dev_manager = dev_manager
		self.app_manager = app_manager
		self.config_handler = config_handler
		self.vfs = vfs

	def build_model (self):
		screen_height = gtk.gdk.screen_height()
		screen_width = gtk.gdk.screen_width()

		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		#self.window.set_gravity(gtk.gdk.GRAVITY_SOUTH_EAST)
		self.window_height = self.config_handler.get ("view/window_height")
		self.window_width = self.config_handler.get ("view/window_width")
		self.window_position_x = self.config_handler.get ("view/window_position_x")
		self.window_position_y = self.config_handler.get ("view/window_position_y")
		self.window.set_size_request(800,600)
		self.window.move (self.window_position_x,self.window_position_y)
		self.window.set_default_size(self.window_width,self.window_height)
		self.window.set_icon_from_file(ICONS_DIR+"/bbd_win_icon.bmp")
		self.window.set_title("BubbledisK Burning Rom")
		self.window.connect("delete_event",self.gui_control.cb_exit_bubbledisk,self.config_handler)

		self.__register_bubbledisk_stock_icons()

		self.uiManager = gtk.UIManager()
		self.window.set_data("ui_manager",self.uiManager)
		self.uiManager.insert_action_group(self.__create_action_group(),0)
		self.window.add_accel_group (self.uiManager.get_accel_group())

		# program's windows
		self.copy_window = xmlfs_copy_window()
		self.copy_window.get_window().set_transient_for(self.window)

		#self.about_window_factory()
		self.mkdir_window = create_dir_win (self.gui_control)
		self.mkdir_window.get_window().set_transient_for(self.window)

		self.create_properties_window()

		try:
			managerId = self.uiManager.add_ui_from_string(ui_info)
		except gobject.GError, msg:
			print "building menus failed: %s" % msg

		self.burn_button = self.uiManager.get_widget('/ToolBar/WriteCd')
		self.burn_button.hide()

		self.edit_menu = self.uiManager.get_widget('/MenuBar/ProjectMenu')
		self.edit_menu2 = self.uiManager.get_widget('/npfs_popup2/npfs_popup2_menu')
		self.audio_menu = self.uiManager.get_widget('/audio_popup/audio_popup_menu')

		self.uiManager.get_widget ("/ToolBar/ChooseRecorder").set_icon_name("drive-cdrom")
		self.uiManager.get_widget ("/ToolBar/EjectCD").set_icon_name("media-eject")

		# Create the boxes containing the widgets
		self.boxes()

		# Create the menuBar of the application
		self.menuBar2()

		# Create the toolbar of the application
		self.toolBar2()

		# Create the directoryTree
		self.build_hpaned()
		self.bubbledisk_status_bar()

		self.new_project_window ()

		self.window.show()

	def set_view(self,gui_view):
		self.gui_view = gui_view

	def set_control (self,control):
		self.gui_control = control

	def file_selected(self,w):
		print "%s" % self.filesel.get_filename()

	def destroy(self,widget):
		gtk.mainquit()

	def file_selection(self,temp=""):
		self.filesel = gtk.FileSelection("Open File")
		self.filesel.connect("destroy",self.destroy)
		#self.filesel.ok_button.connect("clicked",self.file_selected)
		#self.filesel.cancel_button.connect("clicked",self.filesel.destroy())
		self.filesel.show()

	def toolBar2(self):
		toolBar = self.uiManager.get_widget("/ToolBar")
		#toolBar.show()
		self.vbox_toolbar.pack_start(toolBar,True,True,0)

	def create_project_window (self,action):
		icon_project = self.proj_window.get_current_project_selected()
		self.projects_window.show_all()
		self.window.set_sensitive(False)
		self.proj_window.hide_widgets_after_iso_creation("cd",icon_project)
		self.proj_window.modify_tabs (icon_project)

	def new_project_window (self):
		if self.projects_window == None:
			# Create the root project window (id=-1)
			self.proj_window = Projects_window (self.gui_control,self.gui_view,-1)
			self.projects_window = self.proj_window.get_window()
			self.projects_window.set_transient_for(self.window)
			self.projects_window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)

		self.projects_window.show_all()
		self.proj_window.modify_tabs("Data CD (iso9660)")
		self.proj_window.hide_widgets_before_iso_creation()
		#self.window.set_state(gtk.STATE_INSENSITIVE)
		self.projects_window.set_property('modal',True)

	def create_properties_window (self):
		#self.dev_manager.unmount_current_writer()
		self.properties_window = properties_window (self.gui_control,
													  self.gui_view,
													  self.dev_manager,
													  self.app_manager,
													  self.config_handler,
													  self.gui_control.toolbox)
		self.properties_window.window.set_transient_for(self.window)
		self.properties_window.window.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
		self.properties_window.window.set_property('modal',True)

	def about_window_factory (self,action):
		# must be config.DIRICONS
		image = gtk.gdk.pixbuf_new_from_file(THEMES_DIR+"/standard/bubbledisk_help.svg")
		self.about_window = gnome.ui.About (constants.config.APPNAME,
											constants.config.VERSION,
											constants.config.COPYRIGHT,
		 									""""%s\n\nBubbledisK is a CD Burnuer for the GNOME 2 desktop""" % constants.config.RELNAME,
		 									[constants.config.AUTHOR],
		 									None,
		 									"",
		 									image)
		self.about_window.set_transient_for (self.window)
		self.about_window.set_title ("About BubbledisK")
		self.about_window.show_all()



	def __create_action_group(self):
		# GtkActionEntry
		entries = (
			( "FileMenu", None, "_File" ),
			( "EditMenu", None, "_Edit" ),
			( "ViewMenu", None, "_View" ),
			( "ProjectMenu", None, "_Project" ),
			( "RecorderMenu", None, "_Recorder" ),
			( "WindowMenu", None, "_View" ),
			( "HelpMenu", None, "_Help" ),
			( "npfs_popup_menu", None, "_npfs_popup" ),
			( "npfs_popup2_menu", None, "_npfs_popup2" ),
			( "audio_popup_menu", None, "_audio_popup" ),
			( "New", gtk.STOCK_NEW,
			  "_New", "<Control>N",
			  "Create a new Burning Project",
			  self.gui_control.cb_show_main_projects_window ),
			( "Open", gtk.STOCK_OPEN,
			  "_Open", "<Control>O",
			  "Open an existing Burning Project",
			  self.activate_action ),
			( "Save", gtk.STOCK_SAVE,
			  "_Save", "<Control>S",
			  "Save the Burning Project",
			   	  self.gui_control.cb_main_save_project ),
			( "SaveAs", gtk.STOCK_SAVE_AS,
			  "_Save as...", None,
			  "Save the compilation into a new file",
			  self.gui_control.cb_main_save_as_project ),
			( "Copy", gtk.STOCK_COPY,
			  "_Copy", "<Control>C",
			  "Copy file(s)",
			  self.activate_action ),
			( "Cut", gtk.STOCK_CUT,
			  "_Cut", "<Control>X",
			  "Cut File(s)",
			  self.activate_action ),
			( "Paste", gtk.STOCK_PASTE,
			  "_Paste...", None,
			  "Paste file(s)",
			  self.activate_action ),
			( "CompilInfos", gtk.STOCK_DIALOG_INFO,
			  "_Project Infos", "<Control>I",
			  "Get information about",
			  self.gui_control.cb_show_projects_window ),
			( "Refresh", gtk.STOCK_REFRESH,
			  "_Refresh", "<Control>R",
			  "Show the actual content of the current directory",
		 	  self.gui_control.cb_refresh_explorer),
			( "WriteCd", gtk.STOCK_CDROM,
			  "_Write CD...", "<Control>W",
			  "Write the compilation on cd",
			  self.gui_control.cb_finalize_compilation ),
			( "Burn", gtk.STOCK_EXECUTE,
			  "_Burn Image...", "<Control>b",
			  "Burn the compilation",
			  self.activate_action ),
			( "BurnBack", gtk.STOCK_HARDDISK,
			  "_Burn HD Backup...", None,
			  "Burn Hard Drive Backup",
			  self.activate_action ),
			( "Prefs", gtk.STOCK_PREFERENCES,
			  "_Preferences", "<Control>P",
			  "Modify Preferences",
			  self.gui_control.cb_show_properties_window ),
			( "Quit", gtk.STOCK_QUIT,
			  "_Quit", "<Control>Q",
			  "Quit GNUro Burning Rom",
			  self.activate_action ),
			( "Delete", gtk.STOCK_DELETE,
			  "_Delete", "<Control>D",
			  "Delete",
		 	  self.gui_control.cb_npfs_delete_files),
			( "SelectAll", None,
			  "_Select All", "<Control>A",
			  "Select all files",
			  self.activate_action ),
			( "Properties", gtk.STOCK_PROPERTIES,
			  "_Properties", None,
			  "Properties",
			  self.activate_action),
			( "CreateFolder", gtk.STOCK_DIRECTORY,
			  "_Create Folder", None,
			  "Create a new folder",
			  self.gui_control.cb_npfs_create_folder ),
			( "Find", gtk.STOCK_FIND,
			  "_Find", "<Control>F",
			  "Find",
			  self.activate_action ),
			( "ChooseRecorder",None,
			  "_Choose Recorder", None,
			  "Choose Recorder",
			  self.gui_control.cb_cw_window ),
			( "InfoCd", gtk.STOCK_DIALOG_QUESTION,
			  "_Disk informations", None,
			  "Infomations about cd",
			  self.gui_control.cb_show_di_window ),
			( "DeleteCDR", gtk.STOCK_CLEAR ,
			  "_Erase Disk", None,
			  "Erase Disk",
			  self.gui_control.cb_show_blankdisk_window),
			( "EjectCD", None,
			  "_Eject Disk", "<Control>E",
			  "Eject the CD",
			  self.gui_control.cb_eject_disk ),
			( "About",gtk.STOCK_ABOUT,
			  "_About bubbledisk", None,
			  "About this program",
			  self.about_window_factory),
			( "npfs_popup_AddFile",gtk.STOCK_ABOUT,
			  "_Add File", None,
			  "Add a new file",
			  self.activate_action),
			( "npfs_popup_CreateFolder",gtk.STOCK_DIRECTORY,
			  "_Create Folder", None,
			  "Create a new folder",
			  self.gui_control.cb_npfs_create_folder ),
			( "npfs_popup_Delete", gtk.STOCK_DELETE,
			  "_Delete", "<Control>D",
			  "Delete",
		 	  self.gui_control.cb_npfs_delete_files),
			( "npfs_popup_Properties", gtk.STOCK_PROPERTIES,
			  "_Properties", None,
			  "Properties",
			  self.activate_action),
			( "npfs_popup_SelectAll", None,
			  "_Select All", "<Control>A",
			  "Select all files",
			  self.activate_action ),
			( "npfs_popup2_AddFile",gtk.STOCK_ABOUT,
			  "_Add File", None,
			  "Add a new file",
			  self.activate_action),
			( "npfs_popup2_CreateFolder",gtk.STOCK_DIRECTORY,
			  "_Create Folder", None,
			  "Create a new folder",
			  self.gui_control.cb_npfs_create_folder ),
			( "npfs_popup2_SelectAll", None,
			  "_Select All", "<Control>A",
			  "Select all files",
			  self.activate_action),
			( "audio_popup_Delete", None,
			  "_Delete", "<Control>D",
			  "Delete track from playlist",
			  self.gui_control.cb_ab_delete_song)
			)

		sense_entries = (
 		 ( "VerticalView", None,
 		   "_Vertical View", "<alt><control>v",
 		   "Use drag and drop vertically", self.VERTICAL),

 		 ( "HorizontalView", None,
 		   "_Horizontal View", "<alt><control>h",
 		   "Use drag and drop horizontally", self.HORIZONTAL )

 		   )

		fs_place_entries = (
			( "FileSystemRight",None,
			  "_Show File System in right (bottom) side","<alt><control>r",
			  "Show File System in right side", self.RIGHT),
			( "FileSystemLeft", None,
			  "_Show File System in left (top) side", "<alt><control>l",
			  "Show File System in left side", self.LEFT )
		)

		action_group = gtk.ActionGroup("AppWindowActions")
		action_group.add_actions(entries)

		sense = self.config_handler.get ("view/explorer_sense")
		if sense == "right":
			sense_as_int = self.RIGHT
		else:
			sense_as_int = self.LEFT

		view = self.config_handler.get ("view/explorer_view")
		if view == "vertical":
			view_as_int = self.VERTICAL
		else:
			view_as_int = self.HORIZONTAL

		action_group.add_radio_actions(sense_entries, view_as_int, self.gui_control.cb_change_sense,self.config_handler)
		action_group.add_radio_actions(fs_place_entries, sense_as_int , self.gui_control.cb_change_fs_place,self.config_handler)
		return action_group

	def activate_action(self, action):
		dialog = gtk.MessageDialog(self,
										 gtk.DIALOG_DESTROY_WITH_PARENT,
										 gtk.MESSAGE_INFO, gtk.BUTTONS_CLOSE,
									 	 'You activated action: "%s" of type "%s"' % (action.get_name(),
										 type(action)))
		# Close dialog on user response
		dialog.connect ("response", lambda d, r: d.destroy())
		dialog.show()

	def boxes(self):
		# Create the 4 toolboxes
		self.mainBox = gtk.VBox(False,0)
		self.vbox_menu = gtk.HBox(False,0)
		self.vbox_toolbar = gtk.HBox(False,0)
		self.vbox_hpaned = gtk.VBox(False,0)

		self.progressbar_hbox = gtk.HBox(False,0)

		self.hbox_status = gtk.HBox(False,0)

		self.mainBox.pack_start(self.vbox_menu,False,True)
		self.mainBox.pack_start(self.vbox_toolbar,False,True)
		self.mainBox.pack_start(self.vbox_hpaned,True,True)
		self.mainBox.pack_start(gtk.HSeparator(),False,True)
		self.mainBox.pack_start(self.progressbar_hbox,False,True)

		self.mainBox.pack_start(self.hbox_status,False,True,2)
		self.window.add(self.mainBox)


	def menuBar2(self):
		menuBar = self.uiManager.get_widget("/MenuBar")
		self.vbox_menu.pack_start(menuBar,True,True,0)

	def build_audio_project_widgets (self):
		self.audio_tracks_box = AudioTracksBox (self.gui_control)
		self.projectvbox.pack_start(self.audio_tracks_box.main_box,True,True)
		self.projectvbox.show_all()

	def build_project_treeview (self,burn_project):
		self.project_treeview = new_project_treeview (self.vfs,burn_project,self.gui_view,self.gui_control)
		self.project_treeview_vbox = self.project_treeview.get_project_treeview_vbox()
		self.projectvbox.pack_start(self.project_treeview_vbox,True,True)
		self.projectvbox.show_all()

	def build_hpaned(self):
		# Create the Hpaned containing the file drag and drop mecanism to create compilations
		self.hpaned = gtk.HPaned()
		self.vpaned = gtk.VPaned()

		self.explorer =  my_little_nautilus(self.window,self.gui_control,self.gui_view)
		self.dirtree = self.explorer.getHpaned()

		self.projectvbox = gtk.VBox (True,0)

		view = self.config_handler.get("view/explorer_view")
		sense = self.config_handler.get("view/explorer_sense")

		if view == "horizontal":
			if sense == "right":
				print "right"
				self.vpaned.add1(self.projectvbox)
				self.vpaned.add2(self.dirtree)
			else:
				print "left"
				self.vpaned.add1(self.dirtree)
				self.vpaned.add2(self.projectvbox)
			self.gui_view.paned_position = int(self.window_height/2-100)
			self.vpaned.set_position(int(self.window_height/2-100))
			self.gui_view.current_paned = self.vpaned

		else:
			print "vertical"
			if sense == "right":
				print "right"
				self.hpaned.add1(self.projectvbox)
				self.hpaned.add2(self.dirtree)
			else:
				print "left"
				self.hpaned.add1(self.dirtree)
				self.hpaned.add2(self.projectvbox)
			self.gui_view.paned_position = int(self.window_width/2)
			self.hpaned.set_position(int(self.window_width/2))
			self.gui_view.current_paned = self.hpaned

		self.vbox_hpaned.pack_start(self.vpaned,True,True)
		self.vbox_hpaned.pack_start(self.hpaned,True,True)

	def bubbledisk_progressbar(self):
		# Progress Bar
		self.progressbar = gtk.ProgressBar(adjustment=None)
		self.progressbar.set_fraction(0.0)
		self.progressbar.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)
		self.progressbar.set_text("0 Mo")

		mycolor = gtk.gdk.Color(red=0, green=0, blue=0, pixel=0)
		style = self.progressbar.get_style().copy ()
		color = self.progressbar.get_colormap().alloc (mycolor)
		for i in range (5):
			style.bg[i] = color
			style.fg[i] = color
			style.base[i] = color
		self.progressbar.set_style (style)

		self.red_progressbar = gtk.ProgressBar(adjustment=None)
		self.progressbar.set_fraction(0.0)
		self.progressbar.set_orientation(gtk.PROGRESS_LEFT_TO_RIGHT)

		# Graduation Bar
		for i in range(0,8):
			if (i <> 0):
				text = '|' + str(i) + '00'
			else:
				text = '|' + str(i)
			label = gtk.Label(text)
			#label.show()
			hbox = gtk.HBox(False,0)
			hbox.pack_start(label,False,True)
			#hbox.show()
			self.hbox_graduationbar.pack_start(hbox,True,True)

		self.hbox_graduationbar.set_border_width(0)
		self.hbox_graduationbar.set_size_request(-1,16)
		self.progressbar.set_size_request(-1,20)
		self.vbox_progressbar.pack_start(self.progressbar,False,False,3)

	def bubbledisk_status_bar (self):
		self.version_status = gtk.Statusbar()
		self.version_status.set_has_resize_grip (True)
		self.version_status.push (1,"bubbledisk 0.01")
		self.version_status.set_size_request(150,-1)

		self.free_disk_status = gtk.Statusbar()
		self.free_disk_status.set_has_resize_grip (False)
		self.free_disk_status.push (2,"27 MB/600 MB (5%)")
		self.free_disk_status.set_size_request(150,-1)

		self.oversized_status = gtk.Statusbar()
		self.oversized_status.set_has_resize_grip (False)

		self.oversized_status.push (3,"oversize!!")
		self.oversized_status.set_size_request(100,-1)

		self.various_status = gtk.Statusbar()
		self.various_status.set_has_resize_grip (False)
		self.various_status.push (4,"Use Drag and Drop to add files to your compilation")

		#self.hbox_status.set_border_width(2)
		self.hbox_status.pack_start(self.various_status,True,True)
		self.hbox_status.pack_start(self.oversized_status,False,False)
		self.hbox_status.pack_start(self.free_disk_status,False,False)
		self.hbox_status.pack_start(self.version_status,False,False)


	def menuItem_response(self,widget,string):
		print "%s" % string

	def __register_bubbledisk_stock_icons(self):
	    ''' This function registers our custom toolbar icons, so they
	        can be themed.
	    '''
	    items = []
	    for i in range(len(self.icons_url)):
	    	items.append((self.icons_ids[i], self.icons_comments[i], 0, 0, ''))

	    # Register our stock items
	    gtk.stock_add(items)

	    # Add our custom icon factory to the list of defaults
	    factory = gtk.IconFactory()
	    factory.add_default()
	    i = 0

	    try:
	    	for icon_url in self.icons_url:
	    		pixbuf = gtk.gdk.pixbuf_new_from_file(os.getcwd() + os.sep + icon_url)
	    		transparent = pixbuf.add_alpha(True, chr(255), chr(255),chr(255))
	    		icon_set = gtk.IconSet(transparent)
	    		factory.add(self.icons_ids[i], icon_set)
	    		i = i+1

	    except gobject.GError, error:
	        print 'failed to load logo for toolbar'

