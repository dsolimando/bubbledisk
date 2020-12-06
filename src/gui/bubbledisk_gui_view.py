import bubbledisk_gui_model

class bubbledisk_gui_view:
	HORIZONTAL = 1
	VERTICAL = 2
	LEFT =1
	RIGHT = 2
	VFS_LEFT = 1
	VFS_RIGHT = 2

	current_explorers_direction = 0
	current_vfs_position = 0
	show_toolbar = True
	gui_model = None

	current_treeiter = None
	current_fs_dir_browsed = None
	files_selected_list = []
	moving_cell_path = None

	config_handler = None
	current_paned = None
	paned_position = 0

	project_media = "cd"

	def __init__(self,config):
		self.config_handler = config
		if self.config_handler.get ("view/explorer_view") == "vertical":
			self.current_explorers_direction = self.VERTICAL
		else:
			self.current_explorers_direction = self.HORIZONTAL

		if self.config_handler.get ("view/explorer_sense") == "right":
			self.current_vfs_position = self.VFS_RIGHT
		else:
			self.current_vfs_position = self.VFS_LEFT


	def set_model (self,model):
		self.gui_model = model

	def get_current_explorers_direction(self):
		return self.current_explorers_direction

	def get_current_vfs_position(self):
		return self.current_vfs_position

	def get_show_toolbar (self):
		return self.show_toolbar

	def set_explorers_direction(self,direction, vfs_position):
		if direction !=	self.current_explorers_direction or vfs_position != self.current_vfs_position:
			print "function set_explorers_direction"
			self.gui_model.vpaned.hide()
			self.gui_model.hpaned.hide()

			if (self.current_explorers_direction == self.HORIZONTAL and direction == self.HORIZONTAL):
				print "1"
				paned_to_remove = self.gui_model.vpaned
				paned_to_add = self.gui_model.vpaned
				self.paned_position= int(self.config_handler.get ("view/window_height")/2-100)
			elif (self.current_explorers_direction == self.VERTICAL and direction == self.VERTICAL):
				print "2"
				paned_to_remove = self.gui_model.hpaned
				paned_to_add = self.gui_model.hpaned
				self.paned_position= int(self.config_handler.get ("view/window_width")/2)
			elif (self.current_explorers_direction == self.HORIZONTAL and direction == self.VERTICAL):
				print"3"
				paned_to_remove = self.gui_model.vpaned
				paned_to_add = self.gui_model.hpaned
				self.paned_position= int(self.config_handler.get ("view/window_width")/2)
			elif (self.current_explorers_direction == self.VERTICAL and direction == self.HORIZONTAL):
				print "4"
				paned_to_remove = self.gui_model.hpaned
				paned_to_add = self.gui_model.vpaned
				self.paned_position= int(self.config_handler.get ("view/window_height")/2-100)

			self.current_explorers_direction = direction
			self.current_vfs_position = vfs_position
			self.current_paned = paned_to_add

			temp_dirtree = self.gui_model.dirtree
			temp_project_treeview = self.gui_model.projectvbox

			paned_to_remove.remove(self.gui_model.dirtree)
			paned_to_remove.remove(self.gui_model.projectvbox)

			if vfs_position == self.VFS_LEFT:
				paned_to_add.add1(temp_dirtree)
				paned_to_add.add2(temp_project_treeview)
			else:
				print "right"
				paned_to_add.add2(temp_dirtree)
				paned_to_add.add1(temp_project_treeview)

			paned_to_add.set_position(self.paned_position)
			self.gui_model.dirtree = temp_dirtree
			self.gui_model.project_treeview_vbox = temp_project_treeview
			paned_to_add.show()

	def set_show_toolbar (self,show):
		self.show_toolbar = show

	def set_initial_view (self):
		self.gui_model.vbox_menu.show_all()
		self.gui_model.vbox_toolbar.show_all()
		self.gui_model.progressbar_hbox.show_all()

		self.gui_model.hbox_status.show_all()
		if self.config_handler.get ("view/explorer_view") == "vertical":
			self.gui_model.hpaned.show_all()
		else:
			self.gui_model.vpaned.show_all()

		self.gui_model.vbox_hpaned.show()
		self.gui_model.mainBox.show()
		self.gui_model.window.show()
		self.project_media = "cd"
		self.gui_model.proj_window.switch_icon_boxes(self.project_media);

		self.set_no_project_view()

	def set_audio_project_window_view (self):
		pass

	def set_no_project_view (self):
		self.gui_model.uiManager.get_widget ("/ToolBar/Save").hide()
		self.gui_model.uiManager.get_widget ("/ToolBar/CompilInfos").hide()

		self.gui_model.uiManager.get_widget ("/MenuBar/ProjectMenu").hide()

	def set_data_project_view (self):
		self.gui_model.uiManager.get_widget ("/ToolBar/Save").show()
		self.gui_model.uiManager.get_widget ("/ToolBar/CompilInfos").show()
		self.gui_model.uiManager.get_widget ('/ToolBar/WriteCd').show()

		self.gui_model.uiManager.get_widget ("/MenuBar/ProjectMenu").show()
