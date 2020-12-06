import gtk
import time

window = gtk.Window (gtk.WINDOW_TOPLEVEL)
image = gtk.Image ()
image.set_from_file ("/home/dsolimando/Multimedia/Images/bubbledisk/bubbledis.svg")
window.add (image)

window.set_decorated(False)

window.move(600,600)
window.show_all()
window.realize()

while gtk.events_pending():
    gtk.main_iteration()
print "waiting 2 sec..."
time.sleep(2)

while gtk.events_pending():
    gtk.main_iteration()
print "waiting 3 sec..."
time.sleep(3)
while gtk.events_pending():
    gtk.main_iteration()


