'''A volatile filesystem that stores all nodes in RAM.

This is used to provide read/write access when only readonly media is
availiable, and also to provide mountpoints for devices. It might later be
replaced by a more general VFS.
'''

import vfs

class Node( vfs.Node ):

    def __init__( self, filesystem=None, data='' ):
        self._children = {}
        self._data = data
        if isinstance( filesystem, Node ):
            self.filesystem = filesystem
        elif filesystem is None:
            self.filesystem = self
        else:
            raise TypeError( 'filesystem must be a Node instance' )


    def __getitem__( self, name ):
        try:
            return self._children[name]
        except KeyError:
            raise vfs.NoSuchNodeError( 'node does not exist' )


    def open( self, read=False, write=False, append=False, truncate=False ):
        return File( self, read=read, write=write, append=append, truncate=truncate )


    def opendir( self ):
        return Directory( self )


    def truncate( self, len ):
        self._data = self._data[:len]


    def create_regular_child( self, name, mode=0666 ):
        node = Node( self.filesystem )
        self._children.setdefault( name, [] ).append( node )
        return node

    mkdir = create_regular_child



class Directory( vfs.Directory ):
    def __init__( self, node ):
        self._node = node


    def __iter__( self ):
        self.check_closed()

        for name in self._node._children:
            for _ in xrange( len(self._node._children[name]) ):
                yield name


    def unlink( self, name ):
        # TODO: change this interface, because it's incompatable with multiple
        # nodes by the same name

        self.check_closed()

        try:
            del self._node._children[name]
        except KeyError:
            raise vfs.NoSuchNodeError( 'node does not exist' )


    def link( self, nodes, name ):
        self._node._children.setdefault( name, [] ).extend( nodes )



class File( vfs.File ):
    _position = 0

    def __init__( self, node, read=False, write=False, append=False, truncate=False ):
        if write:
            self.allow_write = True
        if read:
            self.allow_read = True
        if truncate:
            node.truncate(0)
        if append:
            self.always_append = True
            #self.seek( node.i_size )
        self._node = node

    def seek( self, offset, whence=0 ):
        self.check_closed()
        if whence == 0:
            if offset < 0:
                raise IOError( 'can not seek to negative offset' )
            self._position = offset
        elif whence == 1:
            if self._position + offset < 0:
                raise IOError( 'can not seek to negative offset' )
            self._position += offset
        elif whence == 2:
            if len(self._node._data) + offset < 0:
                raise IOError( 'can not seek to negative offset' )
            self._position = len(self._node._data) + offset
        else:
            raise IOError( "invalid whence for seek" )


    def tell( self ):
        self.check_closed()
        return self._position


    def read( self, size = None ):
        self.check_closed()
        if not self.allow_read:
            raise vfs.PermissionError( 'file not opened for reading' )
        if size is not None:
            r = self._node._data[self._position:self._position+size]
        elif self._position:
            r = self._node._data[self._position:]
        else:
            r = self._node._data
        self._position += len(r)
        return r


    def write( self, data ):
        self.check_closed()
        if not self.allow_write:
            raise vfs.PermissionError( 'file not opened for writing' )
        self._node._data = \
            self._node._data[:self._position] \
            + chr(0) * (self._position - len(self._node._data)) \
            + data \
            + self._node._data[self._position+len(data):]
        self._position += len(data)
        return len(data)


    def stat( self ):
        self.check_closed()
        return Stat( self._node )



class Stat( object ):
    def __init__( self, node ):
        #self.st_dev = node.
        #self.st_ino = node.number
        #self.st_mode = node.i_mode
        #self.st_nlink = node.i_links_count
        self.st_uid = 0
        self.st_gid = 0
        #self.st_rdev = node.
        self.st_size = len(node._data)
        #self.st_blksize = node.
        #self.st_blocks = node.
        self.st_atime = 0
        self.st_mtime = 0
        self.st_ctime = 0



vfs.register_fs( 'ramfs', lambda _, __: Node() )
