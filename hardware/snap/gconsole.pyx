cimport common
cimport ga

font_8x8 = GC_FONT_8X8
font_8x14 = GC_FONT_8X14
font_8x16 = GC_FONT_8X16

cdef class Console:

    def __init__( self, ga.Driver deviceContext, xchars=80, ychars=25, fontType=GC_FONT_8X8, bitsPerPixel=0 ):
        if deviceContext is None:
            pass #raise TypeError( 'deviceContext must not be None' )
            # raising an exception here leads to multiple definitions
            # of __pyx_k6 in the generated C code. A bug report has
            # been submitted to the pyrex ML. <indigo@unununium.org>
            # 2004-06-19
        self._context = GC_createExt( deviceContext._context, xchars, ychars, fontType, bitsPerPixel )

    def leave( self ):
        GC_leave( self._context )

    def restore( self ):
        GC_restore( self._context )

    def __del__( self ):
        GC_destroy( self._context )

    def heartBeat( self ):
        GC_heartBeat( self._context )

    def setLineWrap( self, int mode ):
        GC_setLineWrap( self._context, mode )

    def puts( self, char *str ):
        GC_puts( self._context, str )

    def write( self, int x, int y, char *str, int attr = 0x07 ):
        GC_write( self._context, x, y, attr, str )

    def clreol( self ):
        GC_clreol( self._context )

    def clrscr( self ):
        GC_clrscr( self._context )

    def gotoxy( self, int x, int y ):
        GC_gotoxy( self._context, x, y )

    def wherex( self ):
        return GC_wherex( self._context )

    def wherey( self ):
        return GC_wherey( self._context )

    def delline( self ):
        GC_delline( self._context )

    def insline( self ):
        GC_insline( self._context )

    def moveText( self, int left, int top, int right, int bottom, int destleft, int desttop ):
        GC_moveText( self._context, left, top, right, bottom, destleft, desttop )

    # GC_bufSize GC_saveText GC_restoreText unimplemented

    def scroll( self, int direction, int amount ):
        GC_scroll( self._context, direction, amount )

    def fillText( self, int left, int top, int right, int bottom, int attr, int ch ):
        GC_fillText( self._context, left, top, right, bottom, attr, ch )

    def fillAttr( self, int left, int top, int right, int bottom, int attr ):
        GC_fillAttr( self._context, left, top, right, bottom, attr )

    def setWindow( self, int left, int top, int right, int bottom ):
        GC_setWindow( self._context, left, top, right, bottom )

    def getWindow( self ):
        cdef int left, top, right, bottom
        GC_getWindow( self._context, &left, &top, &right, &bottom )
        return left, top, right, bottom

    def maxx( self ):
        return GC_maxx( self._context )

    def maxy( self ):
        return GC_maxy( self._context )

    def getAttr( self ):
        return GC_getAttr( self._context )

    def setAttr( self, int attr ):
        GC_setAttr( self._context, attr )

    def setBackground( self, int attr, int ch ):
        GC_setBackground( self._context, attr, ch )

    def getBackground( self ):
        cdef int attr, ch
        GC_getBackground( self._context, &attr, &ch )
        return attr, ch

    def setForeColor( self, int newcolor ):
        GC_setForeColor( self._context, newcolor )

    def setBackColor( self, int newcolor ):
        GC_setBackColor( self._context, newcolor )

    def setCursor( self, int type ):
        GC_setCursor( self._context, type )

    def cursorOff( self ):
        GC_cursorOff( self._context )

    def restoreCursor( self, int scans ):
        GC_restoreCursor( self._context, scans )

    def getCursor( self ):
        return GC_getCursor( self._context )

    def screenWidth( self ):
        return GC_screenWidth( self._context )

    def screenHeight( self ):
        return GC_screenHeight( self._context )
