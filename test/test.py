#!/usr/bin/python
#
import gtk

class test:
    
    vbox1 = None
    vbox2 = None
    
    def change(self,widget,event,data=None):
        self.vbox1.hide_all()
        self.vbox2.show_all()
    
    def change2(self,widget,event,data=None):
            self.vbox2.hide_all()
            self.vbox1.show_all()
            
        
    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_size_request(600,400)
        vbox_main = gtk.VBox(True,10)
        button_temp = gtk.Button("test")
        self.vbox1 = gtk.VBox(False,5)
        self.vbox1.set_size_request(-1,400)
        
        self.vbox1.pack_start (button_temp, True, True )
        
        vbox_main.pack_start(self.vbox1,False,False)
        
        self.vbox2 = gtk.VBox(False,5)
        self.vbox2.set_size_request(-1,100)
        
        button_temp2 = gtk.Button("test2")
        self.vbox2.pack_start (button_temp2, True, True )
        
        vbox_main.pack_start(self.vbox2,False,False)
        
        vbox3 = gtk.HBox(False,5)
        vbox3.set_size_request(-1,100)
        
        button = gtk.Button("ok")
        button2 = gtk.Button("ko")
        
        button.connect("button_press_event",self.change)
        button2.connect("button_press_event",self.change2)
        
        vbox3.pack_start (button, False, True )
        vbox3.pack_start (button2, False, True )
        
        vbox_main.pack_start(vbox3,False,False)
        vbox_main.show()
        window.add(vbox_main)
        self.vbox1.show_all()
        vbox3.show_all()
        window.show()
        
def main():
    gtk.main()
    return()

if __name__ == "__main__":
    test()
    main()