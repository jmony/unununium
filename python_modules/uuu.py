import vfs, ramfs

root_vfs = vfs.Vfs( ramfs.Node() )
dev_path = vfs.Path('/dev')

def reboot():
    import disk_cache, sys
    for disk in disk_cache.cached_disks.keys():
        disk.disable_cache()
    sys.exit()
