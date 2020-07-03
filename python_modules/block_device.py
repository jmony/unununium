import vfs

class BlockDevice( object ):

    def read_bytes( self, first, count ):
        first_block = first / self.block_size
        offset = first % self.block_size
        last_block = (count + first) / self.block_size # exclusive
        end_offset = (count + first) % self.block_size
        if end_offset:
            last_block += 1

        if not offset and not end_offset:
            return self.read_sectors( first_block, last_block-first_block )
        else:
            return self.read_sectors( first_block, last_block-first_block )\
                [offset:offset+count]


    def write_bytes( self, first, data ):
        first_block = first / self.block_size
        leading_bytes = first % self.block_size
        last_block = (len(data) + first) / self.block_size # inclusive
        trailing_bytes = (len(data) + first) % self.block_size

        if not (leading_bytes or trailing_bytes):
            assert not len(data) % self.block_size and not first % self.block_size
            self.write_sectors( first_block, data )
        else:
            if leading_bytes:
                first_block_data = self.read_sectors( first_block, 1 )
                data = first_block_data[:leading_bytes] + data
            if trailing_bytes:
                if first_block == last_block and leading_bytes:
                    last_block_data = first_block_data
                else:
                    last_block_data = self.read_sectors( last_block, 1 )
                data += last_block_data[trailing_bytes:]
            self.write_sectors( first_block, data )


    def open( self, read=False, write=False, append=False, truncate=False ):
        if append:
            raise Exception( 'appending to block devices is not yet supported' )
        return File( self, read=read, write=write )



class File( vfs.File ):

    _position = 0

    def __init__( self, device, read=False, write=False ):
        if write:
            if not device.allow_write:
                raise IOError( 'device does not support writing' )
            self.allow_write = True
        if read:
            if not device.allow_read:
                raise IOError( 'device does not support reading' )
            self.allow_read = True
        self._device = device
        self.block_size = device.block_size


    def seek( self, offset, whence=0 ):
        if self.closed:
            raise ValueError( 'I/O operation on closed file' )
        if whence == 0:
            if offset < 0:
                raise IOError( 'can not seek to negative offset' )
            self._position = offset
        elif whence == 1:
            if self._position + offset < 0:
                raise IOError( 'can not seek to negative offset' )
            self._position += offset
        elif whence == 2:
            raise Exception( 'no way to find end of block device; someone implement this' )
        else:
            raise IOError( 'invalid whence for seek' )


    def tell( self ):
        if self.closed:
            raise ValueError( 'I/O operation on closed file' )
        return self._position


    def read( self, size = None ):
        if self.closed:
            raise ValueError( 'I/O operation on closed file' )
        if not self.allow_read:
            raise vfs.PermissionError( 'file not opened for reading' )
        if size is None:
            raise NotImplementError
        else:
            r = self._device.read_bytes( self._position, size )
        self._position += len(r)
        return r


    def write( self, data ):
        if self.closed:
            raise ValueError( 'I/O operation on closed file' )
        if not self.allow_write:
            raise vfs.PermissionError( 'file not opened for writing' )
        self._device.write_bytes( self._position, data )
        self._position += len(data)


    def read_sectors( self, first, count ):
        if not self.allow_read:
            raise vfs.PermissionError( 'file not opened for reading' )
        return self._device.read_sectors( first, count )


    def write_sectors( self, first, count ):
        if not self.allow_write:
            raise vfs.PermissionError( 'file not opened for writing' )
        return self._device.write_sectors( first, count )


    def read_bytes( self, first, count ):
        if not self.allow_read:
            raise vfs.PermissionError( 'file not opened for reading' )
        return self._device.read_bytes( first, count )


    def write_bytes( self, first, count ):
        if not self.allow_write:
            raise vfs.PermissionError( 'file not opened for writing' )
        return self._device.write_bytes( first, count )


    def stat( self ):
        if self.closed:
            raise ValueError( 'I/O operation on closed file' )
        return Stat( self._device )



class Stat( object ):
    def __init__( self, device ):
        #self.st_dev = device.
        #self.st_ino = device.number
        #self.st_mode = device.i_mode
        #self.st_nlink = device.i_links_count
        self.st_uid = 0
        self.st_gid = 0
        #self.st_rdev = device.
        self.st_size = len(device._data)
        #self.st_blksize = device.
        #self.st_blocks = device.
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0
