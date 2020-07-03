import ga
import gconsole
import keyboard
import uuu
import vfs

class Console( vfs.Node, gconsole.Console ):

    def __init__( self, xchars=80, ychars=25, fontType=gconsole.font_8x8, bitsPerPixel=0 ):
        self._driver = ga.Driver()
        gconsole.Console.__init__( self, self._driver, xchars, ychars, fontType, bitsPerPixel )
        pass


    def open( self, read=False, write=False, append=False, truncate=False ):
        return ConsoleFile( self, read=read, write=write )



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
