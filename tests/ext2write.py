#!/usr/bin/python

import sys
sys.path.insert(0,'../python_modules')
import ext2, vfs, block_device
import random

disk_image = './testimage'
image_file = '/fu'              # name of a file within that image
total_sectors = 4194304         # number of sectors in disk image

class ImageDrive( block_device.BlockDevice ):

    block_size = 512

    def __init__(self):
        self.drive = file(disk_image, 'r+')

    def read_sectors( self, first, count ):
        'Read any number of sectors from the drive, and return them as a string.'
        if first < 0 or count < 0 or first+count > total_sectors:
            raise ValueError( "Request for sectors beyond disk capacity" )

        if count == 0:
            return ''

        self.drive.seek( first*512 )
        return self.drive.read( count*512 )


    def write_sectors( self, first, data ):
        assert not len(data) % self.block_size
        self.drive.seek( first*512 )
        self.drive.write( data )



e = ext2.Ext2FS( ImageDrive() )
v = vfs.Vfs(e)
n = v.locate_node(image_file)
f1 = n.open()

#print '%i frags per group' % e.superblock.s_frags_per_group


#e._block_bitmaps[0].mark_bit(35, False)

#f1.write( ''.join([chr(x/0x100)+chr(x%0x100) for x in xrange(0, 0x1000, 2)]) )
f1.write( ''.join(['XXXXXXXXXXXXYYYYYYYYYYYYYYYYYZZZZZZZZZZZZZZZ this is line %i\n' % x for x in xrange(1, 20001)]) )
f1.seek(0x100)
#f1.write( 'this starts 20 bytes into the file, and should truncate here ->' )
f1.close()

#print 'file uses blocks:'
#for block in xrange( n.i_blocks/2 ):
#    print n.i_block[block]
#
#print 'bitmap says blocks are used:'
#for group in xrange( e._groups_count ):
#    print 'group %i' % group
#    for bit in xrange( e.superblock.s_frags_per_group ):
#        if e._block_bitmaps[group].read_bit(bit):
#            print group * e.superblock.s_frags_per_group + bit
