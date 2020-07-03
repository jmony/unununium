from common cimport N_int32, N_uint32, N_uint8, N_int16, N_uint16, N_int8, N_fix32, ibool, uchar

cdef extern from "snap/graphics.h":

    ctypedef enum GA_modeFlagsType:
        gaDontClear                     = 0x8000
        gaLinearBuffer                  = 0x4000
        ga6BitDAC                       = 0x2000
        gaNoAccel                       = 0x1000
        gaRefreshCtrl                   = 0x0800
        gaWindowedMode                  = 0x0400
        gaPartialModeSet                = 0x0200
        gaModeMask                      = 0x01FF

    ctypedef enum GA_funcGroupsType:
        GA_GET_RESERVED
        GA_GET_INITFUNCS
        GA_GET_DRIVERFUNCS
        GA_GET_CURSORFUNCS
        GA_GET_VIDEOFUNCS
        GA_GET_DPMSFUNCS
        GA_GET_SCIFUNCS
        GA_GET_2DSTATEFUNCS
        GA_GET_2DRENDERFUNCS
        GA_GET_RESERVED1
        GA_GET_RESERVED2
        GA_GET_RESERVED3
        GA_GET_RESERVED4
        GA_GET_VBEFUNCS
        GA_GET_REGIONFUNCS
        GA_GET_BUFFERFUNCS
        GA_GET_CLIPPERFUNCS
        GA_GET_FIRST_OEM                = 0x00010000

    ctypedef struct GA_recMode:
        N_uint16    XResolution
        N_uint16    YResolution
        N_uint8     BitsPerPixel
        N_int8      RefreshRate

    ctypedef struct GA_layout:
        N_uint32 left
        N_uint32 top
        N_uint32 right
        N_uint32 bottom

    ctypedef struct GA_globalOptions:
        N_uint32        dwSize
        N_uint8         bVirtualDisplay
        N_uint8         bPortrait
        N_uint8         bFlipped
        N_uint8         bInvertColors
        N_uint8         bVBEOnly
        N_uint8         bVGAOnly
        N_uint8         bReserved1
        N_uint16        wCertifiedVersion
        N_uint8         bNoWriteCombine
        N_uint8         bAllowNonCertified
        N_uint8         bLCDUseBIOS
        N_uint8         bUseMemoryDriver
        N_uint16        wSysMemSize
        N_uint32        dwReserved2
        N_uint8         bVBEUseLinear
        N_uint8         bVBEUsePal
        N_uint8         bVBEUsePM32
        N_uint8         bReserved2
        N_uint8         bVBEUseVBE20
        N_uint8         bVBEUseVBE30
        N_uint8         bVBEUsePM
        N_uint8         bVBEUseSCI
        N_uint8         bVBEUseDDC
        N_uint8         bGDIUseAccel
        N_uint8         bGDIUseBrushCache
        N_uint8         bGDIUseBitmapCache
        N_uint8         bDXUseAccel2D
        N_uint8         bDXUseAccel3D
        N_uint8         bDXUseAccelVideo
        N_uint8         bDXWaitRetrace
        N_uint32        dwCPLFlags
        N_uint32        dwSharedAGPMemSize
        N_uint8         bUseVBECore
        N_uint8         bUseVGACore
        N_uint32        dwCheckForUpdates
        N_uint8         bNoDDCDetect
        N_uint8         bDisableLogFile
        N_uint8         bCheckWebSelection
        N_uint16        wMonitorHSize
        N_uint16        wMonitorVSize
        N_uint16        wOptimizedModeXRes
        N_uint16        wOptimizedModeYRes
        N_uint16        wOptimizedModeBits
        GA_recMode      recommendedMode
        GA_recMode      recommendedMode8
        GA_recMode      recommendedMode16
        GA_recMode      recommendedMode24
        GA_recMode      recommendedMode32
        N_uint8         bAGPFastWrite
        N_uint8         bMaxAGPRate
        GA_layout       virtualSize
        GA_layout       resolutions[16] #[GA_MAX_VIRTUAL_DISPLAYS]
        GA_layout       bounds[16]  #[GA_MAX_VIRTUAL_DISPLAYS]


    ctypedef struct GA_configInfo:
        N_uint32        dwSize
        char            ManufacturerName[80]
        char            ChipsetName[80]
        char            DACName[80]
        char            ClockName[80]
        char            VersionInfo[80]
        char            BuildDate[80]
        char            Certified
        char            CertifiedDate[20]
        N_uint16        CertifyVersion


    ctypedef struct GA_mode
    ctypedef struct GA_options 
    ctypedef struct GA_modeProfile
    ctypedef struct GA_bltFx
    ctypedef struct GA_videoInf

    ctypedef struct GA_pixelFormat:
        N_uint8 RedMask
        N_uint8 RedPosition
        N_uint8 RedAdjust
        N_uint8 GreenMask
        N_uint8 GreenPosition
        N_uint8 GreenAdjust
        N_uint8 BlueMask
        N_uint8 BluePosition
        N_uint8 BlueAdjust
        N_uint8 AlphaMask
        N_uint8 AlphaPosition
        N_uint8 AlphaAdjust


    ctypedef struct GA_modeInfo:
        N_uint32        dwSize
        N_uint32        Attributes
        N_uint16        XResolution
        N_uint16        YResolution
        N_uint8         XCharSize
        N_uint8         YCharSize
        N_uint32        BytesPerScanLine
        N_uint32        MaxBytesPerScanLine
        N_uint32        MaxScanLineWidth
        N_uint32        MaxScanLines
        N_uint32        LinearHeapStart
        N_uint32        MaxLinearOffset
        N_uint16        BitsPerPixel
        GA_pixelFormat  PixelFormat
        N_uint16        MaxBuffers
        N_uint32        MaxPixelClock
        N_int32         DefaultRefreshRate
        N_int32         *RefreshRateList
        N_uint32        BitmapStartAlign
        N_uint32        BitmapStridePad
        N_uint32        MonoBitmapStartAlign
        N_uint32        MonoBitmapStridePad
        GA_bltFx        *BitBltCaps
        GA_videoInf     **VideoWindows
        N_uint32        VideoTextureFormats
        N_uint32        DepthFormats
        N_uint32        DepthStartAlign
        N_uint32        DepthStridePad
        N_uint32        TextureFormats
        N_uint32        TextureStartAlign
        N_uint32        TextureStridePad
        N_uint32        TextureMaxX
        N_uint32        TextureMaxY
        N_uint16        TextureMaxAspect
        N_uint32        StencilFormats
        N_uint32        StencilStartAlign
        N_uint32        StencilStridePad
        N_uint32        LinearSize
        N_uint32        LinearBasePtr
        N_uint32        AttributesExt
        N_uint16        PhysicalXResolution
        N_uint16        PhysicalYResolution

    ctypedef struct GA_CRTCInfo
    ctypedef struct GA_monitor
    ctypedef struct GA_certifyInfo
    cdef struct _REF2D_driver
    ctypedef struct GA_palette
    ctypedef struct GA_paletteExt
    ctypedef struct GA_loaderFuncs

    ctypedef struct GA_driverFuncs:
        N_uint32        dwSize
        void            (* SetBank)( N_int32 bank )
        void            (* SetDisplayStart)( N_int32 offset, N_int32 waitVRT )
        void            (* SetStereoDisplayStart)( N_int32 leftOffset, N_int32 rightOffset, N_int32 waitVRT )
        N_int32         (* GetDisplayStartStatus)()
        void            (* EnableStereoMode)( N_int32 enable )
        N_int32         (* IsVSync)()
        void            (* WaitVSync)()
        void            (* SetVSyncWidth)( N_int32 width )
        N_int32         (* GetVSyncWidth)()
#        void            (* SetPaletteData)( GA_palette *pal, N_int32 num, N_int32 index, N_int32 waitVRT )
#        void            (* GetPaletteData)( GA_palette *pal, N_int32 num, N_int32 index )
#        void            (* SetGammaCorrectData)( GA_palette *pal, N_int32 num, N_int32 index, N_int32 waitVRT )
#        void            (* GetGammaCorrectData)( GA_palette *pal, N_int32 num, N_int32 index )
        N_int32         (* GetCurrentScanLine)()
#        void            (* SetPaletteDataExt)( GA_paletteExt *pal, N_int32 num, N_int32 index, N_int32 waitVRT )
#        void            (* GetPaletteDataExt)( GA_paletteExt *pal, N_int32 num, N_int32 index )
#        void            (* SetGammaCorrectDataExt)( GA_paletteExt *pal, N_int32 num, N_int32 index, N_int32 waitVRT )
#        void            (* GetGammaCorrectDataExt)( GA_paletteExt *pal, N_int32 num, N_int32 index )

    ctypedef struct GA_initFuncs:
        N_uint32        dwSize
        void            (* GetConfigInfo)( GA_configInfo *info )
#        void            (* SetModeProfile)( GA_modeProfile *profile )
#        void            (* GetOptions)( GA_options *options )
#        void            (* SetOptions)( GA_options *options )
        N_int32         (* GetVideoModeInfo)( N_uint32 mode, GA_modeInfo *modeInfo )
        N_int32         (* SetVideoMode)( N_uint32 mode, N_int32 *virtualX, N_int32 *virtualY, N_int32 *bytesPerLine, N_int32 *maxMem, N_int32 refreshRate, GA_CRTCInfo *crtc )
#        N_uint32        (* GetVideoMode)()
#        N_int32         (* GetCustomVideoModeInfo)( N_int32 xRes, N_int32 yRes, N_int32 virtualX, N_int32 virtualY, N_int32 bitsPerPixel, GA_modeInfo *modeInfo )
#        N_int32         (* SetCustomVideoMode)( N_int32 xRes, N_int32 yRes, N_int32 bitsPerPixel, N_uint32 flags, N_int32 *virtualX, N_int32 *virtualY, N_int32 *bytesPerLine, N_int32 *maxMem, GA_CRTCInfo *crtc )
#        N_uint32        (* GetClosestPixelClockV1)( N_int32 xRes, N_int32 yRes, N_int32 bitsPerPixel, N_uint32 pixelClock )
#        void            (* GetCRTCTimings)( GA_CRTCInfo *crtc )
#        void            (* SaveCRTCTimings)( GA_CRTCInfo *crtc )
#        void            (* SetGlobalRefresh)( N_int32 refresh, N_int32 outputHead )
#        N_int32         (* SaveRestoreState)( N_int32 subfunc, void *saveBuf )
#        N_int32         (* SetDisplayOutput)( N_int32 device )
#        N_int32         (* GetDisplayOutput)( )
#        void            (* SetSoftwareRenderFuncs)( GA_2DRenderFuncs *softwareFuncs )
#        void            (* GetUniqueFilename)( char *filename, int type )
#        void            (* GetMonitorInfo)( GA_monitor *monitor, N_int32 outputHead )
#        void            (* SetMonitorInfo)( GA_monitor *monitor, N_int32 outputHead )
        void            (* GetCurrentVideoModeInfo)( GA_modeInfo *modeInfo )
#        void            (* GetCertifyInfo)( GA_certifyInfo *info )
#        void            (* SetCRTCTimings)( GA_CRTCInfo *crtc )
#        ibool           (* AlignLinearBuffer)( N_int32 height, N_int32 *stride, N_int32 *offset, N_int32 *size, N_int32 growUp )
#        N_int32         (* GetCurrentRefreshRate)()
#        N_int32         (* PollForDisplaySwitch)()
#        void            (* PerformDisplaySwitch)()
#        N_int32         (* GetVideoModeInfoExt)( N_uint32 mode, GA_modeInfo *modeInfo, N_int32 outputDevice, N_int32 outputHead )
#        N_int32         (* GetCustomVideoModeInfoExt)( N_int32 xRes, N_int32 yRes, N_int32 virtualX, N_int32 virtualY, N_int32 bitsPerPixel, GA_modeInfo *modeInfo, N_int32 outputDevice, N_int32 outputHead )
#        N_int32         (* SwitchPhysicalResolution)( N_int32 physicalXResolution, N_int32 physicalYResolution, N_int32 refreshRate )
#        N_int32         (* GetNumberOfHeads)()
#        N_int32         (* SetActiveHead)( N_int32 headIndex )
#        N_int32         (* GetActiveHead)()
#        void            (* SetRef2dPointer)( _REF2D_driver *ref2d )
#        N_int32         (* SetDisplayOutputExt)( N_int32 device, N_int32 outputHead )
#        N_int32         (* GetDisplayOutputExt)( N_int32 outputHead )
#        N_uint32        (* GetClosestPixelClock)( N_int32 outputHead, N_int32 xRes, N_int32 yRes, N_int32 bitsPerPixel, N_uint32 pixelClock )


    ctypedef N_uint32 GA_stipple
    ctypedef N_uint32 GA_color

    ctypedef struct GA_2DStateFuncs:
        N_uint32        dwSize
#        N_int32         (* SetDrawBuffer)( GA_buffer *drawBuf )
        N_int32         (* IsIdle)()
        void            (* WaitTillIdle)()
        void            (* EnableDirectAccess)()
        void            (* DisableDirectAccess)()
        N_int32         (* SetMix)( N_int32 mix )
        void            (* SetForeColor)( GA_color color )
        void            (* SetBackColor)( GA_color color )
#        void            (* Set8x8MonoPattern)( N_int32 index, GA_pattern *pattern )
        void            (* Use8x8MonoPattern)( N_int32 index )
        void            (* Use8x8TransMonoPattern)( N_int32 index )
#        void            (* Set8x8ColorPattern)( N_int32 index, GA_colorPattern *pattern )
        void            (* Use8x8ColorPattern)( N_int32 index )
        void            (* Use8x8TransColorPattern)( N_int32 index, GA_color transparent )
        void            (* SetLineStipple)( GA_stipple stipple )
        void            (* SetLineStippleCount)( N_uint32 count )
        void            (* SetPlaneMask)( N_uint32 mask )
        void            (* SetAlphaValue)( N_uint8 alpha )
        void            (* SetLineStyle)( N_uint32 styleMask, N_uint32 styleStep, N_uint32 styleValue )
#        void            (* BuildTranslateVector)( GA_color *translate, GA_palette *dstPal, GA_palette *srcPal, int srcColors )
        void            (* SetBlendFunc)( N_int32 srcBlendFunc, N_int32 dstBlendFunc )


    ctypedef struct GA_trap:
        N_uint32    y
        N_uint32    count
        N_fix32     x1
        N_fix32     x2
        N_fix32     slope1
        N_fix32     slope2


    ctypedef struct GA_2DRenderFuncs:
        N_uint32        dwSize
        GA_color        (* GetPixel)( N_int32 x, N_int32 y )
        void            (* PutPixel)( N_int32 x, N_int32 y )
#        void            (* DrawScanList)( N_int32 y, N_int32 length, N_int16 *scans )
#        void            (* DrawPattScanList)( N_int32 y, N_int32 length, N_int16 *scans )
#        void            (* DrawColorPattScanList)( N_int32 y, N_int32 length, N_int16 *scans )
#        void            (* DrawEllipseList)( N_int32 y, N_int32 length, N_int32 height, N_int16 *scans )
#        void            (* DrawPattEllipseList)( N_int32 y, N_int32 length, N_int32 height, N_int16 *scans )
#        void            (* DrawColorPattEllipseList)( N_int32 y, N_int32 length, N_int32 height, N_int16 *scans )
#        void            (* DrawFatEllipseList)( N_int32 y, N_int32 length, N_int32 height, N_int16 *scans )
#        void            (* DrawPattFatEllipseList)( N_int32 y, N_int32 length, N_int32 height, N_int16 *scans )
#        void            (* DrawColorPattFatEllipseList)( N_int32 y, N_int32 length, N_int32 height, N_int16 *scans )
        void            (* DrawRect)( N_int32 left, N_int32 top, N_int32 width, N_int32 height )
        void            (* DrawPattRect)( N_int32 left, N_int32 top, N_int32 width, N_int32 height )
        void            (* DrawColorPattRect)( N_int32 left, N_int32 top, N_int32 width, N_int32 height )
#        void            (* DrawTrap)( GA_trap *trap )
#        void            (* DrawPattTrap)( GA_trap *trap )
#        void            (* DrawColorPattTrap)( GA_trap *trap )
        void            (* DrawLineInt)( N_int32 x1, N_int32 y1, N_int32 x2, N_int32 y2, N_int32 drawLast )
#        void            (* DrawBresenhamLine)( N_int32 x1, N_int32 y1, N_int32 initialError, N_int32 majorInc, N_int32 diagInc, N_int32 count, N_int32 flags )
        void            (* DrawStippleLineInt)( N_int32 x1, N_int32 y1, N_int32 x2, N_int32 y2, N_int32 drawLast, N_int32 transparent )
#        void            (* DrawBresenhamStippleLine)( N_int32 x1, N_int32 y1, N_int32 initialError, N_int32 majorInc, N_int32 diagInc, N_int32 count, N_int32 flags, N_int32 transparent )
        void            (* DrawEllipse)( N_int32 left, N_int32 top, N_int32 A, N_int32 B )
        void            (* ClipEllipse)( N_int32 left, N_int32 top, N_int32 A, N_int32 B, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom )
#        void            (* PutMonoImageMSBSys)( N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_uint8 *image, N_int32 transparent )
#        void            (* PutMonoImageMSBLin)( N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_int32 imageOfs, N_int32 transparent )
#        void            (* PutMonoImageMSBBM)( N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_uint8 *image, N_int32 imagePhysAddr, N_int32 transparent )
#        void            (* PutMonoImageLSBSys)( N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_uint8 *image, N_int32 transparent )
#        void            (* PutMonoImageLSBLin)( N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_int32 imageOfs, N_int32 transparent )
#        void            (* PutMonoImageLSBBM)( N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_uint8 *image, N_int32 imagePhysAddr, N_int32 transparent )
#        void            (* ClipMonoImageMSBSys)( N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_uint8 *image, N_int32 transparent, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom )
#        void            (* ClipMonoImageMSBLin)( N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_int32 imageOfs, N_int32 transparent, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom )
#        void            (* ClipMonoImageMSBBM)( N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_uint8 *image, N_int32 imagePhysAddr, N_int32 transparent, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom )
#        void            (* ClipMonoImageLSBSys)( N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_uint8 *image, N_int32 transparent, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom )
#        void            (* ClipMonoImageLSBLin)( N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_int32 imageOfs, N_int32 transparent, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom )
#        void            (* ClipMonoImageLSBBM)( N_int32 x, N_int32 y, N_int32 width, N_int32 height, N_int32 byteWidth, N_uint8 *image, N_int32 imagePhysAddr, N_int32 transparent, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom )
#        void            (* BitBlt)( N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix )
#        void            (* BitBltLin)( N_int32 srcOfs, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix )
#        void            (* BitBltSys)( void *srcAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix, N_int32 flipY )
#        void            (* BitBltBM)( void *srcAddr, N_int32 srcPhysAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix )
#        void            (* BitBltPatt)( N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 rop3 )
#        void            (* BitBltPattLin)( N_int32 srcOfs, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 rop3 )
#        void            (* BitBltPattSys)( void *srcAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 rop3, N_int32 flipY )
#        void            (* BitBltPattBM)( void *srcAddr, N_int32 srcPhysAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 rop3 )
#        void            (* BitBltColorPatt)( N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 rop3 )
#        void            (* BitBltColorPattLin)( N_int32 srcOfs, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 rop3 )
#        void            (* BitBltColorPattSys)( void *srcAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 rop3, N_int32 flipY )
#        void            (* BitBltColorPattBM)( void *srcAddr, N_int32 srcPhysAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 rop3 )
#        void            (* SrcTransBlt)( N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix, GA_color transparent )
#        void            (* SrcTransBltLin)( N_int32 srcOfs, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix, GA_color transparent )
#        void            (* SrcTransBltSys)( void *srcAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix, GA_color transparent, N_int32 flipY )
#        void            (* SrcTransBltBM)( void *srcAddr, N_int32 srcPhysAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix, GA_color transparent )
#        void            (* DstTransBlt)( N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix, GA_color transparent )
#        void            (* DstTransBltLin)( N_int32 srcOfs, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix, GA_color transparent )
#        void            (* DstTransBltSys)( void *srcAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix, GA_color transparent, N_int32 flipY )
#        void            (* DstTransBltBM)( void *srcAddr, N_int32 srcPhysAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix, GA_color transparent )
#        void            (* StretchBlt)( N_int32 srcLeft, N_int32 srcTop, N_int32 srcWidth, N_int32 srcHeight, N_int32 dstLeft, N_int32 dstTop, N_int32 dstWidth, N_int32 dstHeight, N_int32 doClip, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom, N_int32 mix )
#        void            (* StretchBltLin)( N_int32 srcOfs, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 srcWidth, N_int32 srcHeight, N_int32 dstLeft, N_int32 dstTop, N_int32 dstWidth, N_int32 dstHeight, N_int32 doClip, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom, N_int32 mix )
#        void            (* StretchBltSys)( void *srcAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 srcWidth, N_int32 srcHeight, N_int32 dstLeft, N_int32 dstTop, N_int32 dstWidth, N_int32 dstHeight, N_int32 doClip, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom, N_int32 mix, N_int32 flipY )
#        void            (* StretchBltBM)( void *srcAddr, N_int32 srcPhysAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 srcWidth, N_int32 srcHeight, N_int32 dstLeft, N_int32 dstTop, N_int32 dstWidth, N_int32 dstHeight, N_int32 doClip, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom, N_int32 mix )
#        N_int32         (* ConvertBltSys_Obsolete)( void *srcAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 bitsPerPixel, GA_pixelFormat *pixelFormat, GA_palette *dstPal, GA_palette *srcPal, N_int32 dither, N_int32 mix, N_int32 flipY )
#        N_int32         (* ConvertBltBM_Obsolete)( void *srcAddr, N_int32 srcPhysAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 bitsPerPixel, GA_pixelFormat *pixelFormat, GA_palette *dstPal, GA_palette *srcPal, N_int32 dither, N_int32 mix )
#        N_int32         (* StretchConvertBltSys_Obsolete)( void *srcAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 srcWidth, N_int32 srcHeight, N_int32 dstLeft, N_int32 dstTop, N_int32 dstWidth, N_int32 dstHeight, N_int32 doClip, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom, N_int32 bitsPerPixel, GA_pixelFormat *pixelFormat, GA_palette *dstPal, GA_palette *srcPal, N_int32 dither, N_int32 mix, N_int32 flipY )
#        N_int32         (* StretchConvertBltBM_Obsolete)( void *srcAddr, N_int32 srcPhysAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 srcWidth, N_int32 srcHeight, N_int32 dstLeft, N_int32 dstTop, N_int32 dstWidth, N_int32 dstHeight, N_int32 doClip, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom, N_int32 bitsPerPixel, GA_pixelFormat *pixelFormat, GA_palette *dstPal, GA_palette *srcPal, N_int32 dither, N_int32 mix )
#        N_int32         (* BitBltFxTest)( GA_bltFx *fx )
#        void            (* BitBltFx)( N_int32 srcLeft, N_int32 srcTop, N_int32 srcWidth, N_int32 srcHeight, N_int32 dstLeft, N_int32 dstTop, N_int32 dstWidth, N_int32 dstHeight, GA_bltFx *fx )
#        void            (* BitBltFxLin)( N_int32 srcOfs, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 srcWidth, N_int32 srcHeight, N_int32 dstLeft, N_int32 dstTop, N_int32 dstWidth, N_int32 dstHeight, GA_bltFx *fx )
#        void            (* BitBltFxSys)( void *srcAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 srcWidth, N_int32 srcHeight, N_int32 dstLeft, N_int32 dstTop, N_int32 dstWidth, N_int32 dstHeight, GA_bltFx *fx )
#        void            (* BitBltFxBM)( void *srcAddr, N_int32 srcPhysAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 srcWidth, N_int32 srcHeight, N_int32 dstLeft, N_int32 dstTop, N_int32 dstWidth, N_int32 dstHeight, GA_bltFx *fx )
#        void            (* GetBitmapSys)( void *dstAddr, N_int32 dstPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix )
#        void            (* GetBitmapBM)( void *dstAddr, N_int32 dstPhysAddr, N_int32 dstPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_int32 mix )
        void            (* UpdateScreen)( N_int32 left, N_int32 top, N_int32 width, N_int32 height )
        N_int32         (* DrawClippedLineInt)( N_int32 x1, N_int32 y1, N_int32 x2, N_int32 y2, N_int32 drawLast, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom )
#        N_int32         (* DrawClippedBresenhamLine)( N_int32 x1, N_int32 y1, N_int32 initialError, N_int32 majorInc, N_int32 diagInc, N_int32 count, N_int32 flags, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom )
#        N_int32         (* DrawClippedStippleLineInt)( N_int32 x1, N_int32 y1, N_int32 x2, N_int32 y2, N_int32 drawLast, N_int32 transparent, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom )
#        N_int32         (* DrawClippedBresenhamStippleLine)( N_int32 x1, N_int32 y1, N_int32 initialError, N_int32 majorInc, N_int32 diagInc, N_int32 count, N_int32 flags, N_int32 transparent, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom )
#        void            (* BitBltPlaneMasked)( N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_uint32 planeMask )
#        void            (* BitBltPlaneMaskedLin)( N_int32 srcOfs, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_uint32 planeMask )
#        void            (* BitBltPlaneMaskedSys)( void *srcAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_uint32 planeMask, N_int32 flipY )
#        void            (* BitBltPlaneMaskedBM)( void *srcAddr, N_int32 srcPhysAddr, N_int32 srcPitch, N_int32 srcLeft, N_int32 srcTop, N_int32 width, N_int32 height, N_int32 dstLeft, N_int32 dstTop, N_uint32 planeMask )
#        void            (* DrawRectLin)( N_int32 dstOfs, N_int32 dstPitch, N_int32 left, N_int32 top, N_int32 width, N_int32 height, GA_color color, N_int32 mix )
#        void            (* DrawRectExt)( N_int32 left, N_int32 top, N_int32 width, N_int32 height, GA_color color, N_int32 mix )
#        void            (* DrawStyleLineInt)( N_int32 x1, N_int32 y1, N_int32 x2, N_int32 y2, N_int32 drawLast, N_int32 transparent )
#        void            (* DrawBresenhamStyleLine)( N_int32 x1, N_int32 y1, N_int32 initialError, N_int32 majorInc, N_int32 diagInc, N_int32 count, N_int32 flags, N_int32 transparent )
#        N_int32         (* DrawClippedStyleLineInt)( N_int32 x1, N_int32 y1, N_int32 x2, N_int32 y2, N_int32 drawLast, N_int32 transparent, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom )
#        N_int32         (* DrawClippedBresenhamStyleLine)( N_int32 x1, N_int32 y1, N_int32 initialError, N_int32 majorInc, N_int32 diagInc, N_int32 count, N_int32 flags, N_int32 transparent, N_int32 clipLeft, N_int32 clipTop, N_int32 clipRight, N_int32 clipBottom )


    ctypedef struct GA_devCtx:
        N_uint32        Version
        N_uint32        DriverRev
        char            OemVendorName[80]
        char            OemCopyright[80]
        N_uint16        *AvailableModes
        N_int32         DeviceIndex
        N_uint32        TotalMemory
        N_uint32        Attributes
        N_uint32        WorkArounds
        N_uint32        TextSize
        N_uint32        TextBasePtr
        N_uint32        BankSize
        N_uint32        BankedBasePtr
        N_uint32        LinearSize
        N_uint32        LinearBasePtr
        N_uint32        ZBufferSize
        N_uint32        ZBufferBasePtr
        N_uint32        TexBufferSize
        N_uint32        TexBufferBasePtr
        N_uint32        LockedMemSize
        N_uint32        IOBase
        N_uint32        MMIOBase[4]
        N_uint32        MMIOLen[4]
        void            *DriverStart
        N_uint32        DriverSize
        N_uint32        BusType
        N_uint32        AttributesExt
        N_uint32        Shared

        # Near pointers mapped by loader for driver
#        void            *IOMemMaps[4]
#        void            *TextMem
#        void            *BankedMem
#        void            *LinearMem
#        void            *ZBufferMem
#        void            *TexBufferMem
#        void            *LockedMem
#        N_physAddr       LockedMemPhys
#        void            *TextFont8x8
#        void            *TextFont8x14
#        void            *TextFont8x16
#        GA_palette      *VGAPal4
#        GA_palette      *VGAPal8


    ibool GA_queryFunctions( GA_devCtx *dc, N_uint32 id, void *funcs )
    GA_devCtx * GA_loadDriver( N_int32 deviceIndex, N_int32 shared )
    int GA_enumerateDevices( N_int32 shared )
    char *GA_errorMsg( N_int32 status )
    int GA_status()
    void GA_unloadDriver( GA_devCtx *dc )


cdef class Driver:
    cdef GA_devCtx *_context
    cdef readonly object AvailableModes

cdef class InitFuncs:
    cdef GA_initFuncs _funcs

cdef class DriverFuncs:
    cdef GA_driverFuncs _funcs

cdef class TwoDStateFuncs:
    cdef GA_2DStateFuncs _funcs

cdef class TwoDRenderFuncs:
    cdef GA_2DRenderFuncs _funcs

cdef class ModeInfo:
    cdef GA_modeInfo _info

cdef class ConfigInfo:
    cdef GA_configInfo _info
