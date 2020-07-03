cimport common

cdef void checkSupported( void *ptr ):
    if ptr == NULL:
        raise Exception( 'function not supported' )

cdef class Driver:

    def __init__( self, deviceIndex=0, shared=0 ):
        self._context = GA_loadDriver(deviceIndex, shared)
        if self._context == NULL:
            raise Exception( 'could not load graphics driver: %s' % GA_errorMsg(GA_status()) )

        self.AvailableModes = []
        cdef int i
        i = 0
        while self._context.AvailableModes[i] != 0xffff:
            self.AvailableModes.append( self._context.AvailableModes[i] )
            i = i+1

    def __del__( self ):
        GA_unloadDriver( self._context )

    property version:
        def __get__( self ):
            return self._context.Version >> 8, self._context.Version & 0xFF

    property driverRev:
        def __get__( self ): return self._context.DriverRev

    property oemVendorName:
        def __get__( self ): return self._context.OemVendorName

    property oemCopyright:
        def __get__( self ): return self._context.OemCopyright

    property deviceIndex:
        def __get__( self ): return self._context.DeviceIndex

    property totalMemory:
        def __get__( self ): return self._context.TotalMemory

    property attributes:
        def __get__( self ): return self._context.Attributes

    property workArounds:
        def __get__( self ): return self._context.WorkArounds

    property textSize:
        def __get__( self ): return self._context.TextSize

    property textBasePtr:
        def __get__( self ): return self._context.TextBasePtr

    property bankSize:
        def __get__( self ): return self._context.BankSize

    property bankedBasePtr:
        def __get__( self ): return self._context.BankedBasePtr

    property linearSize:
        def __get__( self ): return self._context.LinearSize

    property linearBasePtr:
        def __get__( self ): return self._context.LinearBasePtr

    property zBufferSize:
        def __get__( self ): return self._context.ZBufferSize

    property zBufferBasePtr:
        def __get__( self ): return self._context.ZBufferBasePtr

    property texBufferSize:
        def __get__( self ): return self._context.TexBufferSize

    property texBufferBasePtr:
        def __get__( self ): return self._context.TexBufferBasePtr

    property lockedMemSize:
        def __get__( self ): return self._context.LockedMemSize

    property IOBase:
        def __get__( self ): return self._context.IOBase

    #N_uint32        MMIOBase[4]
    #N_uint32        MMIOLen[4]

    property driverStart:
        def __get__( self ): return <unsigned>self._context.DriverStart

    property driverSize:
        def __get__( self ): return self._context.DriverSize

    property busType:
        def __get__( self ): return self._context.BusType

    property attributesExt:
        def __get__( self ): return self._context.AttributesExt

    property shared:
        def __get__( self ): return bool(self._context.Shared)



cdef class InitFuncs:

    def __init__( self, Driver driver ):
        self._funcs.dwSize = sizeof( self._funcs )
        if not GA_queryFunctions( driver._context, GA_GET_INITFUNCS, &self._funcs ):
            raise Exception( 'unable to get InitFuncs for driver' )

    def getConfigInfo( self ):
        return ConfigInfo( self )

    def getVideoModeInfo( self, int mode=-1 ):
        return ModeInfo( self, mode )

    def setVideoMode( self,
                      N_uint32 mode,
                      N_int32 virtualX = -1,
                      N_int32 virtualY = -1,
                      N_int32 refreshRate = 0,
                      dontClear = False,
                      linearBuffer = False,
                      sixBitDAC = False,
                      noAccel = False,
                      windowedMode = False,
                      partialModeSet = False ):
        # crtc parameter unimplemented
        checkSupported( self._funcs.SetVideoMode )
        cdef N_int32 bytesPerLine, maxMem
        if dontClear: mode = mode | gaDontClear
        if linearBuffer: mode = mode | gaLinearBuffer
        if sixBitDAC: mode = mode | ga6BitDAC
        if noAccel: mode = mode | gaNoAccel
        if windowedMode: mode = mode | gaWindowedMode
        if partialModeSet: mode = mode | gaPartialModeSet
        if self._funcs.SetVideoMode( mode, &virtualX, &virtualY, &bytesPerLine, &maxMem, refreshRate, NULL ):
            raise Exception( 'could not set video mode %i' % (mode & gaModeMask)  )
        return virtualX, virtualY, bytesPerLine, maxMem



cdef class ModeInfo:

    def __init__( self, InitFuncs initfuncs, int mode=-1 ):
        # TODO: validate mode?
        self._info.dwSize = sizeof( self._info )
        if mode != -1:
            checkSupported( initfuncs._funcs.GetVideoModeInfo )
            if initfuncs._funcs.GetVideoModeInfo( mode, &self._info ) == -1:
                raise Exception( 'could not get video mode info for mode %i' % mode )
        if mode == -1:
            checkSupported( initfuncs._funcs.GetCurrentVideoModeInfo )
            initfuncs._funcs.GetCurrentVideoModeInfo( &self._info )

    property Attributes:
        def __get__( self ): return self._info.Attributes

    property XResolution:
        def __get__( self ): return self._info.XResolution

    property YResolution:
        def __get__( self ): return self._info.YResolution

    property XCharSize:
        def __get__( self ): return self._info.XCharSize

    property YCharSize:
        def __get__( self ): return self._info.YCharSize

    property BytesPerScanLine:
        def __get__( self ): return self._info.BytesPerScanLine

    property MaxBytesPerScanLine:
        def __get__( self ): return self._info.MaxBytesPerScanLine

    property MaxScanLineWidth:
        def __get__( self ): return self._info.MaxScanLineWidth

    property MaxScanLines:
        def __get__( self ): return self._info.MaxScanLines

    property LinearHeapStart:
        def __get__( self ): return self._info.LinearHeapStart

    property MaxLinearOffset:
        def __get__( self ): return self._info.MaxLinearOffset

    property BitsPerPixel:
        def __get__( self ): return self._info.BitsPerPixel

    #    GA_pixelFormat  PixelFormat

    property MaxBuffers:
        def __get__( self ): return self._info.MaxBuffers

    property MaxPixelClock:
        def __get__( self ): return self._info.MaxPixelClock

    property DefaultRefreshRate:
        def __get__( self ): return self._info.DefaultRefreshRate

    #N_int32         *RefreshRateList

    property BitmapStartAlign:
        def __get__( self ): return self._info.BitmapStartAlign

    property BitmapStridePad:
        def __get__( self ): return self._info.BitmapStridePad

    property MonoBitmapStartAlign:
        def __get__( self ): return self._info.MonoBitmapStartAlign

    property MonoBitmapStridePad:
        def __get__( self ): return self._info.MonoBitmapStridePad

    #    GA_bltFx        *BitBltCaps
    #    GA_videoInf     **VideoWindows

    property VideoTextureFormats:
        def __get__( self ): return self._info.VideoTextureFormats

    property DepthFormats:
        def __get__( self ): return self._info.DepthFormats

    property DepthStartAlign:
        def __get__( self ): return self._info.DepthStartAlign

    property DepthStridePad:
        def __get__( self ): return self._info.DepthStridePad

    property TextureFormats:
        def __get__( self ): return self._info.TextureFormats

    property TextureStartAlign:
        def __get__( self ): return self._info.TextureStartAlign

    property TextureStridePad:
        def __get__( self ): return self._info.TextureStridePad

    property TextureMaxX:
        def __get__( self ): return self._info.TextureMaxX

    property TextureMaxY:
        def __get__( self ): return self._info.TextureMaxY

    property TextureMaxAspect:
        def __get__( self ): return self._info.TextureMaxAspect

    property StencilFormats:
        def __get__( self ): return self._info.StencilFormats

    property StencilStartAlign:
        def __get__( self ): return self._info.StencilStartAlign

    property StencilStridePad:
        def __get__( self ): return self._info.StencilStridePad

    property LinearSize:
        def __get__( self ): return self._info.LinearSize

    property LinearBasePtr:
        def __get__( self ): return self._info.LinearBasePtr

    property AttributesExt:
        def __get__( self ): return self._info.AttributesExt

    property PhysicalXResolution:
        def __get__( self ): return self._info.PhysicalXResolution

    property PhysicalYResolution:
        def __get__( self ): return self._info.PhysicalYResolution



cdef class ConfigInfo:

    def __init__( self, InitFuncs initfuncs ):
        self._info.dwSize = sizeof( self._info )
        checkSupported( initfuncs._funcs.GetConfigInfo )
        initfuncs._funcs.GetConfigInfo( &self._info )

    property manufacturerName:
        def __get__( self ): return self._info.ManufacturerName

    property chipsetName:
        def __get__( self ): return self._info.ChipsetName

    property DACName:
        def __get__( self ): return self._info.DACName

    property clockName:
        def __get__( self ): return self._info.ClockName

    property versionInfo:
        def __get__( self ): return self._info.VersionInfo

    property buildDate:
        def __get__( self ): return self._info.BuildDate

    property certified:
        def __get__( self ): return self._info.Certified

    property certifiedDate:
        def __get__( self ): return self._info.CertifiedDate

    property certifyVersion:
        def __get__( self ): return self._info.CertifyVersion



cdef class DriverFuncs:

    def __init__( self, Driver driver ):
        self._funcs.dwSize = sizeof( self._funcs )
        if not GA_queryFunctions( driver._context, GA_GET_DRIVERFUNCS, &self._funcs ):
            raise Exception( 'unable to get DriverFuncs for driver' )

    def setBank( self, N_int32 bank):
        checkSupported( self._funcs.SetBank )
        self._funcs.SetBank( bank )

    def setDisplayStart( self, N_int32 offset, N_int32 waitVRT):
        checkSupported( self._funcs.SetDisplayStart )
        self._funcs.SetDisplayStart( offset, waitVRT )

    def setStereoDisplayStart( self, N_int32 leftOffset, N_int32 rightOffset, N_int32 waitVRT):
        checkSupported( self._funcs.SetStereoDisplayStart )
        self._funcs.SetStereoDisplayStart( leftOffset, rightOffset, waitVRT )

    def getDisplayStartStatus( self ):
        checkSupported( self._funcs.GetDisplayStartStatus )
        return self._funcs.GetDisplayStartStatus()

    def enableStereoMode( self, N_int32 enable):
        checkSupported( self._funcs.EnableStereoMode )
        self._funcs.EnableStereoMode( enable )

    def isVSync( self ):
        checkSupported( self._funcs.IsVSync )
        return bool( self._funcs.IsVSync() )

    def waitVSync( self ):
        checkSupported( self._funcs.WaitVSync )
        self._funcs.WaitVSync()

    def setVSyncWidth( self, N_int32 width):
        checkSupported( self._funcs.SetVSyncWidth )
        self._funcs.SetVSyncWidth( width )

    def getVSyncWidth( self ):
        checkSupported( self._funcs.GetVSyncWidth )
        return self._funcs.GetVSyncWidth()

#    def setPaletteData( self, GA_palette *pal, N_int32 num, N_int32 index, N_int32 waitVRT):
#        self._funcs.SetPaletteData( pal, num, index, waitVRT )

#    def getPaletteData( self, GA_palette *pal, N_int32 num, N_int32 index):
#        self._funcs.GetPaletteData(

#    def setGammaCorrectData( self, GA_palette *pal, N_int32 num, N_int32 index, N_int32 waitVRT):
#        self._funcs.SetGammaCorrectData(

#    def getGammaCorrectData( self, GA_palette *pal, N_int32 num, N_int32 index):
#        self._funcs.GetGammaCorrectData(

    def getCurrentScanLine( self ):
        checkSupported( self._funcs.GetCurrentScanLine )
        return self._funcs.GetCurrentScanLine()

#    def setPaletteDataExt( self, GA_paletteExt *pal, N_int32 num, N_int32 index, N_int32 waitVRT):
#        self._funcs.SetPaletteDataExt(

#    def getPaletteDataExt( self, GA_paletteExt *pal, N_int32 num, N_int32 index):
#        self._funcs.GetPaletteDataExt(

#    def setGammaCorrectDataExt( self, GA_paletteExt *pal, N_int32 num, N_int32 index, N_int32 waitVRT):
#        self._funcs.SetGammaCorrectDataExt(

#    def getGammaCorrectDataExt( self, GA_paletteExt *pal, N_int32 num, N_int32 index):
#        self._funcs.GetGammaCorrectDataExt(



cdef class TwoDStateFuncs:

    def __init__( self, Driver driver ):
        self._funcs.dwSize = sizeof( self._funcs )
        if not GA_queryFunctions( driver._context, GA_GET_2DSTATEFUNCS, &self._funcs ):
            raise Exception( 'unable to get TwoDStateFuncs for driver' )

#    def setDrawBuffer( self, GA_buffer *drawBuf ):
#        N_int32         (* SetDrawBuffer)

    def isIdle( self ):
        checkSupported( self._funcs.IsIdle )
        return self._funcs.IsIdle()

    def waitTillIdle( self ):
        checkSupported( self._funcs.WaitTillIdle )
        self._funcs.WaitTillIdle()

    def enableDirectAccess( self ):
        checkSupported( self._funcs.EnableDirectAccess )
        self._funcs.EnableDirectAccess()

    def disableDirectAccess( self ):
        checkSupported( self._funcs.DisableDirectAccess )
        self._funcs.DisableDirectAccess()

    def setMix( self, N_int32 mix ):
        checkSupported( self._funcs.SetMix )
        if not self._funcs.SetMix( mix ):
            raise Exception( 'mix %i not supported' % mix )

    def setForeColor( self, GA_color color ):
        checkSupported( self._funcs.SetForeColor )
        self._funcs.SetForeColor( color )

    def setBackColor( self, GA_color color ):
        checkSupported( self._funcs.SetBackColor )
        self._funcs.SetBackColor( color )

#    def set8x8MonoPattern( self, N_int32 index, GA_pattern *pattern ):
#        self._funcs.Set8x8MonoPattern(

    def use8x8MonoPattern( self, N_int32 index ):
        checkSupported( self._funcs.Use8x8MonoPattern )
        self._funcs.Use8x8MonoPattern( index )

    def use8x8TransMonoPattern( self, N_int32 index ):
        checkSupported( self._funcs.Use8x8TransMonoPattern )
        self._funcs.Use8x8TransMonoPattern( index )

#    def set8x8ColorPattern( self, N_int32 index, GA_colorPattern *pattern ):
#        self._funcs.Set8x8ColorPattern(

    def use8x8ColorPattern( self, N_int32 index ):
        checkSupported( self._funcs.Use8x8ColorPattern )
        self._funcs.Use8x8ColorPattern( index )

    def use8x8TransColorPattern( self, N_int32 index, GA_color transparent ):
        checkSupported( self._funcs.Use8x8TransColorPattern )
        self._funcs.Use8x8TransColorPattern( index, transparent )

    def setLineStipple( self, GA_stipple stipple ):
        checkSupported( self._funcs.SetLineStipple )
        self._funcs.SetLineStipple( stipple )

    def setLineStippleCount( self, N_uint32 count ):
        checkSupported( self._funcs.SetLineStippleCount )
        self._funcs.SetLineStippleCount( count )

    def setPlaneMask( self, N_uint32 mask ):
        checkSupported( self._funcs.SetPlaneMask )
        self._funcs.SetPlaneMask( mask )

    def setAlphaValue( self, N_uint8 alpha ):
        checkSupported( self._funcs.SetAlphaValue )
        self._funcs.SetAlphaValue( alpha )

    def setLineStyle( self, N_uint32 styleMask, N_uint32 styleStep, N_uint32 styleValue ):
        checkSupported( self._funcs.SetLineStyle )
        self._funcs.SetLineStyle( styleMask, styleStep, styleValue )

#    def buildTranslateVector( self, GA_color *translate, GA_palette *dstPal, GA_palette *srcPal, int srcColors ):
#        self._funcs.BuildTranslateVector(

    def setBlendFunc( self, N_int32 srcBlendFunc, N_int32 dstBlendFunc ):
        checkSupported( self._funcs.SetBlendFunc )
        self._funcs.SetBlendFunc( srcBlendFunc, dstBlendFunc )



cdef class TwoDRenderFuncs:

    def __init__( self, Driver driver ):
        self._funcs.dwSize = sizeof( self._funcs )
        if not GA_queryFunctions( driver._context, GA_GET_2DRENDERFUNCS, &self._funcs ):
            raise Exception( 'unable to get TwoDRenderFuncs for driver' )

    def getPixel( self, N_int32 x, N_int32 y ):
        checkSupported( self._funcs.GetPixel )
        return self._funcs.GetPixel( x, y )

    def putPixel( self, N_int32 x, N_int32 y ):
        checkSupported( self._funcs.PutPixel )
        self._funcs.PutPixel( x, y )

#    def drawScanList( self, N_int32 y, N_int32 length, N_int16 *scans ):
#        self._funcs.DrawScanList(

#    def drawPattScanList( self, N_int32 y, N_int32 length, N_int16 *scans ):
#        void            self._funcs.DrawPattScanList(

#    def drawColorPattScanList( self, N_int32 y, N_int32 length, N_int16 *scans ):
#        void            self._funcs.DrawColorPattScanList(

#    def drawEllipseList( self, N_int32 y, N_int32 length, N_int32 height, N_int16 *scans ):
#        void            self._funcs.DrawEllipseList(

#    def drawPattEllipseList( self, N_int32 y, N_int32 length, N_int32 height, N_int16 *scans ):
#        void            self._funcs.DrawPattEllipseList(

#    def drawColorPattEllipseList( self, N_int32 y, N_int32 length, N_int32 height, N_int16 *scans ):
#        void            self._funcs.DrawColorPattEllipseList(

#    def drawFatEllipseList( self, N_int32 y, N_int32 length, N_int32 height, N_int16 *scans ):
#        void            self._funcs.DrawFatEllipseList(

#    def drawPattFatEllipseList( self, N_int32 y, N_int32 length, N_int32 height, N_int16 *scans ):
#        void            self._funcs.DrawPattFatEllipseList(

#    def drawColorPattFatEllipseList( self, N_int32 y, N_int32 length, N_int32 height, N_int16 *scans ):
#        void            self._funcs.DrawColorPattFatEllipseList(

    def drawRect( self, N_int32 left, N_int32 top, N_int32 width, N_int32 height ):
        checkSupported( self._funcs.DrawRect )
        self._funcs.DrawRect( left, top, width, height )

    def drawPattRect( self, N_int32 left, N_int32 top, N_int32 width, N_int32 height ):
        checkSupported( self._funcs.DrawPattRect )
        self._funcs.DrawPattRect( left, top, width, height )

    def drawColorPattRect( self, N_int32 left, N_int32 top, N_int32 width, N_int32 height ):
        checkSupported( self._funcs.DrawColorPattRect )
        self._funcs.DrawColorPattRect( left, top, width, height )

#    def drawTrap( self, GA_trap *trap ):
#        void            self._funcs.DrawTrap(

#    def drawPattTrap( self, GA_trap *trap ):
#        void            self._funcs.DrawPattTrap(

#    def drawColorPattTrap( self, GA_trap *trap ):
#        void            self._funcs.DrawColorPattTrap(

    def drawLineInt( self, N_int32 x1, N_int32 y1, N_int32 x2, N_int32 y2, N_int32 drawLast=1 ):
        checkSupported( self._funcs.DrawLineInt )
        self._funcs.DrawLineInt( x1, y1, x2, y2, drawLast )

#    def drawBresenhamLine( self, N_int32 x1, N_int32 y1, N_int32 initialError, N_int32 majorInc, N_int32 diagInc, N_int32 count, N_int32 flags ):
#        void            self._funcs.DrawBresenhamLine(

    def drawStippleLineInt( self, N_int32 x1, N_int32 y1, N_int32 x2, N_int32 y2, N_int32 drawLast=1, N_int32 transparent=0 ):
        checkSupported( self._funcs.DrawStippleLineInt )
        self._funcs.DrawStippleLineInt( x1, y1, x2, y2, drawLast, transparent )

#    def drawBresenhamStippleLine( self, N_int32 x1, N_int32 y1, N_int32 initialError, N_int32 majorInc, N_int32 diagInc, N_int32 count, N_int32 flags, N_int32 transparent ):
#        void            self._funcs.DrawBresenhamStippleLine(

    def drawEllipse( self, N_int32 left, N_int32 top, N_int32 A, N_int32 B ):
        checkSupported( self._funcs.DrawEllipse )
        self._funcs.DrawEllipse( left, top, A, B )

    def clipEllipse( self, N_int32 left, N_int32 top, N_int32 A, N_int32 B, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom ):
        checkSupported( self._funcs.ClipEllipse )
        self._funcs.ClipEllipse( left, top, A, B, clipLeft, clipTop, clipRight, clipBottom )

#    def putMonoImageMSBSys( self, N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_uint8 *image, N_int32 transparent ):
#        void            self._funcs.PutMonoImageMSBSys(

#    def putMonoImageMSBLin( self, N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_int32 imageOfs, N_int32 transparent ):
#        void            self._funcs.PutMonoImageMSBLin(

#    def putMonoImageMSBBM( self, N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_uint8 *image, N_int32 imagePhysAddr, N_int32 transparent ):
#        void            self._funcs.PutMonoImageMSBBM(

#    def putMonoImageLSBSys( self, N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_uint8 *image, N_int32 transparent ):
#        void            self._funcs.PutMonoImageLSBSys(

#    def putMonoImageLSBLin( self, N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_int32 imageOfs, N_int32 transparent ):
#        void            self._funcs.PutMonoImageLSBLin(

#    def putMonoImageLSBBM( self, N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_uint8 *image, N_int32 imagePhysAddr, N_int32 transparent ):
#        void            self._funcs.PutMonoImageLSBBM(

#    def clipMonoImageMSBSys( self, N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_uint8 *image, N_int32 transparent, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom ):
#        void            self._funcs.ClipMonoImageMSBSys(

#    def clipMonoImageMSBLin( self, N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_int32 imageOfs, N_int32 transparent, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom ):
#        void            self._funcs.ClipMonoImageMSBLin(

#    def clipMonoImageMSBBM( self, N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_uint8 *image, N_int32 imagePhysAddr, N_int32 transparent, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom ):
#        void            self._funcs.ClipMonoImageMSBBM(

#    def clipMonoImageLSBSys( self, N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_uint8 *image, N_int32 transparent, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom ):
#        void            self._funcs.ClipMonoImageLSBSys(

#    def clipMonoImageLSBLin( self, N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_int32 imageOfs, N_int32 transparent, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom ):
#        void            self._funcs.ClipMonoImageLSBLin(

#    def clipMonoImageLSBBM( self, N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_uint8 *image, N_int32 imagePhysAddr, N_int32 transparent, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom ):
#        void            self._funcs.ClipMonoImageLSBBM(

#    def bitBlt( self, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix ):
#        void            self._funcs.BitBlt(

#    def bitBltLin( self, N_int32 srcOfs, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix ):
#        void            self._funcs.BitBltLin(

#    def bitBltSys( self, void *srcAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix, N_int32 flipY ):
#        void            self._funcs.BitBltSys(

#    def bitBltBM( self, void *srcAddr, N_int32 srcPhysAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix ):
#        void            self._funcs.BitBltBM(

#    def bitBltPatt( self, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 rop3 ):
#        void            self._funcs.BitBltPatt(

#    def bitBltPattLin( self, N_int32 srcOfs, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 rop3 ):
#        void            self._funcs.BitBltPattLin(

#    def bitBltPattSys( self, void *srcAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 rop3, N_int32 flipY ):
#        void            self._funcs.BitBltPattSys(

#    def bitBltPattBM( self, void *srcAddr, N_int32 srcPhysAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 rop3 ):
#        void            self._funcs.BitBltPattBM(

#    def bitBltColorPatt( self, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 rop3 ):
#        void            self._funcs.BitBltColorPatt(

#    def bitBltColorPattLin( self, N_int32 srcOfs, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 rop3 ):
#        void            self._funcs.BitBltColorPattLin(

#    def bitBltColorPattSys( self, void *srcAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 rop3, N_int32 flipY ):
#        void            self._funcs.BitBltColorPattSys(

#    def bitBltColorPattBM( self, void *srcAddr, N_int32 srcPhysAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 rop3 ):
#        void            self._funcs.BitBltColorPattBM(

#    def srcTransBlt( self, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix, GA_color transparent ):
#        void            self._funcs.SrcTransBlt(

#    def srcTransBltLin( self, N_int32 srcOfs, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix, GA_color transparent ):
#        void            self._funcs.SrcTransBltLin(

#    def srcTransBltSys( self, void *srcAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix, GA_color transparent, N_int32 flipY ):
#        void            self._funcs.SrcTransBltSys(

#    def srcTransBltBM( self, void *srcAddr, N_int32 srcPhysAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix, GA_color transparent ):
#        void            self._funcs.SrcTransBltBM(

#    def dstTransBlt( self, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix, GA_color transparent ):
#        void            self._funcs.DstTransBlt(

#    def dstTransBltLin( self, N_int32 srcOfs, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix, GA_color transparent ):
#        void            self._funcs.DstTransBltLin(

#    def dstTransBltSys( self, void *srcAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix, GA_color transparent, N_int32 flipY ):
#        void            self._funcs.DstTransBltSys(

#    def dstTransBltBM( self, void *srcAddr, N_int32 srcPhysAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix, GA_color transparent ):
#        void            self._funcs.DstTransBltBM(

#    def stretchBlt( self, N_int32 srcLeft, N_int32 srcTop, N_int32 srcWidth, N_int32 srcHeight, N_int32 dstLeft, N_int32 dstTop, N_int32 dstWidth, N_int32 dstHeight, N_int32 doClip, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom, N_int32 mix ):
#        void            self._funcs.StretchBlt(

#    def stretchBltLin( self, N_int32 srcOfs, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 srcWidth, N_int32 srcHeight, N_int32 dstLeft, N_int32 dstTop, N_int32 dstWidth, N_int32 dstHeight, N_int32 doClip, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom, N_int32 mix ):
#        void            self._funcs.StretchBltLin(

#    def stretchBltSys( self, void *srcAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 srcWidth, N_int32 srcHeight, N_int32 dstLeft, N_int32 dstTop, N_int32 dstWidth, N_int32 dstHeight, N_int32 doClip, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom, N_int32 mix, N_int32 flipY ):
#        void            self._funcs.StretchBltSys(

#    def stretchBltBM( self, void *srcAddr, N_int32 srcPhysAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 srcWidth, N_int32 srcHeight, N_int32 dstLeft, N_int32 dstTop, N_int32 dstWidth, N_int32 dstHeight, N_int32 doClip, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom, N_int32 mix ):
#        void            self._funcs.StretchBltBM(

#    def convertBltSys_Obsolete( self, void *srcAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 bitsPerPixel, GA_pixelFormat *pixelFormat, GA_palette *dstPal, GA_palette *srcPal, N_int32 dither, N_int32 mix, N_int32 flipY ):
#        N_int32         self._funcs.ConvertBltSys_Obsolete(

#    def convertBltBM_Obsolete( self, void *srcAddr, N_int32 srcPhysAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 bitsPerPixel, GA_pixelFormat *pixelFormat, GA_palette *dstPal, GA_palette *srcPal, N_int32 dither, N_int32 mix ):
#        N_int32         self._funcs.ConvertBltBM_Obsolete(

#    def stretchConvertBltSys_Obsolete( self, void *srcAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 srcWidth, N_int32 srcHeight, N_int32 dstLeft, N_int32 dstTop, N_int32 dstWidth, N_int32 dstHeight, N_int32 doClip, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom, N_int32 bitsPerPixel, GA_pixelFormat *pixelFormat, GA_palette *dstPal, GA_palette *srcPal, N_int32 dither, N_int32 mix, N_int32 flipY ):
#        N_int32         self._funcs.StretchConvertBltSys_Obsolete(

#    def stretchConvertBltBM_Obsolete( self, void *srcAddr, N_int32 srcPhysAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 srcWidth, N_int32 srcHeight, N_int32 dstLeft, N_int32 dstTop, N_int32 dstWidth, N_int32 dstHeight, N_int32 doClip, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom, N_int32 bitsPerPixel, GA_pixelFormat *pixelFormat, GA_palette *dstPal, GA_palette *srcPal, N_int32 dither, N_int32 mix ):
#        N_int32         self._funcs.StretchConvertBltBM_Obsolete(

#    def bitBltFxTest( self, GA_bltFx *fx ):
#        N_int32         self._funcs.BitBltFxTest(

#    def bitBltFx( self, N_int32 srcLeft, N_int32 srcTop, N_int32 srcWidth, N_int32 srcHeight, N_int32 dstLeft, N_int32 dstTop, N_int32 dstWidth, N_int32 dstHeight, GA_bltFx *fx ):
#        void            self._funcs.BitBltFx(

#    def bitBltFxLin( self, N_int32 srcOfs, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 srcWidth, N_int32 srcHeight, N_int32 dstLeft, N_int32 dstTop, N_int32 dstWidth, N_int32 dstHeight, GA_bltFx *fx ):
#        void            self._funcs.BitBltFxLin(

#    def bitBltFxSys( self, void *srcAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 srcWidth, N_int32 srcHeight, N_int32 dstLeft, N_int32 dstTop, N_int32 dstWidth, N_int32 dstHeight, GA_bltFx *fx ):
#        void            self._funcs.BitBltFxSys(

#    def bitBltFxBM( self, void *srcAddr, N_int32 srcPhysAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 srcWidth, N_int32 srcHeight, N_int32 dstLeft, N_int32 dstTop, N_int32 dstWidth, N_int32 dstHeight, GA_bltFx *fx ):
#        void            self._funcs.BitBltFxBM(

#    def getBitmapSys( self, void *dstAddr, N_int32 dstPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix ):
#        void            self._funcs.GetBitmapSys(

#    def getBitmapBM( self, void *dstAddr, N_int32 dstPhysAddr, N_int32 dstPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix ):
#        void            self._funcs.GetBitmapBM(

    def updateScreen( self, N_int32 left, N_int32 top, N_int32 width, N_int32 height ):
        checkSupported( self._funcs.UpdateScreen )
        self._funcs.UpdateScreen( left, top, width, height )

    def drawClippedLineInt( self, N_int32 x1, N_int32 y1, N_int32 x2, N_int32 y2, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom, N_int32 drawLast=1 ):
        checkSupported( self._funcs.DrawClippedLineInt )
        return self._funcs.DrawClippedLineInt( x1, y1, x2, y2, drawLast, clipLeft, clipTop, clipRight, clipBottom )

#    def drawClippedBresenhamLine( self, N_int32 x1, N_int32 y1, N_int32 initialError, N_int32 majorInc, N_int32 diagInc, N_int32 count, N_int32 flags, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom ):
#        N_int32         self._funcs.DrawClippedBresenhamLine(

#    def drawClippedStippleLineInt( self, N_int32 x1, N_int32 y1, N_int32 x2, N_int32 y2, N_int32 drawLast, N_int32 transparent, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom ):
#        N_int32         self._funcs.DrawClippedStippleLineInt(
#
#    def drawClippedBresenhamStippleLine( self, N_int32 x1, N_int32 y1, N_int32 initialError, N_int32 majorInc, N_int32 diagInc, N_int32 count, N_int32 flags, N_int32 transparent, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom ):
#        N_int32         self._funcs.DrawClippedBresenhamStippleLine(
#
#    def bitBltPlaneMasked( self, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_uint32 planeMask ):
#        void            self._funcs.BitBltPlaneMasked(
#
#    def bitBltPlaneMaskedLin( self, N_int32 srcOfs, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_uint32 planeMask ):
#        void            self._funcs.BitBltPlaneMaskedLin(
#
#    def bitBltPlaneMaskedSys( self, void *srcAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_uint32 planeMask, N_int32 flipY ):
#        void            self._funcs.BitBltPlaneMaskedSys(
#
#    def bitBltPlaneMaskedBM( self, void *srcAddr, N_int32 srcPhysAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_uint32 planeMask ):
#        void            self._funcs.BitBltPlaneMaskedBM(
#
#    def drawRectLin( self, N_int32 dstOfs, N_int32 dstPitch, N_int32 left, N_int32 top, N_int32 width, N_int32 height, GA_color color, N_int32 mix ):
#        void            self._funcs.DrawRectLin(
#
#    def drawRectExt( self, N_int32 left, N_int32 top, N_int32 width, N_int32 height, GA_color color, N_int32 mix ):
#        void            self._funcs.DrawRectExt(
#
#    def drawStyleLineInt( self, N_int32 x1, N_int32 y1, N_int32 x2, N_int32 y2, N_int32 drawLast, N_int32 transparent ):
#        void            self._funcs.DrawStyleLineInt(
#
#    def drawBresenhamStyleLine( self, N_int32 x1, N_int32 y1, N_int32 initialError, N_int32 majorInc, N_int32 diagInc, N_int32 count, N_int32 flags, N_int32 transparent ):
#        void            self._funcs.DrawBresenhamStyleLine(
#
#    def drawClippedStyleLineInt( self, N_int32 x1, N_int32 y1, N_int32 x2, N_int32 y2, N_int32 drawLast, N_int32 transparent, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom ):
#        N_int32         self._funcs.DrawClippedStyleLineInt(
#
#    def drawClippedBresenhamStyleLine( self, N_int32 x1, N_int32 y1, N_int32 initialError, N_int32 majorInc, N_int32 diagInc, N_int32 count, N_int32 flags, N_int32 transparent, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom ):
#        N_int32         self._funcs.DrawClippedBresenhamStyleLine(



def enumerateDevices( shared=0 ):
    return GA_enumerateDevices( shared )
