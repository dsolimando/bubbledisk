import gnomevfs

"""
Object GnomeVFSVolumeMonitorClient

'get_mounted_volumes'
'__new__'
'get_volume_for_path'
'__doc__'
'get_connected_drives'
'__gtype__'
'get_drive_by_id'
'get_volume_by_id'
'__init__'

Signals from GObject:
  notify (GParam)

Signals from GnomeVFSVolumeMonitor:
  volume-mounted (GnomeVFSVolume)
  volume-pre-unmount (GnomeVFSVolume)
  volume-unmounted (GnomeVFSVolume)
  drive-connected (GnomeVFSDrive)
  drive-disconnected (GnomeVFSDrive)

VolumeMounted Object

'get_drive'
'get_hal_udi'
'get_display_name'
'get_icon'
'__new__'
'is_user_visible'
'__cmp__'
'get_device_path'
'unmount'
'get_device_type'
'get_id'
'is_mounted'
'is_read_only'
'handles_trash'
'eject'
'get_filesystem_type'
'get_volume_type'
'__doc__'
'get_activation_uri'
'__gtype__'

Drive Object (cdroms, network devices,usb devices,...)

'get_hal_udi'
'get_mounted_volumes'
'get_display_name'
'get_icon', '__new__'
'is_user_visible'
'get_device_path'
'unmount'
'get_device_type'
'get_id'
'is_mounted'
'__doc__'
'eject'
'__gtype__'
'__cmp__'
'is_connected'
'mount'
'get_activation_uri'


"""
def fait_rien():
    return
    
gvfs = gnomevfs.VolumeMonitor()

connected_drives = gvfs.get_connected_drives()
for drive in connected_drives:
    print drive.get_display_name()
    try:
        print drive.get_mounted_volumes()[0].get_device_path()
    except IndexError:
        pass
    print drive.get_activation_uri()
    print drive.is_mounted()
    print drive.get_device_type()

def hello():
    pass

connected_drives[2].get_mounted_volumes()[0].unmount(hello)
#vol_mounted = gvfs.get_mounted_volumes()

#for vol in vol_mounted:
#        print vol.get_display_name()
#        print vol.get_icon()
