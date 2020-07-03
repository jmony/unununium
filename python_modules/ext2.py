'''A readonly implementation of the second extended filesystem in Python.

This is a rather simple implementation, and does not implement some of the
advanced or rarely used features of ext2. It does not yet support symlinks, but
that should be rather easy to implement when the time comes.

This has been throughly tested on a Linux created FS reading a 2GiB file. With
the block size at 1024 this is enough to get into ternary indirection. Writing
has been tested somewhat, but due to the complexity of writing and the
potential of data loss, this module should only be used on filesystems with
unimportant data. Please report bugs to <uuu-devel@unununium.org>.

Information needed to improve this implementation:

- what do the st_dev, st_rdev, st_blksize, and st_blocks fields of the stat
  structure mean precisely?

- how are files larger than 4GiB handled? The inode structure allocates only 4
  bytes to store the size; is this to mean that it's the size, mod 2**32, and
  the missing bits are to be inferred by the block count?

- if the inode size != 128, can one safely assume that an integral number of
  inodes fit in one block? Will an inode ever be smaller than 128 bytes?

- do block and inode bitmaps always fit exactly in a block? A disk sector? Do
  they always have a multiple of 8 bits? It seems linux pads the bitmaps with
  -1 until the end of the block, but fsck does not identify an error if this
  padding is altered. TODO: This implementation assumes bitmaps always end on a
  byte boundry; this is probably a bad assumption.

- where are superblock and group descriptor copies stored? This implementation
  ignores them.

- from experimentation, it seems 0 in a file's blocklist is valid, and means
  that block of data consists entirely of 0s. Is this true? This implementation
  assumes it is.

- can there be non-zero block numbers stored in i_block or the indirect blocks
  it references if the file is smaller than what would be needed to use that
  number of blocks? For example, if a file is only one block large, may the 2nd
  block number be non-zero? Experimentation with fsck indicates this is an
  error.

- experimentation suggests that i_blocks is the count of real disk sectors
  actually used by the file and related metadata. It includes indirect blocks
  allocated for the block list, and does not include sparse regions of the
  file. Is this correct?

If you know the answers to any of these questions, please contact
<uuu-devel@unununium.org>.

Most of this stuff was written using http://www.nongnu.org/ext2-doc/ as a
reference. Besides the questions remaining above, here is a list of errors I
have found:

- directory entries must be aligned on a 4 byte boundry
'''

import struct
import array

from block_device import BlockDevice
import vfs

EXT2_MAGIC = 0xef53

EXT2_VALID_FS = 1
EXT2_ERROR_FS = 0

EXT2_ROOT_INO = 0x02

EXT2_GOOD_OLD_REV = 0  # original format
EXT2_DYNAMIC_REV = 1   # V2 format with dynamic inode sizes

# file types for directory entries
EXT2_FT_UNKNOWN = 0 
EXT2_FT_REG_FILE = 1
EXT2_FT_DIR = 2
EXT2_FT_CHRDEV = 3 
EXT2_FT_BLKDEV = 4
EXT2_FT_FIFO = 5 
EXT2_FT_SOCK = 6 
EXT2_FT_SYMLINK = 7 
EXT2_FT_MAX = 8

# flags for Node.i_mode
EXT2_S_IFMT = 0xF000 # format mask
EXT2_S_IFSOCK = 0xC000 # socket
EXT2_S_IFLNK = 0xA000 # symbolic link
EXT2_S_IFREG = 0x8000 # regular file
EXT2_S_IFBLK = 0x6000 # block device
EXT2_S_IFDIR = 0x4000 # directory
EXT2_S_IFCHR = 0x2000 # character device
EXT2_S_IFIFO = 0x1000 # fifo

i_mode_to_ft = {
    EXT2_S_IFREG: EXT2_FT_REG_FILE,
    EXT2_S_IFDIR: EXT2_FT_DIR,
    EXT2_S_IFCHR: EXT2_FT_CHRDEV,
    EXT2_S_IFBLK: EXT2_FT_BLKDEV,
    EXT2_S_IFIFO: EXT2_FT_FIFO,
    EXT2_S_IFSOCK: EXT2_FT_SOCK,
    EXT2_S_IFLNK: EXT2_FT_SYMLINK
}

# more flags for Node.i_mode
EXT2_S_ISUID = 0x0800 # SUID
EXT2_S_ISGID = 0x0400 # SGID
EXT2_S_ISVTX = 0x0200 # sticky bit
EXT2_S_IRWXU = 0x01C0 # user access rights mask
EXT2_S_IRUSR = 0x0100 # read
EXT2_S_IWUSR = 0x0080 # write
EXT2_S_IXUSR = 0x0040 # execute
EXT2_S_IRWXG = 0x0038 # group access rights mask
EXT2_S_IRGRP = 0x0020 # read
EXT2_S_IWGRP = 0x0010 # write
EXT2_S_IXGRP = 0x0008 # execute
EXT2_S_IRWXO = 0x0007 # others access rights mask
EXT2_S_IROTH = 0x0004 # read
EXT2_S_IWOTH = 0x0002 # write
EXT2_S_IXOTH = 0x0001 # execute

# flags for Node.i_flags
EXT2_SECRM_FL = 0x00000001      # secure deletion
EXT2_UNRM_FL = 0x00000002       # record for undelete
EXT2_COMPR_FL = 0x00000004      # compressed file
EXT2_SYNC_FL = 0x00000008       # synchronous updates
EXT2_IMMUTABLE_FL = 0x00000010  # immutable file
EXT2_APPEND_FL = 0x00000020     # append only
EXT2_NODUMP_FL = 0x00000040     # do not dump/delete file
EXT2_NOATIME_FL = 0x00000080    # do not update .i_atime
EXT2_DIRTY_FL = 0x00000100      # dirty (file is in use?)
EXT2_COMPRBLK_FL = 0x00000200   # compressed blocks
EXT2_NOCOMPR_FL = 0x00000400    # access raw compressed data
EXT2_ECOMPR_FL = 0x00000800     # compression error
EXT2_BTREE_FL = 0x00010000      # b-tree format directory
EXT2_INDEX_FL = 0x00010000      # Hash indexed directory
EXT2_IMAGIC_FL = 0x00020000     # ?
EXT3_JOURNAL_DATA_FL = 0x00040000 # journal file data
# the following causes a warning about future compat, and somehow prevents ext2
# from being imported.
#EXT2_RESERVED_FL = 0x80000000   # reserved for ext2 implementation


class Stat( object ):
    def __init__( self, inode ):
        #self.st_dev = inode.
        self.st_ino = inode.number
        self.st_mode = inode.i_mode
        self.st_nlink = inode.i_links_count
        self.st_uid = inode.i_uid
        self.st_gid = inode.i_gid
        #self.st_rdev = inode.
        self.st_size = inode.i_size
        #self.st_blksize = inode.
        #self.st_blocks = inode.
        self.st_atime = inode.i_atime
        self.st_mtime = inode.i_mtime
        self.st_ctime = inode.i_ctime



class Superblock( object ):
    data_format = '< 7I i 5I 6H 4I 2H I 2H 3I 16s 16s 64s I 2B 2x 16s 3I 788x'
    def __init__( self, data ):
        '''create a superblock from a data string'''
        (
            self.s_inodes_count,        self.s_blocks_count,
            self.s_r_blocks_count,      self.s_free_blocks_count,
            self.s_free_inodes_count,   self.s_first_data_block,
            self.s_log_block_size,      self.s_log_frag_size,
            self.s_blocks_per_group,    self.s_frags_per_group,
            self.s_inodes_per_group,    self.s_mtime,
            self.s_wtime,               self.s_mnt_count,
            self.s_max_mnt_count,       self.s_magic,
            self.s_state,               self.s_errors,
            self.s_minor_rev_level,     self.s_lastcheck,
            self.s_checkinterval,       self.s_creator_os,
            self.s_rev_level,           self.s_def_resuid,
            self.s_def_resgid,
#   -- EXT2_DYNAMIC_REV Specific --,
            self.s_first_ino,           self.s_inode_size,
            self.s_block_group_nr,      self.s_feature_compat,
            self.s_feature_incompat,    self.s_feature_ro_compat,
            self.s_uuid,                self.s_volume_name,
            self.s_last_mounted,        self.s_algo_bitmap,
#   -- Performance Hints         --,
            self.s_prealloc_blocks,     self.s_prealloc_dir_blocks,
#   -- Journaling Support        --,
            self.s_journal_uuid,        self.s_journal_inum,
            self.s_journal_dev,         self.s_last_orphan
        ) = struct.unpack( self.data_format, data )


    def pack( self ):
        return struct.pack( self.data_format,
            self.s_inodes_count,        self.s_blocks_count,
            self.s_r_blocks_count,      self.s_free_blocks_count,
            self.s_free_inodes_count,   self.s_first_data_block,
            self.s_log_block_size,      self.s_log_frag_size,
            self.s_blocks_per_group,    self.s_frags_per_group,
            self.s_inodes_per_group,    self.s_mtime,
            self.s_wtime,               self.s_mnt_count,
            self.s_max_mnt_count,       self.s_magic,
            self.s_state,               self.s_errors,
            self.s_minor_rev_level,     self.s_lastcheck,
            self.s_checkinterval,       self.s_creator_os,
            self.s_rev_level,           self.s_def_resuid,
            self.s_def_resgid,
#   -- EXT2_DYNAMIC_REV Specific --,
            self.s_first_ino,           self.s_inode_size,
            self.s_block_group_nr,      self.s_feature_compat,
            self.s_feature_incompat,    self.s_feature_ro_compat,
            self.s_uuid,                self.s_volume_name,
            self.s_last_mounted,        self.s_algo_bitmap,
#   -- Performance Hints         --,
            self.s_prealloc_blocks,     self.s_prealloc_dir_blocks,
#   -- Journaling Support        --,
            self.s_journal_uuid,        self.s_journal_inum,
            self.s_journal_dev,         self.s_last_orphan
        )



class block_group( object ):
    data_format = '< 3I 3H 14x'
    def __init__( self, data ):
        '''create a block group descriptor from a data string'''
        (
            self.bg_block_bitmap,
            self.bg_inode_bitmap,
            self.bg_inode_table,
            self.bg_free_blocks_count,
            self.bg_free_inodes_count,
            self.bg_used_dirs_count
        ) = struct.unpack( self.data_format, data )


    def pack( self ):
        return struct.pack( self.data_format,
            self.bg_block_bitmap,
            self.bg_inode_bitmap,
            self.bg_inode_table,
            self.bg_free_blocks_count,
            self.bg_free_inodes_count,
            self.bg_used_dirs_count
        )



class Directory( vfs.Directory ):
    '''Represents an open directory.'''

    closed = True
    _entry_format = '< I H 2B'

    def __init__( self, node ):
        self._inode = node
        node._file_opened( self )
        self.closed = False


    def __iter__( self ):
        self.check_closed()
        return self._iterchildren( yield_details=False )


    def _iterchildren( self, yield_details=True ):
        '''Iterate over each child in this directory. Iff `yield_details` is
        True, also yield ext2 specific data, for internal use.'''

        self.check_closed()
        position = 0
        
        while True:
            if position >= self._inode.i_size:
                return
            dir = self._inode.read_bytes( position, 8 )
            (inode, rec_len, name_len, file_type) = struct.unpack( self._entry_format, dir )
            name = self._inode.read_bytes( position+8, name_len )
            if yield_details:
                yield (position, inode, rec_len, name_len, file_type, name)
            else:
                yield name
            if not rec_len:
                raise vfs.CorruptFSError( 'Invalid directory format' )
            position += rec_len


    def unlink( self, name ):
        self.check_closed()
        if self._inode.filesystem._readonly:
            raise vfs.PermissionError( 'filesystem is mounted read-only' )

        name = str(name)
        if '/' in name:
            raise vfs.InvalidNodeNameError( 'filename may not include "/": %r' % name )
        if name == '..' or name == '.':
            raise vfs.InvalidNodeNameError( 'can not unlink magic file %r' % name )

        previous = None
        for current in self._iterchildren():
            (position, inode_number, rec_len, _, _, entry_name) = current
            if entry_name == name:
                assert previous
                i = Node.from_number( inode_number, self._inode.filesystem )
                if i.i_mode & EXT2_S_IFDIR:
                    raise NotImplementedError( 'can not unlink directories yet' )
                (prev_position, _, prev_rec_len, _, _, _) = previous
                self._inode.write_bytes( prev_position + 4, struct.pack('<H', prev_rec_len + rec_len) )
                i._dec_link_count()
                #i.save_inode()
                return

            previous = current

        raise vfs.NoSuchNodeError( 'can not unlink %r, no such file or directory' % name )


    def link( self, inodes, name ):
        self.check_closed()
        if self._inode.filesystem._readonly:
            raise vfs.PermissionError( 'filesystem is mounted read-only' )

        if not inodes:
            return
        if len(inodes) != 1:
            raise vfs.FSLimitError( 'ext2 does not support nodes with identical names' )
        inode = inodes[0]
        name = str(name)
        if '/' in name:
            raise vfs.InvalidNodeNameError( 'filename may not include "/": %r' % name )

        def do_link():
            new_position = position + rec_len - free_space
            self._inode.write_bytes( new_position, struct.pack( self._entry_format,
                inode.number,
                free_space,
                len(name),
                i_mode_to_ft[inode.i_mode & EXT2_S_IFMT] ) )
            self._inode.write_bytes( new_position+8, name )

            self._inode.write_bytes( position+4, struct.pack('<H', rec_len-free_space) )
            inode._inc_link_count()
            #inode.save_inode()

        children = self._iterchildren()

        for (position, _, rec_len, name_len, _, entry_name) in children:
            if entry_name == name:
                raise vfs.InvalidNodeNameError( 'file already exists: %r' % name )
            free_space = rec_len - ((name_len+3)&-4) - 8
            if free_space < len(name) + 8:
                continue
            for (_, _, _, _, _, entry_name) in children:
                if entry_name == name:
                    raise vfs.InvalidNodeNameError( 'file already exists: %r' % name )
            do_link()
            return

        # extend the directory file
        self._inode.i_size += self._inode.block_size
        rec_len += self._inode.block_size
        free_space += self._inode.block_size
        do_link()
        #self._inode.save_inode()


    def close( self ):
        if not self.closed:
            self.closed = True
            self._inode._file_closed( self )


    def __del__( self ):
        self.close()
 
 

class File( vfs.File ):

    closed = True

    def __init__( self, node, read=False, write=False, append=False, truncate=False ):
        self._inode = node
        self._file_position = 0

        if write:
            if node.filesystem._readonly:
                raise vfs.PermissionError( 'filesystem is mounted read-only' )
            self.allow_write = True
        if read:
            self.allow_read = True
        if truncate:
            assert not node.filesystem._readonly
            node.truncate(0)
        if append:
            assert not node.filesystem._readonly
            self.always_append = True
            #self.seek( node.i_size )

        node._file_opened( self )
        self.closed = False


    def close( self ):
        if not self.closed:
            self.closed = True
            self._inode._file_closed( self )


    def seek( self, pos, whence=0 ):
        self.check_closed()
        if whence == 0:
            if pos < 0:
                raise IOError( 'can not seek to negative offset' )
            self._file_position = pos
        elif whence == 1:
            if self._file_position + pos < 0:
                raise IOError( 'can not seek to negative offset' )
            self._file_position += pos
        elif whence == 2:
            if self._inode.i_size + pos < 0:
                raise IOError( 'can not seek to negative offset' )
            self._file_position = self._inode.i_size + pos
        else:
            raise IOError( "invalid whence for seek" )


    def tell( self ):
        self.check_closed()
        return self._file_position


    def read( self, size = None ):
        self.check_closed()
        if not self.allow_read:
            raise vfs.PermissionError( 'file not opened for reading' )
        if size is None \
           or self._file_position + size > self._inode.i_size \
           or size == -1:
            size = self._inode.i_size - self._file_position

        r = self._inode.read_bytes( self._file_position, size )
        self._file_position += size
        return r


    def write( self, data ):
        self.check_closed()
        if not self.allow_write:
            raise vfs.PermissionError( 'file not opened for writing' )
        if self.always_append:
            self.seek( self._inode.i_size )
        if self._file_position + len(data) > self._inode.i_size:
            grow = self._file_position - self._inode.i_size
            if grow and self._inode.i_block[self._file_position/self._inode.block_size]:
                # if the file position is past the current size, and the
                # current last block is not already zero, fill the space with 0
                in_block = self._inode.block_size - (self._inode.i_size % self._inode.block_size)
                if in_block < grow:
                    grow = in_block
                if grow != self._inode.block_size:
                    # fill remainder of last block with zeros
                    assert grow < self._inode.block_size
                    self._inode.write_bytes( self._inode.i_size, chr(0) * grow )
            self._inode.i_size = self._file_position + len(data)
        self._inode.write_bytes( self._file_position, data )
        self._file_position += len(data)
        #self._inode.save_inode()
        return len(data)


    def stat( self ):
        self.check_closed()
        return Stat( self._inode )


    def __del__( self ):
        self.close()



class BlockList( object ):
    '''Represents the list of blocks a file occupies, abstracting the tree of
    indirect blocks to a flat sequence.'''

    def __init__( self, inode ):
        self.inode = inode
        self.i_block = inode.i_block


    class _folded_block_number( list ):
        '''This helps with the representation of block numbers. This is a list,
        with each element representing a level of indirection in the block list
        structure. The first element gives the element to read from the block
        list in the inode. The second gives the element within that, and so on,
        up to a maximum length of 4.'''

        def __init__( self, n, log_block_size ):
            '''Initialize. `n` is the linear block number to calculate, and
            `log_block_size` is s_log_block_size taken from the superblock.'''

            super( BlockList._folded_block_number, self ).__init__()
            base = 256 << log_block_size

            def build( n ):
                del self[:]

                if n < 12:
                    self.insert(0, n)
                    return

                n -= 12
                while n >= 0:
                    n, i = divmod( n, self.base )
                    self.insert( 0, i )
                    n -= 1
                if len(self) > 3:
                    raise vfs.FSLimitError( 'maximum file size exceeded' )
                self.insert( 0, 11 + len(self) )


            if n < 12:
                del self[:]
                self.insert(0, n)
                return

            n -= 12
            del self[:]
            while n >= 0:
                n, i = divmod( n, base )
                self.insert( 0, i )
                n -= 1
            if len(self) > 3:
                raise vfs.FSLimitError( 'maximum file size exceeded' )
            self.insert( 0, 11 + len(self) )


    def __getitem__( self, n ):
        '''Return the `n`th block of the file.'''

        n = int(n)

        l = self._folded_block_number( n, self.inode.filesystem._superblock.s_log_block_size )
        data = self.i_block
        for i in l[:-1]:
            block = struct.unpack( '<I', data[i*4:i*4+4] )[0]
            if not block: return 0
            data = self.inode.filesystem._read_block( block )
        i = l[-1]
        return struct.unpack( '<I', data[i*4:i*4+4] )[0]


    def __setitem__( self, n, value ):
        '''Set the `n`th block of the file to `value`.'''

        assert not self.inode.filesystem._readonly
        n = int(n)
        value = int(value)

        class c( object ):
            block = None
            data = self.i_block

        def set_and_save( n, value ):
            p = struct.pack( '<I', value )
            c.data = c.data[:n*4] + p + c.data[n*4+4:]
            if c.block:
                assert len(c.data) == self.inode.block_size
                self.inode.filesystem._write_block( c.block, c.data )
            else:
                assert len(c.data) == 15*4
                self.i_block = c.data

        l = self._folded_block_number( n, self.inode.filesystem._superblock.s_log_block_size )
        for i in l[:-1]:
            newblock = struct.unpack( '<I', c.data[i*4:i*4+4] )[0]
            if not newblock:
                newblock = self.inode._allocate_block()
                set_and_save( i, newblock )
                c.data = chr(0) * self.inode.block_size
            else:
                c.data = self.inode.filesystem._read_block( newblock )
            c.block = newblock

        i = l[-1]
        set_and_save( i, value )


    def truncate( self, blocks ):
        '''Truncate the block list to be `blocks` in length. All blocks
        truncated are freed.'''

        assert not self.inode.filesystem._readonly

        def free_block_branch( n, depth ):
            '''Free a block, and all the blocks referenced by it. Depth
            indicates the number of generations in the branch. If it is zero,
            the block is simply freed. If one, each block number in the block
            is first freed, then the block itself is freed. Etc.'''

            if n == 0:
                # block 0 is magic, it shouldn't be freed.
                return
            if depth:
                data = self.inode.filesystem._read_block( n )
                for i in xrange( 0, self.inode.block_size, 4 ):
                    free_block_branch( struct.unpack('<I', data[i:i+4])[0], depth-1 )
            self.inode.free_block( n )

        # we want the position of the last block, *inclusive*
        position = self._folded_block_number( blocks-1, self.inode.filesystem._superblock.s_log_block_size )

        data = [self.i_block]
        data_blocks = []
        for i in position[:-1]:
            block = struct.unpack('<I', data[-1][i*4:i*4+4])[0]
            data_blocks.append(block)
            data.append( self.inode.filesystem._read_block( block ) )

        assert len(position) == len(data)

        for depth in xrange( len(data)-1 ):
            start = position.pop()+1
            block = data_blocks.pop()
            datum = data.pop()
            for i in xrange( start*4, self.inode.block_size, 4 ):
                free_block_branch( struct.unpack('<I', datum[i:i+4])[0], depth )
            self.inode.filesystem._write_block( block, datum[:start*4] + chr(0) * (self.inode.block_size-(start*4)) )

        start = position.pop()+1
        datum = data.pop()
        for i in xrange( start*4, 12*4, 4 ):
            free_block_branch( struct.unpack('<I', datum[i:i+4])[0], 0 )
        if start < 13:
            free_block_branch( struct.unpack('<I', datum[12*4:12*4+4])[0], 1 )
        if start < 14:
            free_block_branch( struct.unpack('<I', datum[13*4:13*4+4])[0], 2 )
        if start < 15:
            free_block_branch( struct.unpack('<I', datum[14*4:14*4+4])[0], 3 )
        self.i_block = self.i_block[:start*4] + chr(0) * ((15-start) * 4)



class Node( BlockDevice, vfs.Node ):
    '''Represents an inode and associated data on disk.'''

    data_format = '< 2H 5I 2H 3I 60s 4I 12s'

    def from_number( number, root ):
        '''Return an existing inode by its number.'''
        try:
            return root._inode_number_cache[number]
        except KeyError:
            pass

        n = Node( number, root )
        n._init_from_number()
        return n

    from_number = staticmethod( from_number )


    def allocate_new( root,
        mode_type=EXT2_S_IFREG,
        mode_perms=0666,
        uid=0,
        gid=0,
        flags=0 ):
        '''Get a new `Node` instance by allocating a new inode.'''
        number = root._allocate_inode()
        self = Node( number, root )
        self.i_mode = mode_type | mode_perms
        self.i_uid = uid
        self.i_size = 0
        self.i_atime = 0
        self.i_ctime = 0
        self.i_mtime = 0
        self.i_dtime = 0
        self.i_gid = 0
        self.i_links_count = 0
        self.i_blocks = 0
        self.i_flags = flags
        self.i_osd1 = 0
        self.i_block = chr(0) * 15 * 4
        self.i_generation = 0
        self.i_file_acl = 0
        self.i_dir_acl = 0
        self.i_faddr = 0
        self.i_osd2 = chr(0) * 12

        self.i_block = BlockList( self )
        return self

    allocate_new = staticmethod( allocate_new )


    def __init__( self, number, root ):
        '''Do not use. See `from_number` or `allocate_new` instead.'''
        self.number = number
        self.filesystem = root
        self._preallocated_blocks = []
        self.__open_count = 0    # number of File classes open on this inode
        self.block_size = 1024 << root._superblock.s_log_block_size
        assert number not in root._inode_number_cache
        root._inode_number_cache[number] = self


    def __del__( self ):
        # TODO: make _inode_number_cache use weak refs, so that this might be called
        if getattr( self, 'i_links_count', None ) == 0:
            self._free()


    def create_regular_child( self, name, mode=0666 ):
        if self.filesystem._readonly:
            raise vfs.PermissionError( 'filesystem is mounted read-only' )
        if not self.i_mode & EXT2_S_IFDIR:
            raise vfs.FSLimitError( 'ext2 does not support children in non-directories' )
        node = Node.allocate_new( self.filesystem, mode_perms=mode )
        dir = self.opendir()
        try:
            dir.link( [node], name )
        finally:
            dir.close()
        return node


    def _inc_link_count( self ):
        '''Increment the link count.'''
        self.i_links_count += 1


    def _dec_link_count( self ):
        '''Decrement the link count. If the resulting count is zero, this inode
        is freed. WARNING: once the link count is decremented to zero, the
        inode is invalid. Further use will almost surely result in filesystem
        corruption.'''
        self.i_links_count -= 1
        if self.i_links_count:
            return
        # TODO: set dtime
        self._free()


    def _free( self ):
        assert not self.filesystem._readonly
        if hasattr(self,'number'):
            self.filesystem._free_inode( self.number )
            self.i_dtime = 1086688456 # TODO: use a real time
            self.i_block.truncate(0)
            self._free_preallocated_blocks()
            self.save_inode()
            del self.filesystem._inode_number_cache[self.number]
            del self.number


    def _init_from_number( self ):
        '''Use from_number(), not this, unless inheriting from `Node`. In that
        case, a Node for `number` must not have been created previously, and
        __init__ must be called first.'''
        (
            self.i_mode,
            self.i_uid,
            self.i_size,
            self.i_atime,
            self.i_ctime,
            self.i_mtime,
            self.i_dtime,
            self.i_gid,
            self.i_links_count,
            self.i_blocks,
            self.i_flags,
            self.i_osd1,
            self.i_block,
            self.i_generation,
            self.i_file_acl,
            self.i_dir_acl,
            self.i_faddr,
            self.i_osd2
        ) = struct.unpack( self.data_format, self.filesystem._get_inode_data(self.number) )

        self.i_block = BlockList( self )


    def _allocate_block( self ):
        '''Allocate and return a block for use by this inode.'''
        assert not self.filesystem._readonly
        if not self._preallocated_blocks:
            self._preallocated_blocks.extend( self.filesystem._allocate_blocks(1, self) )
            # _allocate_blocks should fail if it can't get at least 1
        b = self._preallocated_blocks[0]
        del self._preallocated_blocks[0]
        self.i_blocks += self.filesystem._sectors_per_block
        return b


    def free_block( self, block ):
        '''Free a block by putting it back in the list of preallocated blocks.
        It will later be freed completely when there is an excess of
        preallocated blocks, or all files for this inode are closed.'''

        assert not self.filesystem._readonly
        self.i_blocks -= self.filesystem._sectors_per_block
        self._preallocated_blocks.insert( 0, block )


    def save_inode( self ):
        '''Write self to disk.'''
        if self.filesystem._readonly:
            return

        if not hasattr( self, 'number' ):
            # if we don't have number, we don't exist on disk.
            return
        data = struct.pack( self.data_format,
            self.i_mode,
            self.i_uid,
            self.i_size,
            self.i_atime,
            self.i_ctime,
            self.i_mtime,
            self.i_dtime,
            self.i_gid,
            self.i_links_count,
            self.i_blocks,
            self.i_flags,
            self.i_osd1,
            self.i_block.i_block,
            self.i_generation,
            self.i_file_acl,
            self.i_dir_acl,
            self.i_faddr,
            self.i_osd2
        )
        self.filesystem._save_inode_data( self.number, data )


    def truncate( self, size ):
        '''Truncate the file to be at most `size` bytes in length. If `size` is
        larger than the file, the file is unchanged; see `extend` to handle
        that case.'''

        if self.filesystem._readonly:
            raise vfs.PermissionError( 'filesystem is mounted read-only' )
        if size >= self.i_size:
            return

        self.i_block.truncate( (size+self.block_size-1)/self.block_size )
        self.i_size = size
        self.save_inode()


    def _trim_preallocated_blocks( self ):
        '''Free any excess preallocated blocks.'''
        self.filesystem._free_blocks( self._preallocated_blocks[8:] )
        del self._preallocated_blocks[8:]


    def _free_preallocated_blocks( self ):
        self.filesystem._free_blocks( self._preallocated_blocks )
        del self._preallocated_blocks[:]


    def _file_opened( self, file ):
        self.__open_count += 1
        self._inc_link_count()


    def _file_closed( self, file ):
        '''Called each time a file of this node is closed. When no
        files reference this node, free all preallocated blocks. `file`
        is the file in the process of being closed.'''
        assert self.__open_count > 0
        self.__open_count -= 1
        if not self.__open_count:
            self._free_preallocated_blocks()
        else:
            self._trim_preallocated_blocks()
        self._dec_link_count()
        self.save_inode()


    def __getitem__( self, name ):
        if not self.i_mode & EXT2_S_IFDIR:
            raise vfs.NoSuchNodeError( 'invalid attempt to get child of non-directory' )

        position = 0
        
        while True:
            if position >= self.i_size:
                raise vfs.NoSuchNodeError( 'node does not exist' )
            dir = self.read_bytes( position, 8 )
            (inode, rec_len, name_len, file_type) = struct.unpack( '< I H 2B', dir )
            if name_len == len(name) and self.read_bytes( position+8, name_len ) == name:
                return [Node.from_number(inode, self.filesystem)]
            if not rec_len:
                raise vfs.CorruptFSError( 'invalid directory format' )
            position += rec_len


    def open( self, read=False, write=False, append=False, truncate=False ):
        '''Open this node and return a File instance.'''
        if (self.i_mode & EXT2_S_IFMT) == EXT2_S_IFDIR:
            raise vfs.FSLimitError( 'ext2 can not open directories' )
        if (self.i_mode & EXT2_S_IFMT) != EXT2_S_IFREG:
            raise NotImplementedError( 'support for non-regular files not yet written' )
        return File( self, read=read, write=write, append=append, truncate=truncate )


    def opendir( self ):
        '''Open this node and return a Directory instance.'''
        if not self.i_mode & EXT2_S_IFDIR:
            raise vfs.FSLimitError( 'ext2 does not support children in non-directories' )
        return Directory( self )


    def stat( self ):
        return Stat( self )


    def _size_in_fs_blocks( self ):
        return ( self.i_size + self.block_size - 1 ) / self.block_size


    def read_sectors( self, first, count ):
        '''Actually, read blocks, as if this were a block device.'''
        if first+count > self._size_in_fs_blocks() or first < 0 or count < 0:
            raise vfs.CorruptFSError( 'request for blocks beyond file boundries' )

        return ''.join( [
            self.filesystem._read_block( self.i_block[x] )
            for x in xrange( first, first+count )
            ] )


    def write_sectors( self, first, data ):
        '''Actually, write blocks, as if this were a block device.'''

        if self.filesystem._readonly:
            raise vfs.PermissionError( 'filesystem is mounted read-only' )

        assert not len(data) % self.block_size
        assert first + len(data) / self.block_size <= self._size_in_fs_blocks()

        for block in xrange( len(data)/self.block_size ):
            data_off = self.block_size * block
            if not self.i_block[first+block]:
                self.i_block[first+block] = self._allocate_block()
            self.filesystem._write_block( self.i_block[first+block], data[data_off:data_off+self.block_size] )
        self.i_generation += 1



class BitMap( object ):

    def __init__( self, sector_size, initializer ):
        tail = len(initializer) % sector_size
        if tail:
            initializer += chr(255) * (sector_size-tail)
        self.array = array.array( 'B', initializer )
        self.dirty_sectors = {}
        self.sector_size = sector_size

    def allocate_bits( self, count, start=0 ):
        '''Try to allocate exactly `count` bits and return them in a list. If
        no bits, or fewer than `count` bits are found, the found bits are still
        marked as allocated and returned in a list. Using `allocate_bit_chunks`
        is preferable as it allocates in chunks of 8 which reduces
        fragmentation.'''

        bits = []
        for i in xrange( (start+7) / 8, len(self.array) ):
            if self.array[i] == 0xff:
                continue
            for j in xrange( 8 ):
                if not self.array[i] & (1<<j):
                    self.dirty_sectors[i/self.sector_size] = None
                    self.array[i] = self.array[i] | (1<<j)
                    bits.append( i*8 + j + 1 )
                    if len(bits) >= count:
                        return bits
        return bits


    def allocate_bit_chunks( self, count, start=0 ):
        '''Try to allocate at least `count` bits and return them in a list.
        This works by scanning for a byte marked 0, marking it as 1, and
        returning a list of the address of each bit in that byte. If at least
        `count` bits can't be found, the list of bits that were found are
        returned, which may be of zero length. It might be possible to find
        more bits in the bitmap with `allocate_bit`.'''

        bits = []
        for i in xrange( (start+7) / 8, len(self.array) ):
            if self.array[i] == 0:
                self.dirty_sectors[i/self.sector_size] = None
                self.array[i] = 0xff
                bits.extend( xrange( i*8+1, i*8+9 ) )
                if len(bits) >= count:
                    return bits
        return bits


    def mark_bit( self, bit, state ):
        '''Mark one bit with a given state.'''

        bit -= 1
        byte = bit / 8
        bit %= 8

        self.dirty_sectors[byte/self.sector_size] = None
        if state:
            self.array[byte] |= 1 << bit
        else:
            self.array[byte] &= ~(1 << bit)


    def read_bit( self, bit ):
        bit -= 1
        byte = bit / 8
        bit %= 8
        return bool( self.array[byte] & (1<<bit) )


    def save_bitmap( self, start_sector, disk ):
        '''Save self to disk. `start_sector` is the block on `disk`
        coresponding to the start of the bitmap. Note that data is written
        blockwise, so if the bitmap isn't a multiple of the disk block size in
        length, the data at the end of the block will be lost.'''

        for sector in self.dirty_sectors:
            slice = self.array[ sector * self.sector_size : (sector+1) * self.sector_size ]
            disk.write_sectors( start_sector + sector, slice.tostring() )
        self.dirty_sectors.clear()



class FileSystem( Node ):

    _readonly = False

    def __init__( self, device, options=None ):
        if options is not None:
            options = [option.strip() for option in options.split(',')]
            for option in options:
                if option == 'ro':
                    self._readonly = True
                else:
                    raise ValueError( 'unknown ext2 mount option %r' % option )
        import uuu
        self._inode_number_cache = {}
        self.disk = uuu.root_vfs.open( device, read=True, write=not self._readonly )
        self._superblock = Superblock( self.disk.read_sectors(2, 2) )
        if self._superblock.s_magic != EXT2_MAGIC:
            raise vfs.CorruptFSError( "not an ext2 filesystem: invalid magic" )
        if self._superblock.s_rev_level != EXT2_DYNAMIC_REV:
            raise vfs.CorruptFSError( "unsupported ext2 version" )
        if self._superblock.s_state != EXT2_VALID_FS:
            raise vfs.FSDirtyError( "filesystem was not cleanly unmounted" )

        self._sectors_per_block = 2 << self._superblock.s_log_block_size

        self._groups_count = self._superblock.s_blocks_count / self._superblock.s_blocks_per_group
        if self._superblock.s_blocks_count % self._superblock.s_blocks_per_group:
            self._groups_count += 1
        group_data = self.disk.read_sectors(
                (self._superblock.s_first_data_block + 1) * self._sectors_per_block,
                self._groups_count * 32 / 512 + 1 )
        self._group_descriptors = []
        self._block_bitmaps = []
        self._inode_bitmaps = []
        for i in xrange( 0, self._groups_count ):
            bg = block_group(group_data[i*32:i*32+32])
            self._group_descriptors.append( bg )
            assert not self._superblock.s_inodes_per_group % 8
            assert not self._superblock.s_frags_per_group % 8
            s = BitMap(
                self.disk.block_size,
                self.disk.read_bytes(
                    bg.bg_block_bitmap * self._sectors_per_block * self.disk.block_size,
                    self._superblock.s_frags_per_group / 8
            ))
            self._block_bitmaps.append( s )
            self._inode_bitmaps.append( BitMap( self.disk.block_size, self.disk.read_bytes(
                    bg.bg_inode_bitmap * self._sectors_per_block * self.disk.block_size,
                    self._superblock.s_inodes_per_group / 8 )))
        assert len(self._group_descriptors) == self._groups_count

        super( FileSystem, self ).__init__( EXT2_ROOT_INO, self )
        super( FileSystem, self )._init_from_number()


    def _flush_block_bitmaps( self ):
        if self._readonly:
            return
        for group in xrange( 0, self._groups_count ):
            self._block_bitmaps[group].save_bitmap(
                self._group_descriptors[group].bg_block_bitmap * self._sectors_per_block,
                self.disk )


    def _flush_inode_bitmaps( self ):
        if self._readonly:
            return
        for group in xrange( 0, self._groups_count ):
            self._inode_bitmaps[group].save_bitmap(
                self._group_descriptors[group].bg_inode_bitmap * self._sectors_per_block,
                self.disk )


    def _get_inode_data( self, i ):
        '''Get the raw inode data given an inode number. TODO: rewrite to use
        read_bytes'''

        isize = self._superblock.s_inode_size

        group = (i - 1) / self._superblock.s_inodes_per_group
        index = (i - 1) % self._superblock.s_inodes_per_group
        sector = self._group_descriptors[group].bg_inode_table * self._sectors_per_block + (index * isize / 512)
        offset = index % (512/isize)
        data = self.disk.read_sectors( sector, 1 )

        return data[offset*isize:offset*isize+128]


    def _save_inode_data( self, i, data ):
        '''Save the raw inode data for inode `i`.'''

        group = (i - 1) / self._superblock.s_inodes_per_group
        index = (i - 1) % self._superblock.s_inodes_per_group
        offset = (self._group_descriptors[group].bg_inode_table
                * self._sectors_per_block
                * self.disk.block_size
                + index * self._superblock.s_inode_size )
        sector_data = self.disk.write_bytes( offset, data )


    def _read_block( self, block ):
        if block:
            return self.disk.read_sectors( block*self._sectors_per_block, self._sectors_per_block )
        else:
            return chr(0) * (1024 << self._superblock.s_log_block_size)


    def _write_block( self, block, data ):
        if self._readonly:
            raise vfs.PermissionError( 'filesystem is mounted read-only' )
        if not block:
            raise ValueError( 'attempt to write to block 0' )
        if len(data) != self._sectors_per_block * self.disk.block_size:
            raise ValueError( 'data must be exactly one block long' )
        self.disk.write_sectors( block*self._sectors_per_block, data )


    def _allocate_inode( self ):
        if self._readonly:
            raise vfs.PermissionError( 'filesystem is mounted read-only' )
        for group in xrange( self._groups_count ):
            inode = self._inode_bitmaps[group].allocate_bits( 1 )
            if inode:
                self._group_descriptors[group].bg_free_inodes_count -= 1
                self._superblock.s_free_inodes_count -= 1
                self._flush_inode_bitmaps()
                self.save_superblock()
                return inode[0] + group * self._superblock.s_inodes_per_group
        raise vfs.FSFullError( 'no free inodes' )


    def _free_inode( self, inode_number ):
        if self._readonly:
            raise vfs.PermissionError( 'filesystem is mounted read-only' )
        ( group, offset ) = divmod( inode_number, self._superblock.s_inodes_per_group )
        self._inode_bitmaps[group].mark_bit( offset, False )
        self._group_descriptors[group].bg_free_inodes_count += 1
        self._superblock.s_free_inodes_count += 1
        self._flush_inode_bitmaps()
        self.save_superblock()


    def _allocate_blocks( self, count, inode ):
        '''Allocate at least `count` blocks for `inode` and return them
        in a list. More than `count` blocks will usually be allocated
        due to preallocation to reduce fragmentation. The `inode`
        parameter is used to try to allocate the blocks in the same
        group as the inode.'''

        if self._readonly:
            raise vfs.PermissionError( 'filesystem is mounted read-only' )
        group = inode.number / self._superblock.s_inodes_per_group
        blocks = []
        grouplist = [group] + range(group) + range(group+1, self._groups_count)

        for group in grouplist:
            new_blocks = self._block_bitmaps[group].allocate_bit_chunks( count )
            self._group_descriptors[group].bg_free_blocks_count -= len(new_blocks)
            self._superblock.s_free_blocks_count -= len(new_blocks)
            blocks.extend(
                [ x + self._superblock.s_blocks_per_group * group
                for x in new_blocks ] )
            if len(blocks) >= count:
                self._flush_block_bitmaps()
                self.save_superblock()
                return blocks

        # can't get them in chunks; resort to individual bits
        for group in grouplist:
            new_blocks = self._block_bitmaps[group].allocate_bits( count )
            self._group_descriptors[group].bg_free_blocks_count -= len(new_blocks)
            self._superblock.s_free_blocks_count -= len(new_blocks)
            blocks.extend(
                [ x + self._superblock.s_frags_per_group * group
                for x in new_blocks ] )
            if len(blocks) >= count:
                self._flush_block_bitmaps()
                self.save_superblock()
                return blocks

        # TODO: release allocated blocks
        raise vfs.FSFullError( 'no space left on device' )


    def _free_blocks( self, blocks ):
        '''Mark all block numbers in iterable `blocks` as free.'''

        if not blocks:
            return
        if self._readonly:
            raise vfs.PermissionError( 'filesystem is mounted read-only' )
        self._superblock.s_free_blocks_count += len(blocks)

        for block in blocks:
            group = block / self._superblock.s_frags_per_group
            self._group_descriptors[group].bg_free_blocks_count += 1
            block %= self._superblock.s_frags_per_group
            self._block_bitmaps[group].mark_bit( block, False )

        self._flush_block_bitmaps()
        self.save_superblock()


    def save_superblock( self ):
        '''Save the superblock and group descriptor structures to disk.'''

        if self._readonly:
            return
        self.disk.write_sectors( 2, self._superblock.pack() )

        gd_data = ''.join([x.pack() for x in self._group_descriptors])
        gd_data += chr(0) * (self.disk.block_size - (len(gd_data) % self.disk.block_size))
        self.disk.write_sectors(
            (self._superblock.s_first_data_block + 1) * self._sectors_per_block,
            gd_data )



vfs.register_fs( 'ext2', FileSystem )
