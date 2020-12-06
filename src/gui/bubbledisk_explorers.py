import gtk
import pygtk
import gobject
import os, stat, time
import os.path
import dircache
import gnomevfs
import shutil

from re import compile,match

from backends.tool_box import Common_tools
from constants.config import *

class my_little_nautilus:

	HOME_DIR = os.environ['HOME']
	icon_theme = gtk.icon_theme_get_for_screen(gtk.gdk.screen_get_default())

	hpaned = None
	scrolled_window_left = None
	scrolled_window_right = None

	fs_list_treeview = None
	liststore = None
	treeview = None
	treestore = None

	gui_control = None
	gui_view = None

	def __init__(self,window,gui_control,gui_view):
		self.gui_control = gui_control
		self.gui_view = gui_view
		self.pair = 0
		self.weight = 400
		self.window = window
		self.ScrolledWindow()
		self.HPanedBox()
		self.folders_treeview()
		self.folder_list_treeview()

	def file_name(self,column,cell,model, iter):
		cell.set_property('text',model.get_value(iter,0))
		return

	def file_size(self,column,cell,model,iter):
		cell.set_property('text',model.get_value(iter,3))
		return

	def file_mode(self, column, cell, model, iter):
		cell.set_property('text', model.get_value(iter,4))
		return

	def file_last_changed(self,column,cell,model,iter):
		filename = model.get_value(iter,2)

		try:
			filestat = os.stat(filename)
			cell.set_property('text', time.ctime(filestat.st_mtime))
		except OSError, error:
			cell.set_property('text','no permission to show this information')
		return

#	def pixbuf_type(self,column,cell,model,iter):
#		filename = model.get_value(iter,2)
#
#		no_file = not os.path.isdir(filename)
#		no_dir = not os.path.isfile(filename)
#		no_abs = not os.path.isabs(filename)
#		no_link = not os.path.islink (filename)
#		no_mount = not os.path.ismount (filename)
#
#		if no_file and no_dir  and no_link and no_mount:
#			small_icon = dirIcon = self.icon_theme.load_icon("emblem-important",
#												24,
#												gtk.ICON_LOOKUP_FORCE_SVG)
#		elif os.path.isdir(filename):
#			small_icon = dirIcon = self.icon_theme.load_icon("gnome-fs-directory",
#												24,
#												gtk.ICON_LOOKUP_FORCE_SVG)
#		else:
#			exten = split(filename,'.')
#			small_icon = get_icon (exten[-1],self.icon_theme)
#
#		cell.set_property('pixbuf', small_icon)
#
#	def change_tree_icon (self,column,cell,model,iter):
#		if model.get_value(iter,0) == 'Home':
#			small_icon = self.icon_theme.load_icon("gnome-fs-home",
#												24,
#												gtk.ICON_LOOKUP_FORCE_SVG)
#		elif model.get_value(iter,0) == 'File System':
#			small_icon = self.icon_theme.load_icon("gnome-dev-harddisk",
#												24,
#												gtk.ICON_LOOKUP_FORCE_SVG)
#		else:
#			small_icon = self.icon_theme.load_icon("gnome-fs-directory",
#													24,
#													gtk.ICON_LOOKUP_FORCE_SVG)
#		cell.set_property('pixbuf', small_icon)


	def folder_list_treeview(self):
		self.column_names = ['Name','Size','Mode','Last Changed']

		# Create the liststore
		self.liststore = self.directory_liststore_factory(self.HOME_DIR)

		# Create the treeview of the list
		self.fs_list_treeview = gtk.TreeView()
		self.fs_list_treeview.set_rules_hint(True)
		self.fs_list_treeview.connect("button-press-event",self.gui_control.cb_fs_button_pressed)
		#self.fs_list_treeview.connect ("drag-end", self.gui_control.npfs_drag_end)

		self.list_treeview_selection = self.fs_list_treeview.get_selection()
		self.list_treeview_selection.set_mode(gtk.SELECTION_MULTIPLE)

		# create the TreeViewColumn containing the cellRederers
		tvcolumn = [None] * len(self.column_names)
		tvcolumn[0] = gtk.TreeViewColumn(self.column_names[0])

		# Create the pixmap Renderer
		cellpb = gtk.CellRendererPixbuf()
		tvcolumn[0].pack_start(cellpb,False)
		tvcolumn[0].set_cell_data_func(cellpb, self.gui_control.cb_fs_pixbuf_type)

		# Create the text Renderer
		cell = gtk.CellRendererText()
		tvcolumn[0].pack_start(cell,False)
		tvcolumn[0].set_cell_data_func(cell, self.file_name)
		tvcolumn[0].set_resizable(True)

		# Add the column to the fs_list_treeview
		self.fs_list_treeview.append_column(tvcolumn[0])

		for n in range(1, len(self.column_names)):
			cell = gtk.CellRendererText()
			tvcolumn[n] = gtk.TreeViewColumn(self.column_names[n], cell)
			#if n==1:
			#	cell.set_property('xalign',1.0)

			if n==1:
				tvcolumn[n].set_cell_data_func(cell, self.file_size)
			elif n==2:
				tvcolumn[n].set_cell_data_func(cell, self.file_mode)
			elif n==3:
				tvcolumn[n].set_cell_data_func(cell, self.file_last_changed)

			tvcolumn[n].set_resizable(True)
			# Add the column to the fs_list_treeview
			self.fs_list_treeview.append_column(tvcolumn[n])

		# Bind the model (the liststore) to the fs_list_treeview
		self.fs_list_treeview.set_model(self.liststore)

		# Connect the a directory selection event to the fonction that fill the fileList
		self.fs_list_treeview.connect('row-activated',self.gui_control.cb_fs_liststore_explore)

		# Add the treeView to the scrolled Window
		self.scrolled_window_right.add_with_viewport(self.fs_list_treeview)


		# Show all widgets in the window
		self.window.show_all()

	def directory_liststore_factory(self,directory):
		listmodel = gtk.ListStore(str,int,str,str,str)
		try:
			files = [f for f in os.listdir(directory) if f[0] <> '.']
			files.sort()
			if directory != self.HOME_DIR and directory != '/' :
				files = ['..'] + files

			# Add each file in the listsore
			i = 0
			for f in files:
				filename = os.path.join(directory,f)
				filestat = os.stat(filename)
				if os.path.isdir(filename):
					listmodel.append([f,i,filename,filestat.st_size,oct(stat.S_IMODE(filestat.st_mode))])
					i = i +1
			for f in files:
				filename = os.path.join(directory,f)
				filestat = os.stat(filename)
				if not os.path.isdir(os.path.join(directory,f)):
					listmodel.append([f,i,filename,filestat.st_size,oct(stat.S_IMODE(filestat.st_mode))])
					i = i + 1
			i=0
		except OSError,error:
			listmodel.append(["you don't have permissions to explore this directory",0,"","",""])
		except gnomevfs.AccessDeniedError,error:
			listmodel.append(["you don't have permissions to explore this directory",0,"","",""])

		return listmodel


#	def fill_tree(self,iter,root_dir):
#		dirs = dircache.listdir(root_dir)
#		if len(dirs) == 0:
#			return
#		else :
#			iter_parent=iter
#			for dir in dirs:
#				if os.path.isdir(root_dir+"/"+dir) & (not dir.startswith(".")):
#					iter = self.treestore.append(iter_parent,[dir , os.path.join(root_dir,dir)])
#					self.fill_tree(iter,root_dir+"/"+dir)
#			return

	def prepopulate_tree (self):
		# Add the home directory
		self.gui_view.current_fs_dir_browsed = self.HOME_DIR
		home_iter = self.treestore.append (None,["Home",self.HOME_DIR])
		dirs = gnomevfs.open_directory(self.HOME_DIR)
		for dir in dirs:
			if (dir.name.find(".") != 0 and dir.type == 2):
				self.treestore.append(home_iter,[dir.name , os.path.join(self.HOME_DIR,dir.name)])

		filesys_iter = self.treestore.append (None,["File System","/"])
		for dir in gnomevfs.open_directory("/"):
			if (dir.name.find(".") != 0 and dir.type == 2):
				self.treestore.append(filesys_iter,[dir.name , os.path.join("/",dir.name)])

	def folders_treeview(self):
		# Tree creation
		self.treestore = gtk.TreeStore(str,str)

#		iter = self.fill_tree(None,self.HOME_DIR)
		self.prepopulate_tree ()
		# Create the treeView
		self.treeview = gtk.TreeView(self.treestore)

		# Create a CellRendererPixbuf to render pixbuf
		self.cellPixbuf = gtk.CellRendererPixbuf()

		# Create the treeviewcolumn to display the data
		self.tvcolumn = gtk.TreeViewColumn("Poste de travail")

		self.tvcolumn.pack_start(self.cellPixbuf,False)

		# Retrieve the icons stock list
		small_icon = dirIcon = self.icon_theme.load_icon("gnome-fs-directory",
												24,
												gtk.ICON_LOOKUP_FORCE_SVG)
		self.cellPixbuf.set_property('pixbuf', small_icon)


		# Create a CellRendertext to render the data
		self.cell = gtk.CellRendererText()

		# Add the cell to the tccolumn and allow it to expand
		self.tvcolumn.pack_start(self.cell,True)

		self.tvcolumn.add_attribute(self.cell,'text',0)

		# connect to a fonction that change the icons
		self.tvcolumn.set_cell_data_func(self.cellPixbuf, self.gui_control.cb_fs_change_tree_icon)

		# Add the tvcolumn to the treeView
		self.treeview.append_column(self.tvcolumn)

		self.treeview.set_search_column(0)

		# Connect the a directory selection event to the fonction that fill the fileList
		self.treeview.connect('cursor-changed',self.gui_control.cb_fs_tree_cursor_changed)
		self.treeview.connect('row-expanded',self.gui_control.cb_fs_gen_subdir)

		# Add the treeView to the scrolled Window
		self.scrolled_window_left.add_with_viewport(self.treeview)



	def ScrolledWindow(self):
		self.scrolled_window_left = gtk.ScrolledWindow()
		self.scrolled_window_left.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
		self.scrolled_window_right = gtk.ScrolledWindow()
		self.scrolled_window_right.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)

	def HPanedBox(self):
		self.hpaned = gtk.HPaned()
		self.hpaned.add1(self.scrolled_window_left)
		self.hpaned.add2(self.scrolled_window_right)
		self.hpaned.set_position(int(self.weight/2))

	def getHpaned(self):
		return self.hpaned

class new_project_treeview:

	PROJECT_NAME = "New Project"
	WEIGHT = 400
	PROJECT_DIR = "/tmp/pyroman"
	icon_theme = gtk.icon_theme_get_for_screen(gtk.gdk.screen_get_default())
	system_tools = Common_tools()
	moving_cell_path = None

	burning_project = None
	vfs = None
	# Widgets
	vbox = None
	current_liststore = None
	list_cell_text = None
	list_treeview = None
	list_treemodel = None
	list_treeviewcolumn = tvcolumn = [None] * 4
	list_treeview_selection = None

	treestore = None
	treeview = None
	tvcolumn = None
	root_iter = None

	scrolled_window_left = None
	scrolled_window_right = None

	hpaned = None
	for_copy_window = None

	# Drop objects
	selected_iters = []

	#####################
	gui_view = None
	gui_control = None

	def __init__(self,vfs,burning_project,gui_view,control):
		self.vfs = vfs
		self.gui_view = gui_view
		self.gui_control = control
		self.burning_project = burning_project
		self.scrolled_window()
		self.hpaned_box ()
		self.list_treeview()
		self.treeview()
		self.vbox.pack_start (self.hpaned,True,True)

		self.gui_view.current_treeiter = self.root_iter


	def list_treeview (self):
		self.vbox = gtk.VBox(True,0)
		self.list_treeview = gtk.TreeView()
		self.list_treeview.set_rules_hint(True)

		self.list_treeview_selection = self.list_treeview.get_selection()
		self.list_treeview_selection.set_mode(gtk.SELECTION_MULTIPLE)

		self.list_treeview.enable_model_drag_dest ([("text/plain",0,0)],
												   gtk.gdk.ACTION_DEFAULT)

		self.list_treeview.connect ("row-activated",self.gui_control.cb_npfs_liststrore_explore_subdir)
		self.list_treeview.connect ("drag-drop", self.gui_control.cb_npfs_drag_drop)
		#self.list_treeview.connect ("drag-end", self.gui_control.npfs_drag_end)
		self.list_treeview.connect ("button-press-event", self.gui_control.cb_npfs_button_pressed)
		#self.list_treeview.connect ("drag-drop",self.gui_control.cb_npfs_drag_drop_in_treeview)


		self.list_treeviewcolumn[0] = gtk.TreeViewColumn("Project")

		cellpb = gtk.CellRendererPixbuf()
		self.list_treeviewcolumn[0].pack_start(cellpb,False)
		self.list_treeviewcolumn[0].set_cell_data_func(cellpb, self.gui_control.cb_npfs_change_list_icon)

		# Create the text Renderer
		self.list_cell_text = gtk.CellRendererText()
		self.list_treeviewcolumn[0].pack_start(self.list_cell_text,False)
		self.list_treeviewcolumn[0].set_cell_data_func(self.list_cell_text, self.gui_control.cb_npfs_change_filename)
		self.list_treeviewcolumn[0].set_resizable(True)

		# Add the column to the fs_list_treeview
		self.list_treeview.append_column(self.list_treeviewcolumn[0])

		column_names = ['URL','Size','Mode']
		for n in range(len(column_names)):
			cell = gtk.CellRendererText()
			self.list_treeviewcolumn[n] = gtk.TreeViewColumn(column_names[n], cell)

			if n == 0:
				self.list_treeviewcolumn[n].set_cell_data_func(cell, self.gui_control.cb_npfs_change_url)
			elif n == 1:
				self.list_treeviewcolumn[n].set_cell_data_func(cell, self.gui_control.cb_npfs_change_size)
			elif n == 2:
				self.list_treeviewcolumn[n].set_cell_data_func(cell, self.gui_control.cb_npfs_change_mode)

			self.list_treeviewcolumn[n].set_resizable(True)
			# Add the column to the fs_list_treeview
			self.list_treeview.append_column(self.list_treeviewcolumn[n])

		self.current_liststore = self.directory_liststore_factory (self.burning_project.get_base_dir())

		self.list_treeview.set_model(self.current_liststore)

		self.scrolled_window_right.add_with_viewport(self.list_treeview)

	def treeview (self):
		# Tree creation
		self.treestore = gtk.TreeStore(str,str)
		self.prepopulate_tree ()

		self.treeview = gtk.TreeView(self.treestore)
		self.treeview.enable_model_drag_source (gtk.gdk.BUTTON1_MASK,[("COMP_TREE",0,0)],gtk.gdk.ACTION_DEFAULT | gtk.gdk.ACTION_MOVE)
		self.treeview.enable_model_drag_dest ([("COMP_TREE",0,0),("LIST2TREE",0,0),("text/plain",0,0)],gtk.gdk.ACTION_DEFAULT)
		self.treeview.connect ('drag_data_get',self.gui_control.cb_npfs_drag_data_get)
		self.treeview.connect ('drag_data_received',self.gui_control.cb_npfs_drag_data_received)
		self.treeview.connect ("drag-drop",self.gui_control.cb_npfs_drag_drop_in_treeview)

		cell_pixbuf = gtk.CellRendererPixbuf()

		self.tvcolumn = gtk.TreeViewColumn("New Project")
		self.tvcolumn.pack_start(cell_pixbuf,False)

		small_icon = self.icon_theme.load_icon("gnome-dev-cdrom",
												24,
												gtk.ICON_LOOKUP_FORCE_SVG)

		cell_pixbuf.set_property('pixbuf', small_icon)

		cell_text = gtk.CellRendererText()


		self.tvcolumn.pack_start(cell_text,True)
		self.tvcolumn.add_attribute(cell_text,'text',0)

		# connect to a fonction that change the icons
		self.tvcolumn.set_cell_data_func(cell_pixbuf, self.gui_control.cb_npfs_change_tree_icon)


		self.treeview.append_column(self.tvcolumn)
		self.treeview.set_search_column(0)

		# Connect the a directory selection event to the fonction that fill the fileList
		self.treeview.connect('cursor-changed',self.gui_control.cb_npfs_cursor_changed)
		self.treeview.connect('row-expanded',self.gui_control.cb_npfs_row_expended)

		# Add the treeView to the scrolled Window
		self.scrolled_window_left.add_with_viewport(self.treeview)

	def prepopulate_tree (self):
		self.root_iter = self.treestore.append (None,[self.PROJECT_NAME,self.burning_project.get_base_dir()])
		self.gui_view.current_treeiter = self.root_iter
		for dir in self.vfs.ls(self.burning_project.get_base_dir()):
			if (dir.find(".") != 0 and self.vfs.get_file_type(self.burning_project.get_base_dir()+"/"+dir) == "directory"):
				self.treestore.append(self.root_iter,[dir , os.path.join(self.burning_project.get_base_dir(),dir)])

	def scrolled_window(self):
		self.scrolled_window_left = gtk.ScrolledWindow()
		self.scrolled_window_left.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
		self.scrolled_window_right = gtk.ScrolledWindow()
		self.scrolled_window_right.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)

	def hpaned_box(self):
		self.hpaned = gtk.HPaned()
		self.hpaned.add1(self.scrolled_window_left)
		self.hpaned.add2(self.scrolled_window_right)
		self.hpaned.set_position(int(self.WEIGHT/2))

	def get_project_treeview_vbox (self):
		return self.vbox

	def is_treeview_empty (self,treeview):
		column = treeview.get_column(0)
		cell_renderers = column.get_cell_renderers()
		return len(cell_renderers) == 0

	def temp_liststore_factory (self):
		listmodel = gtk.ListStore(str,str,str,str,str,str)
		listmodel.append(["importing files ...","","","","","0"])
		return listmodel

	def directory_liststore_factory (self,directory):
		#files = [f for f in os.listdir(directory) if f[0] != '.']

		files = [f for f in self.vfs.ls(directory) if f[0] != '.' and f[0] != '..']
		if len(files) == 0:
			return

		files.sort()
		#print self.dirname
#		if directory != self.burning_project.get_base_dir() and directory != '/' :
#			files = ['..'] + files

		listmodel = gtk.ListStore(str,str,str,str,str,str)

		# Add each file in the listsore
		for f in files:
			url = os.path.join(directory,f)
			try:
				infos = self.burning_project.get_file_infos (url)
			except IndexError:
				infos = ["","","directory","","","0"]
			if infos[2] == "directory":
				listmodel.append([f,
								  url,
								  infos[3],
								  infos[0],
								  infos[1],
								  infos[4]])

		for f in files:
			url = os.path.join(directory,f)
			try:
				infos = self.burning_project.get_file_infos (url)
			except IndexError:
				infos = ["","","file","","","0"]
			if infos[2] == "file":
				listmodel.append ([f,
								  url,
								  infos[3],
								  infos[0],
								  infos[1],
								  infos[4]])

		return listmodel

	def remove_child_iters (self,model,iter):
		child_iter = model.iter_children (iter)
		if child_iter == None:
			return
		removing = True
		while removing:
			removing = model.remove (child_iter)


	def populate_treestore_iter_with_files (self,model,iter):
		self.remove_child_iters (model,iter)
		dirname = model.get_value(iter,1)

		# Adds file nodes to xml tree if needed
		self.vfs.explore_dir2 (dirname)

		for dir in self.vfs.ls(dirname):
			if (dir.find(".") != 0 and self.vfs.get_file_type(dirname+"/"+dir) == "directory"):
				#print "arbre: "+dir+" "+dirname
				self.treestore.append(iter,[dir, os.path.join(dirname,dir)])

	def get_current_iter_children (self,model,iter,dir):
		child_iter = model.iter_children (iter)
		while child_iter != None:
			if model.get_value(child_iter,0) == dir:

				return child_iter
			child_iter = model.iter_next(child_iter)
		return None


class AudioTracksBox:
	"""
	Backends
	"""
	gui_control = None

	"""
	Widgets
	"""
	tracks_liststore = None
	scrolled_window = None
	main_box = None
	tracks_treeview = None

	play = None
	pause = None

	artist_name = None
	artist_title = None
	artist_genre = None
	artist_album = None
	artist_length = None

	UPDATE_INTERVAL = 1000

	def __init__ (self,gui_control):

		self.gui_control = gui_control
		self.main_box = gtk.VBox (False,0)
		self.main_box.pack_start (self.controls_box(),False,False)
		self.main_box.pack_start (self.tracks_box(),True,True)
		self.main_box.pack_start (self.song_details_box(),False,False)

		self.UPDATE_INTERVAL = 500


	def controls_box (self):
		"""
		List of buttons that allow playing and navigating into track list
		"""
		hbox = gtk.HBox (False,10)
		hbox.set_border_width (10)

		self.play = gtk.Button (None,gtk.STOCK_MEDIA_PLAY)
		self.stop = gtk.Button (None,gtk.STOCK_MEDIA_STOP)
		self.play.connect ("clicked",self.gui_control.cb_ab_play_pressed)
		self.stop.connect ("clicked",self.gui_control.cb_ab_stop_pressed,self.play)

		"""
		Track exploring widget
		"""
		self.scale_adjustment = gtk.Adjustment(0.0, 0.00, 100.0, 0.1, 1.0, 1.0)
		hscale = gtk.HScale(self.scale_adjustment)
		hscale.set_digits(2)
		hscale.set_update_policy(gtk.UPDATE_CONTINUOUS)
		hscale.connect('button-press-event', self.gui_control.cb_ab_scale_button_press_cb)
		hscale.connect('button-release-event', self.gui_control.cb_ab_scale_button_release_cb)
		hscale.connect('format-value', self.gui_control.cb_ab_scale_format_value_cb)

		self.hscale = hscale

		hbox.pack_start(self.play,False,False)
		hbox.pack_start(self.stop,False,False)
		hbox.pack_end(hscale)

		return hbox


	def tracks_box (self):
		"""
		The scroll
		"""
		self.scrolled_window = gtk.ScrolledWindow()
		self.scrolled_window.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)

		"""
		The list treeview
		"""
		self.tracks_treeview = gtk.TreeView()
		self.tracks_treeview.set_rules_hint(True)
		#self.tracks_treeview.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
		self.tracks_treeview.enable_model_drag_dest ([("text/plain",0,0)], gtk.gdk.ACTION_DEFAULT)
		self.tracks_treeview.connect ("drag-drop", self.gui_control.cb_ab_drop)
		self.tracks_treeview.connect ("cursor-changed",self.gui_control.cb_ab_cursor_changed )
		self.tracks_treeview.connect ("button-press-event", self.gui_control.cb_ab_button_pressed)

		"""
		The columns in the treeview
		"""
		# Track list number column
		cellpb = gtk.CellRendererPixbuf()
		cell_text = gtk.CellRendererText()

		number_column = gtk.TreeViewColumn("No.")
		number_column.set_resizable(True)
		number_column.pack_start(cellpb,False)
		number_column.pack_start(cell_text,False)
		number_column.set_cell_data_func(cellpb,None) #TODO self.gui_control.cb_npfs_change_list_icon)
		number_column.set_cell_data_func(cell_text,self.gui_control.cb_ab_number_changed)

		# Artist column
		artist_renderer = gtk.CellRendererText()
		artist_column = gtk.TreeViewColumn("Artist")
		artist_column.pack_start(artist_renderer,False)
		artist_column.set_cell_data_func(artist_renderer,self.gui_control.cb_ab_artist_changed)
		artist_column.set_resizable(True)

		# Title column
		title_renderer = gtk.CellRendererText()
		title_column = gtk.TreeViewColumn("Title")
		title_column.pack_start(title_renderer,False)
		title_column.set_cell_data_func(title_renderer,self.gui_control.cb_ab_title_changed)
		title_column.set_resizable(True)
		title_column.width=600

#		# Type column
#		type_renderer = gtk.CellRendererText()
#		type_column = gtk.TreeViewColumn("Type")
#		type_column.pack_start(type_renderer,False)
#		type_column.set_cell_data_func(type_renderer,self.gui_control.cb_ab_genre_changed)
#		type_column.set_resizable(True)

		# Length column
		length_renderer = gtk.CellRendererText()
		length_column = gtk.TreeViewColumn("Length")
		length_column.pack_start (length_renderer)
		length_column.set_cell_data_func(length_renderer,self.gui_control.cb_ab_length_changed)
		length_column.set_resizable(True)

		# Filename column
		filename_renderer = gtk.CellRendererText()
		filename_column = gtk.TreeViewColumn("File name")
		filename_column.pack_start (filename_renderer)
		filename_column.set_cell_data_func(filename_renderer,self.gui_control.cb_ab_filename_changed)
		filename_column.set_resizable(True)

		# Appends columns to treeview
		self.tracks_treeview.append_column(number_column)
		self.tracks_treeview.append_column(artist_column)
		self.tracks_treeview.append_column(title_column)
		#self.tracks_treeview.append_column(type_column)
		self.tracks_treeview.append_column(length_column)
		self.tracks_treeview.append_column(filename_column)

		"""
		The liststore tied to the treeview
		"""
		self.tracks_liststore = gtk.ListStore(str,str,str,str,str)

		self.tracks_treeview.set_model(self.tracks_liststore)

		self.scrolled_window.add_with_viewport (self.tracks_treeview)

		return self.scrolled_window

	def song_details_box (self):
		frame = gtk.Frame()
		#frame.set_shadow_type(gtk.SHADOW_IN)

		event_box = gtk.EventBox()
		frame.add(event_box)

		detailsBox = gtk.HBox (False,0)
		event_box.add(detailsBox)
		event_box.modify_bg(gtk.STATE_NORMAL,event_box.get_colormap().alloc_color('#ffffff'))

		detailsBox.set_size_request(-1,200)

		self.cd_sleeve = gtk.Image ()
		self.cd_sleeve.set_from_file(ICONS_DIR + "/bubble_disk2.png")
		detailsBox.pack_start(self.cd_sleeve,False,False,20)

		song_details_box = gtk.VBox (False,5)
		tmpvbox = gtk.VBox (False,0)
		song_details_box.pack_start(tmpvbox,False,False,30)

		song_details_box2 = gtk.VBox (False,5)
		tmpvbox2 = gtk.VBox (False,0)
		song_details_box2.pack_start(tmpvbox2,False,False,30)

		artist_hbox = gtk.HBox (False,0)
		artist_hbox2 = gtk.HBox (False,0)
		artist_label = gtk.Label()
		artist_label.set_markup ('<span weight="bold">Artist:</span>')
		self.artist_name = gtk.Label ("")
		artist_hbox.pack_start (artist_label,False,False,5)
		tmpvbox.pack_start (artist_hbox,False,False,5)
		artist_hbox2.pack_start (self.artist_name,False,False,5)
		tmpvbox2.pack_start (artist_hbox2, False,False,5)

		title_hbox = gtk.HBox (False,0)
		title_hbox2 = gtk.HBox (False,0)
		title_label = gtk.Label()
		title_label.set_markup ('<span weight="bold">Title:</span>')
		self.artist_title = gtk.Label ("")
		title_hbox.pack_start (title_label,False,False,5)
		tmpvbox.pack_start (title_hbox,False,False,5)
		title_hbox2.pack_start (self.artist_title,False,False,5)
		tmpvbox2.pack_start (title_hbox2, False,False,5)


		album_hbox = gtk.HBox (False,0)
		album_hbox2 = gtk.HBox (False,0)
		album_label = gtk.Label()
		album_label.set_markup ('<span weight="bold">Album:</span>')
		self.artist_album = gtk.Label ("")
		album_hbox.pack_start (album_label,False,False,5)
		tmpvbox.pack_start (album_hbox,False,False,5)
		album_hbox2.pack_start (self.artist_album,False,False,5)
		tmpvbox2.pack_start (album_hbox2, False,False,5)

		genre_hbox = gtk.HBox (False,0)
		genre_hbox2 = gtk.HBox (False,0)
		genre_label = gtk.Label()
		genre_label.set_markup ('<span weight="bold">Genre:</span>')
		self.artist_genre = gtk.Label ("")
		genre_hbox.pack_start (genre_label,False,False,5)
		tmpvbox.pack_start (genre_hbox,False,False,5)
		genre_hbox2.pack_start (self.artist_genre,False,False,5)
		tmpvbox2.pack_start (genre_hbox2, False,False,5)

		length_hbox = gtk.HBox (False,0)
		length_hbox2 = gtk.HBox (False,0)
		length_label = gtk.Label()
		length_label.set_markup ('<span weight="bold">Length:</span>')
		self.artist_length = gtk.Label ("")
		length_hbox.pack_start (length_label,False,False,5)
		tmpvbox.pack_start (length_hbox,False,False,5)
		length_hbox2.pack_start (self.artist_length,False,False,5)
		tmpvbox2.pack_start (length_hbox2, False,False,5)

		detailsBox.pack_start(song_details_box,False,False)
		detailsBox.pack_start(song_details_box2,True,True)

		right_image = gtk.Image ()
		right_image.set_from_file(ICONS_DIR + "/audio_project_details_right_image2.png")
		detailsBox.pack_start(right_image,False,False)

		return frame