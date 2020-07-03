class FSLimitError( IOError ):
    '''The technical capabilities of the filesystem were exceeded.
    
    Examples:
    - exceeding maximum file size
    - creating symlinks on a FS that does not support them.
    '''


class CorruptFSError( IOError ):
    '''Corruption was detected in the filesystem.
    
    Running a filesystem check would be a good idea. This is also raised if a
    filesystem is opened with the incorrect driver.
    '''


class FSDirtyError( CorruptFSError ):
    '''The filesystem is explicitly marked as dirty.

    Probably due to a crash or power loss, the filesystem is in an inconsistant
    state and recovery is required.
    '''


class NoSuchNodeError( IOError ):
    '''The specified node does not exist.'''


class InvalidNodeNameError( IOError ):
    '''An invalid name was used for a node.

    Examples:
    - filenames containing '/'
    - filenames too long
    - attempting to unlink "magic" . or ..
    - a file by that name already exists

    In all cases, changing the name might help.
    '''


class InvalidModeError( IOError ):
    '''An attempt was made to open a file with an invalid mode.
    
    This means the mode is not valid under any circumstances, and is distinct
    from an error in permissions.
    '''


class PermissionError( IOError ):
    '''Permission to perform the operation is lacking.
    
    This could be that the file permissions disallow the operation, or that a
    request to write to a file opened for reading only was made.
    '''


class FSFullError( IOError ):
    '''The filesystem is full, in one way or another.
    
    This could be because the disk is really full, or there are no free inodes,
    or all availible space is reserved. In all cases, deleting files might help.
    '''


class RootPath( object ):
    '''A placeholder class representing the root of the hierarchy.'''

class ParentPath( object ):
    '''A placeholder class representing the parent in the hierarchy.
    Traditionally, this has been called ".."'''

class SelfPath( object ):
    '''A placeholder class representing self in the hierarchy. Traditionally,
    this has been called "."'''



class Path( object ):
    def __init__( self, path=[] ):
        '''Create a new Path.

        `path` is an initializer which may be any sequence or a string with
        segments delimited by '/'. If `path` is not specified, the created Path
        will represent the current working directory.
        '''

        if isinstance( path, basestring ):
            segments = path.split('/')
            if segments[0] == '':
                path = [RootPath]
                del segments[0]
            else:
                path = []
            for segment in segments:
                if segment == '..':
                    path.append( ParentPath )
                elif segment == '.':
                    path.append( SelfPath )
                elif segment == '':
                    continue
                else:
                    path.append( segment )

        if not path:
            from uuu import root_vfs
            self._path = list(root_vfs.cwd)
            return
        if path[0] != RootPath:
            from uuu import root_vfs
            self._path = list(root_vfs.cwd)
        else:
            self._path = [RootPath]
        self.extend( path )


    def __getitem__( self, key ):
        return self._path[key]


    def __iter__( self ):
        return self._path.__iter__()


    def __len__( self ):
        return len( self._path )


    def __add__( self, other ):
        r = Path( self )
        r.extend( other )
        return r


    def append( self, element ):
        if element == RootPath:
            del self._path[1:]
        elif element == SelfPath:
            return
        elif element == ParentPath:
            if len(self._path) < 2:
                raise InvalidNodeNameError( 'path has too many ".."' )
            del self._path[-1]
        else:
            self._path.append(element)


    def extend( self, iterable ):
        for element in iterable:
            self.append( element )


    def __str__( self ):
        result = []
        for segment in self:
            if segment == RootPath:
                result = ['']
            elif segment == ParentPath:
                result.append('..')
            elif segment == SelfPath:
                result.append('.')
            else:
                result.append(str(segment))
        if len(result) == 1 and result[0] == '':
            return '/'
        return '/'.join(result)



fs_types = {}

def register_fs( type, create ):
    '''Register a filesystem driver.

    `type` is the name of the filesystem as a string, such as "ext2". `create`
    is a callable taking two parameters, what to mount, and arbitrary options.
    On calling, it returns an instance of the filesystem.
    '''

    fs_types[type] = create


class Vfs( object ):
    __cwd = Path([RootPath])

    def __init__( self, root ):
        '''Create a new VFS.

        `root` is a `Node` which will become the root of the vfs hierarchy. This
        is most usually an instance of ramfs.Node, although another filesystem
        could be used if it supported all the VFS features.
        '''
        self._root = root


    def locate_nodes( self, path, create=False, mode=0666 ):
        '''Return a node addressed by the normalized `path`.

        If `create` is True and all nodes but the last are found, then it will
        be created as a regular file and returned.
        '''

        if not isinstance( path, Path ):
            path = Path(path)
        prepath = []
        nodes = [self._root]
        last_exception = None
        for segment in path:
            prepath += (segment,)
            child_nodes = []
            for node in nodes:
                try:
                    child_nodes.extend( node[segment] )
                except NoSuchNodeError, last_exception:
                    pass
            if not child_nodes:
                if len(prepath) == len(path) and create:
                    for parent_node in nodes:
                        try:
                            if parent_node.filesystem is self._root.filesystem:
                                continue
                            return [parent_node.create_regular_child( segment, mode )]
                        except PermissionError:
                            if parent_node is nodes[-1]:
                                raise
                if last_exception:
                    raise last_exception
                else:
                    raise NoSuchNodeError( 'node does not exist' )
            assert child_nodes
            nodes = child_nodes
        return nodes


    def open( self, path, read=False, write=False, create=False, truncate=False, append=False, mode=0666 ):
        if not isinstance( path, Path ):
            path = Path(path)
        nodes = self.locate_nodes( path, create=create, mode=mode )
        for node in nodes:
            try:
                return node.open( read=read, write=write, append=append, truncate=truncate )
            except PermissionError:
                if node is nodes[-1]:
                    raise
        assert False # locate_nodes should always return at least one node


    def mount( self, source, path, filesystem_type, options=None ):
        '''Mount a filesystem.

        Parameters:
        - `source`: what to mount. Usually a `Path` to a device, but is FS
          dependant.
        - `path`: target path to which to bind the mounted filesystem
        - `filesystem_type`: the type of filesystem, such as "ext2"
        - `options`: arbitrary options passed to the filesystem
        '''

        try:
            fs_creator = fs_types[filesystem_type]
        except KeyError:
            raise ValueError( 'filesystem type %r not registered' % filesystem_type )

        self.bind( [fs_creator(source, options)], path )


    def bind( self, nodes, path ):
        '''Bind a list of nodes to a path.'''

        def get_node( node, segment ):
            try:
                child_nodes = node[segment]
            except NoSuchNodeError:
                return node.mkdir( segment )
            for child_node in child_nodes:
                if child_node.filesystem is node.filesystem:
                    return child_node
            return node.mkdir( segment )

        if not isinstance( path, Path ):
            path = Path(path)
        node = self._root
        for segment in path[:-1]:
            node = get_node( node, segment )
        d = node.opendir()
        try:
            d.link( nodes, path[-1] )
        finally:
            d.close()


    def get_cwd( self ):
        return self.__cwd

    def set_cwd( self, path ):
        new_path = Path(path)
        self.locate_nodes( new_path )   # try, to see that it exists
        self.__cwd = Path(path)

    cwd = property( get_cwd, set_cwd )



class Node( object ):
    '''Represents all nodes in the filesystem hierarchy.'''

    def __getitem__( self, name ):
        '''Get a list of children matching `name`.

        Although most filesystems require each child to have a unique name, this
        method returns a list of matching nodes, allowing multiple children
        under the same name. This property is used internally by VFS to support
        mount unions. It could also be used by hierarchies such as XML that do
        not have the unique name requirement.

        Also, the name may be any hashable python object. While most filesystems
        intended for human interaction use strings, the VFS does not impose any
        such requirement. However, the current implementation reserves the
        strings '.' and '..' for special use. This is likely to change in the
        future, replacing them with python objects. However, the the common
        string based interfaces will retain their special meaning.

        Filesystem implementations should override this method if applicable. If
        no matching nodes are found, `NoSuchNodeError` should be raised, not
        KeyError.
        '''
        raise NoSuchNodeError( 'node does not exist' )


    def create_regular_child( self, name, mode=0666 ):
        '''Create and return a regular file child of `self`.

        parameters:
        -----------
        - `name`: the name to use for the created child
        - `mode`: the permissions to give the newly created file
        '''


    def open( self, read=False, write=False, append=False, truncate=False ):
        '''Return a `File` instance for this node.

        While the `Node` instance represents the entity as a whole, the
        coresponding `File` instance represents the data stored within that node
        to allow reading and writing.

        Filesystem implementations should override this method if applicable.
        FSLimitError should be raised if the implementation does not opening
        this sort of node.
        '''
        raise FSLimitError( 'node does not support opening' )


    def opendir( self ):
        '''Return a `Directory` instance for this node.

        While the `Node` instance represents the entity as a whole, the
        coresponding `Directory` instance represents the node's metadata
        regarding the node's children.

        Filesystem implementations should override this method if applicable.
        FSLimitError should be raised if the implementation does not opening
        this sort of node.
        '''
        raise FSLimitError( 'node does not support directory operations' )



class Directory( object ):
    '''Represents an open directory.'''

    closed = False

    def __iter__( self ):
        '''Iterate over the name of each child node.'''

        if self.closed:
            raise ValueError( 'I/O operation on closed directory' )
        raise FSLimitError( 'node does not support opening' )


    def unlink( self, name ):
        '''Unlink child `name`'''

        if self.closed:
            raise ValueError( 'I/O operation on closed directory' )
        raise FSLimitError( 'node does not support opening' )


    def link( self, nodes, name ):
        '''Link `Node` instances in iterable `node` to the directory as
        `name`.'''

        if self.closed:
            raise ValueError( 'I/O operation on closed directory' )
        raise FSLimitError( 'node does not support opening' )


    def close( self ):
        '''Close this directory.

        `closed` attribute will be set to True. Any further operations on this
        directory raise ValueError. `close` may be called multiple times without
        error. Filesystem implementations should override this method if they
        need to do more than set the `closed` attribute to True.
        '''

        self.closed = True


    def check_closed( self ):
        '''Raise ValueError iff `self` is closed.
        
        This can be used by File subclasses.
        '''

        if self.closed:
            raise ValueError( 'I/O operation on closed file' )



class File( object ):
    '''Represents an open file.'''

    closed = False
    always_append = False
    allow_read = False
    allow_write = False

    def close( self ):
        '''Close this file.

        `closed` attribute will be set to True. Any further operations on this
        directory raise ValueError. `close` may be called multiple times without
        error. Filesystem implementations should override this method if they
        need to do more than set the `closed` attribute to True.
        '''

        self.closed = True


    def seek( self, offset, whence=0 ):
        '''Move to a new file position.

       Argument `offset` is a byte count. Optional argument `whence` defaults to
       0 (offset from start of file, offset should be >= 0); other values are 1
       (move relative to current position, positive or negative), and 2 (move
       relative to end of file). Seeking beyond the end a file is legal, and
       results in the file being extended by zeros. Filesystem implementations
       should override this method if applicable. If `seek` is supported, so
       must be `tell`.
       '''

        raise FSLimitError( 'node does not support seeking' )


    def tell( self ):
        '''Return the current file offset.
        
        Filesystem implementations should override this if `seek` is
        implemented.
        '''

        raise FSLimitError( 'node does not support seeking' )


    def read( self, size=None ):
        '''Read at most `size` bytes, returned as a string.

        If `size` is None, read until EOF is reached.
        '''

        raise FSLimitError( 'node does not support reading' )


    def write( self, data ):
        '''Write `data` to the file.'''

        raise FSLimitError( 'node does not support writing' )


    def stat( self ):
        '''Return a Stat object for this file.'''

        raise FSLimitError( 'node does not support stat' )


    def check_closed( self ):
        '''Raise ValueError iff `self` is closed.
        
        This can be used by File subclasses.
        '''

        if self.closed:
            raise ValueError( 'I/O operation on closed file' )
