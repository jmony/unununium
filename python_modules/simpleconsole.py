import vfs
import keyboard
import io

class Console( vfs.Node ):

    _position = 0
    _vram = 0xb8000
    width = 80
    height = 25

    def open( self, read=False, write=False, append=False, truncate=False ):
        return ConsoleFile( self, read=read, write=write )


    def clreol( self ):
        '''Clear from the cursor position to end of line, inclusive'''
        io.string_to_mem(
            self._vram + self._position * 2,
            (' '+chr(0x07)) * (self.width - self._position % self.width) )


    def puts( self, data ):
        for c in data:
            if self._position >= self.width * self.height:
                io.mem_to_mem(
                    self._vram,
                    self._vram + self.width * 2,
                    self.width * (self.height-1) * 2 )
                self._position = self.width * (self.height-1)
                self.clreol()
            if c == '\n':
                self._position += self.width
                self._position -= self._position % self.width
            elif c == '\b':
                self._position -= 1
                io.string_to_mem( self._vram + self._position * 2, ' ' + chr(0x07) )
            else:
                io.string_to_mem( self._vram + self._position * 2, c + chr(0x07) )
                self._position += 1
        io.outw( 0x3d4, 0x0e + (self._position & 0xff00) )
        io.outw( 0x3d4, 0x0f + ((self._position & 0xff) << 8) )



class ConsoleFile( vfs.File ):

    def __init__( self, console, read, write ):
        self._console = console

        if write:
            self.allow_write = True
        if read:
            self.allow_read = True


    def read( self, size=None ):
        r = ''
        while len(r) < size or size is None:
            key = keyboard.get_key()
            if key == '\b':
                if len(r):
                    r = r[:-1]
                    self._console.puts( key )
                continue
            if key == '\r':
                key = '\n'
            self._console.puts( key )
            r += key
            if key == '\n':
                break
        return r


    def write( self, data ):
        self._console.puts( data )
        return len(data)


    def stat( self, data ):
        return Stat()



class Stat( object ):
    def __init__( self, inode ):
        #self.st_dev = inode.
        #self.st_ino = inode.number
        self.st_mode = 0020000
        self.st_nlink = 1
        self.st_uid = 0
        self.st_gid = 0
        #self.st_rdev = inode.
        self.st_size = 0
        #self.st_blksize = inode.
        #self.st_blocks = inode.
        self.st_atime = 1234
        self.st_mtime = 1234
        self.st_ctime = 1234
