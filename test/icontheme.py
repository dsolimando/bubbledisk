import gtk
import string
import gnome.vfs
import gnome
import ldap



try:
    #l = ldap.open("localhost", 31001)
    l = ldap.open("172.16.10.1")
    
    #login_dn = "cn=manager,o=multitel,c=be"
    #login_pw = getpass.getpass("Password for %s: " % login_dn)
    #l.simple_bind_s(login_dn, login_pw)
    
    
    #
    # search beneath the CSEE/UQ/AU tree
    #
    
    res = l.search_s(
        "ou=staff,o=multitel,c=be", 
        ldap.SCOPE_SUBTREE, 
        "objectclass=*",
          )
    
    for key, value in res.items(): 
        print key
    
    l.unbind()
    
except ldap.LDAPError, msg:
    print "erreur"

#icon = gnome.vfs.mime_get_default_action("image/gif")
#print icon
#iconth = gtk.icon_theme_get_for_screen(gtk.gdk.screen_get_default())
#iconth_def = gtk.icon_theme_get_default()
#iconlist = iconth_def.list_icons(context=None)
#
#for icon in iconlist:
#    if string.find(icon,"png") != -1:
#        print icon