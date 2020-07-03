#!/usr/bin/python

'''A test for unununium's ext2.py

Given a disk image, a path to a file within that, and an identicial file on the
host machine (think loopback), this program will read them in various ways and
compare.'''

import sys
sys.path.insert(0,'../python_modules')
import ext2, vfs, block_device
import random

disk_image = './testimage'
image_file = '/fu'              # name of a file within that image
native_file = '/mnt/tmp/fu'     # name of the same file from host OS
total_sectors = 4194304         # number of sectors in disk image
max_frag_size = 1024 * 8        # for random seek test, largest fragment
compare_block_size = 1024       # size of block to use to compare
random_iterations = 10000



class ImageDrive( block_device.BlockDevice ):

    block_size = 512

    def __init__(self):
        self.drive = file(disk_image)

    def read_sectors( self, first, count ):
        'Read any number of sectors from the drive, and return them as a string.'
        print 'reading %r %r' % (first, count)
        if first < 0 or count < 0 or first+count > total_sectors:
            raise ValueError( "Request for sectors beyond disk capacity" )

        if count == 0:
            return ''

        self.drive.seek( first*512 )
        return self.drive.read( count*512 )



e = ext2.Ext2FS( ImageDrive() )
v = vfs.Vfs(e)
n = v.locate_node(image_file)
f1 = n.open()
f2 = file(native_file)

observed_size = 0

print 'comparing files'

while True:
    r1 = f1.read(compare_block_size)
    r2 = f2.read(compare_block_size)
    if r1 != r2:
        raise AssertionError( 'files differ after %i bytes' % observed_size )
    observed_size += len(r1)
    if not r1:
        print 'compare test passed'
        break

f1.seek( 0, 2 )
f2.seek( 0, 2 )

size1 = f1.tell()
size2 = f2.tell()

assert size1 == size2
assert size1 == observed_size

for i in xrange(random_iterations):
    pos = random.randrange( 0, size1-max_frag_size )
    len = random.randint( 1, max_frag_size )
    f1.seek(pos)
    f2.seek(pos)
    r1 = f1.read(len)
    r2 = f2.read(len)
    assert r1 == r2

print 'random seek test passed'
