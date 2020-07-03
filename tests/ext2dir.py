#!/usr/bin/python

import sys
sys.path.insert(0,'../python_modules')
import ext2, vfs, block_device
import random

disk_image = './,testimage'
image_file = '/fu'              # name of a file within that image

class ImageDrive( block_device.BlockDevice ):

    block_size = 512

    def __init__(self):
        self.drive = file(disk_image, 'r+')

    def read_sectors( self, first, count ):
        'Read any number of sectors from the drive, and return them as a string.'
        if first < 0 or count < 0:
            raise ValueError( "Request for sectors beyond disk capacity" )

        if count == 0:
            return ''

        self.drive.seek( first*512 )
        return self.drive.read( count*512 )


    def write_sectors( self, first, data ):
        assert not len(data) % self.block_size
        self.drive.seek( first*512 )
        self.drive.write( data )



e = ext2.FileSystem( ImageDrive() )
v = vfs.Vfs(e)
node = v.locate_node(image_file)
rootdir = v.locate_node('/').opendir()

#for i in xrange( 10 ):
#    rootdir.link( node, '----------link----------'+str(i) )
rootdir.unlink('fu')

for i in rootdir._iterchildren():
    print i

rootdir.close()
