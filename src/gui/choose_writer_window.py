import gtk
import gobject

from gui.bubble_windows import window
from gui.gui_tools import section_frame
from gui.gui_tools import devices_options_box

class choose_writer_window (window):

    gui_control = None
    gui_view = None

    device_manager = None
    application_manager = None

    window = None

    device_options_frame = None
    setup_hbox = None
    device_combo_box = None
    close_button = None

    def __init__ (self,gui_control,gui_view,dev_manager,app_manager):
        self.gui_control = gui_control
        self.gui_view = gui_view

        self.device_manager = dev_manager
        self.application_manager = app_manager

        self.window = gtk.Window (gtk.WINDOW_TOPLEVEL)
        self.window.set_size_request (500,500)
        self.window.set_title ("Choose Recorder")

        main_box = gtk.VBox (False,0)
        main_box.set_border_width (10)
        device_frame = self.device_choose_frame()
        main_box.pack_start (device_frame,False,False)

        device = self.device_manager.get_drive_features(self.device_manager.get_current_writer().get_device())
        self.device_options_frame = self.devices_options_frame (
                            device
                            )
        main_box.pack_start (self.device_options_frame,True,True)
        main_box.pack_start (gtk.HSeparator(),False,False)
        main_box.pack_start (self.buttons_box(),False,False)
        self.device_combo_box.connect("changed",
                                        self.gui_control.cb_choose_writer_window_change_writer,
                                        self.device_options_frame,
                                        self.device_manager.writers)
        self.window.add(main_box)



    def device_choose_frame (self):
        device_frame = section_frame("Burning Device")
        device_hbox = gtk.HBox (False,0)
        device_hbox.set_border_width (10)
        device_frame.add (device_hbox)

        self.device_combo_box = gtk.ComboBox()
        self.device_combo_box = gtk.combo_box_new_text()

        for device in self.device_manager.writers:
            print device.__class__.__dict__
            self.device_combo_box.append_text(device.get_name_for_display())

        self.device_combo_box.set_active(self.device_manager.used_device)

        device_hbox.pack_start(self.device_combo_box,True,True)
        return device_frame

    def devices_options_frame (self,device):
        setup_frame = section_frame ("Device features")
        options = device.print_friendly_devices_params ()
        self.setup_hbox = devices_options_box (options)
        setup_frame.add(self.setup_hbox)

        return setup_frame


    def buttons_box (self):
        hbox = gtk.HBox (False,0)
        hbox.set_border_width (10)
        self.close_button = gtk.Button ("Close",gtk.STOCK_CLOSE,True)
        self.close_button.connect ("pressed",self.gui_control.cb_hide_cw_window  )

        hbox.pack_end (self.close_button,False,False)

        return hbox
