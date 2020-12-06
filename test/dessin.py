import gtk
import math
import time


global drawing_area,gc


def area_expose_cb (area, event):
    style = drawing_area.get_style()
    print style
    gc = style.fg_gc[gtk.STATE_NORMAL]
    
    for elem in drawing_area.window.__class__.__dict__:
        print elem
    i = 0.00
    while i < math.pi*2:
        i+=0.01
        print 150+math.sin(i*(300/(math.pi*2)))
        drawing_area.window.draw_point(gc,150+100*math.sin(i*(300/(math.pi*2))),(300/(math.pi*2))*i)
        drawing_area.window.clear_area()
        time.sleep (0.05)
        print (300/(math.pi*2))*i
        

window2 = gtk.Window()
window2.set_size_request(300,300)

drawing_area = gtk.DrawingArea()
drawing_area.set_size_request(300,300)
drawing_area.connect("expose-event",area_expose_cb)

window2.add (drawing_area)
window2.show_all()
gtk.main()