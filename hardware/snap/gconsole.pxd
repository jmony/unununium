from ga cimport GA_devCtx

cdef extern from "gconsole.h":
    ctypedef struct GC_devCtx:
        int attr

    ctypedef enum GC_FONT_TYPES:
        GC_FONT_8X8 = 1
        GC_FONT_8X14
        GC_FONT_8X16

    ctypedef enum GC_WRAP_MODES:
        GC_NO_WRAP
        GC_LINE_WRAP
        GC_WORD_WRAP

    ctypedef enum GC_CURSOR_TYPES:
        GC_CURSOR_NORMAL
        GC_CURSOR_FULL

    GC_devCtx * GC_createExt( GA_devCtx *dc, int xchars, int ychars, int fontType, int bitsPerPixel )
    void GC_leave( GC_devCtx *gc )
    void GC_restore( GC_devCtx *gc )
    void GC_destroy( GC_devCtx *gc )
    void GC_heartBeat( GC_devCtx *gc )
    void GC_setLineWrap( GC_devCtx *gc, int mode )
    void GC_puts( GC_devCtx *gc, char *str )
    void GC_write( GC_devCtx *gc, int x, int y, int attr, char *str )
    void GC_clreol( GC_devCtx *gc )
    void GC_clrscr( GC_devCtx *gc )
    void GC_gotoxy( GC_devCtx *gc, int x, int y )
    int GC_wherex( GC_devCtx *gc )
    int GC_wherey( GC_devCtx *gc )
    void GC_delline( GC_devCtx *gc )
    void GC_insline( GC_devCtx *gc )
    void GC_moveText( GC_devCtx *gc, int left, int top, int right, int bottom, int destleft, int desttop )
#    int GC_bufSize( GC_devCtx *gc, int width, int height )
#    void GC_saveText( GC_devCtx *gc, int left, int top, int right, int bottom, void *dest )
#    void GC_restoreText( GC_devCtx *gc, int left, int top, int right, int bottom, void *source )
    void GC_scroll( GC_devCtx *gc, int direction, int amt )
    void GC_fillText( GC_devCtx *gc, int left, int top, int right, int bottom, int attr, int ch )
    void GC_fillAttr( GC_devCtx *gc, int left, int top, int right, int bottom, int attr )
    void GC_setWindow( GC_devCtx *gc, int left, int top, int right, int bottom )
    void GC_getWindow( GC_devCtx *gc, int *left, int *top, int *right, int *bottom )
    int GC_maxx( GC_devCtx *gc )
    int GC_maxy( GC_devCtx *gc )
    int GC_getAttr( GC_devCtx *gc )
    void GC_setAttr( GC_devCtx *gc, int attr )
    void GC_setBackground( GC_devCtx *gc, int attr, int ch )
    void GC_getBackground( GC_devCtx *gc, int *attr, int *ch )
    void GC_setForeColor( GC_devCtx *gc, int newcolor )
    void GC_setBackColor( GC_devCtx *gc, int newcolor )
    void GC_setCursor( GC_devCtx *gc, int type )
    void GC_cursorOff( GC_devCtx *gc )
    void GC_restoreCursor( GC_devCtx *gc, int scans )
    int GC_getCursor( GC_devCtx *gc )
    int GC_screenWidth( GC_devCtx *gc )
    int GC_screenHeight( GC_devCtx *gc )

cdef class Console:
    cdef GC_devCtx *_context
