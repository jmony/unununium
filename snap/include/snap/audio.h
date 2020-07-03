/****************************************************************************
*
*                     SciTech SNAP Audio Architecture
*
*  ========================================================================
*
*   Copyright (C) 1991-2004 SciTech Software, Inc. All rights reserved.
*
*   This file may be distributed and/or modified under the terms of the
*   GNU General Public License version 2.0 as published by the Free
*   Software Foundation and appearing in the file LICENSE.GPL included
*   in the packaging of this file.
*
*   Licensees holding a valid Commercial License for this product from
*   SciTech Software, Inc. may use this file in accordance with the
*   Commercial License Agreement provided with the Software.
*
*   This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING
*   THE WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR
*   PURPOSE.
*
*   See http://www.scitechsoft.com/license/ for information about
*   the licensing options available and how to purchase a Commercial
*   License Agreement.
*
*   Contact license@scitechsoft.com if any conditions of this licensing
*   are not clear to you, or you have questions about licensing options.
*
*  ========================================================================
*
* Language:     ANSI C
* Environment:  Any 32-bit protected mode environment
*
* Description:  Header file for the SciTech SNAP Audio Architecture
*               device driver Hardware Abstraction Layer.
*
****************************************************************************/

#ifndef __SNAP_AUDIO_H
#define __SNAP_AUDIO_H

#include "snap/common.h"
#include "clib/peloader.h"
#include "ztimerc.h"

/*---------------------- Macros and type definitions ----------------------*/

#pragma pack(1)

/* Signature for the audio driver file */

#define AA_SIGNATURE        "AUDIO"

/* Define the interface version */

#define AA_VERSION          0x100

/* Define the maximum number of devices supported. Internally we can handle
 * any number, so if you need more than this many devices let us know and
 * we can build custom drivers that support more devices.
 */

#define AA_MAX_DEVICES          4

/****************************************************************************
REMARKS:
This enumeration defines the identifiers used to obtain the device context
function group pointer structures. As new features and capabilities are
added to the future versions of the specification, new identifiers will
be added to extract new function pointers from the drivers.

The AA_GET_FIRST_OEM defines the first identifier for OEM extensions. OEM's
are free to added their own private functional extensions to the drivers
as desired. Note that OEM's must verify the presence of their OEM drivers
via the the OemVendorName string before attempting to use OEM extension
functions.

HEADER:
snap/audio.h

MEMBERS:
AA_GET_INITFUNCS        - Get AA_initFuncs structure
AA_GET_PLAYBACKFUNCS    - Get AA_playbackFuncs structure
AA_GET_RECORDFUNCS      - Get AA_recordFuncs structure
AA_GET_MIDIFUNCS        - Get AA_midiFuncs structure
AA_GET_VOLUMEFUNCS      - Get AA_volumeFuncs structure
AA_GET_MIXERFUNCS       - Get AA_mixerFuncs structure
AA_GET_3DFUNCS          - Get AA_3DFuncs structure
AA_GET_FIRST_OEM        - ID of first OEM extension function
****************************************************************************/
typedef enum {
    AA_GET_INITFUNCS,
    AA_GET_PLAYBACKFUNCS,
    AA_GET_RECORDFUNCS,
    AA_GET_MIDIFUNCS,
    AA_GET_VOLUMEFUNCS,
    AA_GET_MIXERFUNCS,
    AA_GET_3DFUNCS,
    AA_GET_FIRST_OEM                = 0x00010000,
    } AA_funcGroupsType;

/****************************************************************************
REMARKS:
Flags for the Attributes member of the main AA_devCtx device context block
structure. These flags define the hardware capabilities of the particular
device.

The aaHaveDigital8Bit flag is used to determine if the device supports
8-bit digital audio.

The aaHaveDigital16Bit flag is used to determine if the device supports
16-bit digital audio.

The aaHaveDigitalStereo flag is used to dertemine if the device supports
stereo digital audio.

The aaHaveDigitalPlayback flag is used to determine if the device supports
hardware digital audio playback capabilities.

The aaHaveDigitalRecord flag is used to determine if the device supports
hardware digital audio recording capabilities.

The aaHaveDigitalAsync flag is used to determine if the device supports
hardware digital audio playback and recording at the same time. This is
sometime referred to as full duplex recording.

The aaHaveMultipleRecord flag is used to determine if the device supports
recording from multiple signal sources at the same time. If this flag is
not set, you can only enable one input signal at a time via the SelectInput
function. Otherwise you can enable multiple inputs and they will be
mixed together based on the settings of their respective volume controls.

The aaHaveWaveTable flag is used to determine if the device supports
hardware wave table output for music synthensis.

The aaHaveMIDIOut flag is used to determine if the device supports MIDI
output functionality.

The aaHaveMIDIIn flag is used to determine if the device supports MIDI
input functionality.

The aaHaveMIDIThru flag is used to determine if the device supports MIDI
through functionality.

The aaHaveMIDIAsync flag is used to determine if the device supports MIDI
input and output functionality at the same time.

The aaHaveHardwareVolume flag is used to determine if the device supports
hardware volume control (or input/output mixing).

The aaHaveHardwareMixing flag is used to determine if the device supports
hardware mixing of multiple audio streams together.

The aaHaveHardware3D flag is used to determine if the device supports
hardware 3D positional audio functionality.

HEADER:
snap/audio.h

MEMBERS:
aaHaveDigital8Bit       - 8-bit digital audio capability
aaHaveDigital16Bit      - 16-bit digital audio capability
aaHaveDigitalStereo     - Stereo digital audio capability
aaHaveDigitalPlayback   - Digital audio playback is supported
aaHaveDigitalRecord     - Digital audio record is supported
aaHaveDigitalAsync      - Digital audio playback and record at same time
aaHaveMultipleRecord    - Recording from multiple sources is supported
aaHaveWaveTable         - Wave table digital audio is supported
aaHaveMIDIOut           - MIDI output is supported
aaHaveMIDIIn            - MIDI input in supported
aaHaveMIDIThru          - MIDI through is supported
aaHaveMIDIAsync         - MIDI input and output at the same time
aaHaveHardwareMixing    - Hardware mixing is suppored
aaHaveHardware3D        - Hardware 3D is supported
aaHaveDigitalAudio      - Mask to determine if digital audio is supported
aaHaveMIDIAudio         - Mask to determine if MIDI audio is supported
****************************************************************************/
typedef enum {
    aaHaveDigital8Bit               = 0x00000001,
    aaHaveDigital16Bit              = 0x00000002,
    aaHaveDigitalStereo             = 0x00000004,
    aaHaveDigitalPlayback           = 0x00000008,
    aaHaveDigitalRecord             = 0x00000010,
    aaHaveDigitalAsync              = 0x00000020,
    aaHaveMultipleRecord            = 0x00000040,
    aaHaveWaveTable                 = 0x00000080,
    aaHaveMIDIOut                   = 0x00000100,
    aaHaveMIDIIn                    = 0x00000200,
    aaHaveMIDIThru                  = 0x00000400,
    aaHaveMIDIAsync                 = 0x00000800,
    aaHaveHardwareVolume            = 0x00001000,
    aaHaveHardwareMixing            = 0x00002000,
    aaHaveHardware3D                = 0x00004000,
    aaHaveDigitalAudio              = aaHaveDigital8Bit | aaHaveDigital16Bit,
    aaHaveMIDIAudio                 = aaHaveMIDIOut | aaHaveMIDIIn
    } AA_AttributeFlagsType;

/****************************************************************************
REMARKS:
Flags for the LockedMemFlags member of the main AA_devCtx device context
block structure. These flags define the requirements for the locked
physical memory needed by the driver for DMA operations.

HEADER:
snap/audio.h

MEMBERS:
aaDMABelow16M   - Locked DMA memory buffer must be below 16Mb memory mark
****************************************************************************/
typedef enum {
    aaDMABelow16M                   = 0x00000001,
    } AA_LockedMemFlagsType;

/****************************************************************************
REMARKS:
Flags for the Flags member of the AA_digitalInfo structure. These flags
define the capabilities of the different hardware audio formats supported
directly by the hardware device. Individual supported formats are
enumerated in the DigitalInfo member of the main AA_devCtx structure.

HEADER:
snap/audio.h

MEMBERS:
aaDigital8Bit       - 8-bit digital audio capability
aaDigital16Bit      - 16-bit digital audio capability
aaDigitalStereo     - Stereo digital audio capability
aaDigitalRecord     - Digital audio recording is supported
aaDigitalAsync      - Digital audio playback and record at same time
aaDigitalSigned     - Digital audio data is signed
aaDigitalBigEndian  - Format is big-endian
****************************************************************************/
typedef enum {
    aaDigital8Bit                   = 0x00000001,
    aaDigital16Bit                  = 0x00000002,
    aaDigitalStereo                 = 0x00000004,
    aaDigitalRecord                 = 0x00000008,
    aaDigitalAsync                  = 0x00000010,
    aaDigitalSigned                 = 0x00000020,
    aaDigitalBigEndian              = 0x40000000,
    } AA_DigitalFlagsType;

/****************************************************************************
REMARKS:
Flags passed to the SelectOutput function, which is used to select what
outputs are mixed into the final output signal. Even though the hardware
may not specifically support turning off a signal, the driver will
emulate that where necessary by setting the volume to 0. If the hardware
supports disconnecting a source, that will be used to provide the best
signal quality.

NOTE:   You can determine what outputs are supported by examining the list
        of functions returned in the AA_volumeFuncs structure. Trying to
        control an output not supported by the hardware will have no effect.

HEADER:
snap/audio.h

MEMBERS:
aaOutputDigital     - Digital audio output is enabled
aaOutputMIDI        - MIDI output is enabled
aaOutputCD          - CD audio output is enabled
aaOutputLineIn      - Line in is enabled
aaOutputMicrophone  - Microphone is enabled
aaOutputPCSpeaker   - PC speaker is enabled
aaOutputAux1        - Aux 1 input is enabled
aaOutputAux2        - Aux 2 input is enabled
****************************************************************************/
typedef enum {
    aaOutputDigital                 = 0x00000001,
    aaOutputMIDI                    = 0x00000002,
    aaOutputCD                      = 0x00000004,
    aaOutputLineIn                  = 0x00000008,
    aaOutputMicrophone              = 0x00000010,
    aaOutputPCSpeaker               = 0x00000020,
    aaOutputAux1                    = 0x00000040,
    aaOutputAux2                    = 0x00000080,
    } AA_OutputFlagsType;

/****************************************************************************
REMARKS:
Flags passed to the SelectInput function, which is used to select what
inputs are mixed together for digital audio recording. Some combinations
may not be supported by the hardware, so make sure you check the return
status of SelectInput for failure conditions.

NOTE:   You can determine what outputs are supported by examining the list
        of functions returned in the AA_volumeFuncs structure. Trying to
        control an output not supported by the hardware will have no effect.

HEADER:
snap/audio.h

MEMBERS:
aaInputMIDI         - MIDI is enabled for recording
aaInputCD           - CD audio is enabled for recording
aaInputLineIn       - Line in is enabled for recording
aaInputMicrophone   - Microphone is enabled for recording
aaInputAux1         - Aux 1 is enabled for recording
aaInputAux2         - Aux 2 is enabled for recording
****************************************************************************/
typedef enum {
    aaInputMIDI                    = 0x00000001,
    aaInputCD                      = 0x00000002,
    aaInputLineIn                  = 0x00000004,
    aaInputMicrophone              = 0x00000008,
    aaInputAux1                    = 0x00000010,
    aaInputAux2                    = 0x00000020,
    } AA_InputFlagsType;

/****************************************************************************
REMARKS:
Function prototype for interrupt callbacks for audio playback and recording.
This callback is called when the DMA buffer needs to be filled or has been
filled. The buffer parameter will be 0 or 1 depending on which half of
the DMA buffer currently needs to be filled (playback mode) or has just been
filled (record mode).

NOTE:   The DMA buffer callback /will/ be called at interrupt time from
        within the driver, so it must be locked in memory and be addressable
        from an interrupt context. Any memory or variables it accesses
        must also be locked in memory and be addressable from an interrupt
        context.

HEADER:
snap/audio.h
****************************************************************************/
typedef (NAPIP AA_DMACallback)(N_int32 buffer);

/****************************************************************************
REMARKS:
Structure defining the different digital audio formats supported by the
hardware. The flags field contains the information about the type of
format being enumerated, and will be a combination of the flags defined
in the AA_DigitalFlagsType enumeration.

HEADER:
snap/audio.h

MEMBERS:
MinPhysRate - Minimum physical sample rate supported by this format
NomPhysRate - Nominal physical sample rate supported by this format
MaxPhysRate - Maximum physical sample rate supported by this format
MinHalfSize - Minimum half buffer size for DMA transfers
MaxHalfSize - Maximum half buffer size for DMA transfers
Flags       - Flags for this format
****************************************************************************/
typedef struct {
    N_uint16    MinPhysRate;
    N_uint16    NomPhysRate;
    N_uint16    MaxPhysRate;
    N_int32     MinHalfSize;
    N_int32     MaxHalfSize;
    N_uint32    Flags;
    } AA_digitalInfo;

/****************************************************************************
REMARKS:
Structure returned by GetConfigInfo, which contains configuration
information about the installed audio hardware.

Note:   The dwSize member is intended for future compatibility, and
        should be set to the size of the structure as defined in this
        header file. Future drivers will be compatible with older software
        by examiming this value.

HEADER:
snap/audio.h

MEMBERS:
dwSize              - Set to size of structure in bytes
ManufacturerName    - Name of audio chipset manufacturer
ChipsetName         - Name of audio chipset name
VersionInfo         - String representation of version and build for driver
BuildDate           - String representation of the build date for driver
Certified           - True if the driver is certified
CertifiedDate       - Date that the driver was certified
CertifiedVersion    - Version info for certification program used
****************************************************************************/
typedef struct {
    N_uint32    dwSize;
    char        ManufacturerName[80];
    char        ChipsetName[80];
    char        VersionInfo[80];
    char        BuildDate[80];
    char        Certified;
    char        CertifiedDate[80];
    char        CertifiedVersion[80];
    } AA_configInfo;

/****************************************************************************
REMARKS:
Parameter block to describe the audio driver IO configuration parameters.

The IOBase member contains the I/O base addresses for up to 4 individual
I/O addresses used by the driver for accessing the hardware I/O registers.

The IRQHook member contains the IRQ number of the device to be used for
handling hardware interrupts from the device.

The DMA8Bit member contains the 8-bit DMA channel used by the driver.
This is for legacy ISA bus based devices that use the old PC/AT DMA
controller. Newer PCI devices will leave these fields as zeros.

The DMA16Bit member contains the 16-bit DMA channel used by the driver.
This is for legacy ISA bus based devices that use the old PC/AT DMA
controller. Newer PCI devices will leave these fields as zeros.

HEADER:
snap/audio.h

MEMBERS:
IOBase              - Base addresses for I/O mapped registers
IRQHook             - Hardware interrupt to hook for driver
DMA8Bit             - 8-bit DMA channel to use
DMA16Bit            - 16-bit DMA channel to use
****************************************************************************/
typedef struct {
    N_uint32        IOBase[4];
    N_uint32        IRQHook;
    N_uint32        DMA8Bit;
    N_uint32        DMA16Bit;
    } AA_IOParams;

/****************************************************************************
REMARKS:
Structure returned by GetOptions, which contains configuration
information about the options for the installed device driver. All the
boolean configuration options are enabled by default and can be optionally
turned off by the user via the configuration functions.

Note:   The dwSize member is intended for future compatibility, and
        should be set to the size of the structure as defined in this
        header file. Future drivers will be compatible with older software
        by examiming this value.

HEADER:
snap/audio.h

MEMBERS:
dwSize              - Set to size of structure in bytes
bDigitalAudio       - True if digital audio is enabled
bDigital8Bit        - True if 8-bit digital output is enabled
bDigital16Bit       - True if 16-bit digital output is enabled
bDigitalStereo      - True if stereo digital output is enabled
bDigitalPlayback    - True if digital playback is enabled
bDigitalRecord      - True if digital recording is enabled
bWaveTable          - True if wave table audio is enabled
bMIDIAudio          - True if MIDI audio is enabled
bMIDIOut            - True if MIDI Out is enabled
bMIDIIn             - True if MIDI In is enabled
bMIDIThru           - True if MIDI Thru is enabled
bHardwareVolume     - True if hardware volume control is enabled
bHardwareMixing     - True if hardware mixing is enabled
bHardware3D         - True if hardware 3D mixing is enabled
OutputSelect        - Current output select mask
InputSelect         - Current input select mask
MasterVolume        - User default master volume
DigitalVolume       - User default digital volume
MIDIVolume          - User default MIDI volume
CDVolume            - User default CD volume
LineInVolume        - User default line in volume
MicrophoneVolume    - User default microphone volume
MicrophoneAGC       - User default microphone AGC setting
PCSpeakerVolume     - User default PC speaker volume
Aux1Volume          - User default aux1 volume
Aux2Volume          - User default aux2 volume
BassVolume          - User default bass volume
TrebleVolume        - User default treble volume
InputGain           - User default input gain
OutputGain          - User default output gain
****************************************************************************/
typedef struct {
    N_uint32        dwSize;
    N_uint8         bDigitalAudio;
    N_uint8         bDigital8Bit;
    N_uint8         bDigital16Bit;
    N_uint8         bDigitalStereo;
    N_uint8         bDigitalPlayback;
    N_uint8         bDigitalRecord;
    N_uint8         bWaveTable;
    N_uint8         bMIDIAudio;
    N_uint8         bMIDIOut;
    N_uint8         bMIDIIn;
    N_uint8         bMIDIThru;
    N_uint8         bHardwareVolume;
    N_uint8         bHardwareMixing;
    N_uint8         bHardware3D;
    } AA_options;

#define AA_FIRST_OPTION     bDigitalAudio
#define AA_LAST_OPTION      bHardware3D

/****************************************************************************
REMARKS:
Main audio device context structure. This structure consists of a header
block that contains configuration information about the graphic device,
as well as detection information and runtime state information.

The Signature member is filled with the null terminated string 'AUDIO\0'
by the driver implementation. This can be used to verify that the file loaded
really is an audio device driver.

The Version member is a BCD value which specifies what revision level of the
audio specification is implemented in the driver. The high byte specifies
the major version number and the low byte specifies the minor version number.
For example, the BCD value for version 1.0 is 0x100 and the BCD value for
version 2.2 would be 0x202.

The DriverRev member specifies the driver revision level, and is used by the
driver configuration software to determine which version was used to generate
the driver file.

The OemVendorName member contains the name of the vendor that developed the
device driver implementation, and can be up to 80 characters in length.

The OemCopyright member contains a copyright string for the vendor that
developed the device driver implementation and may be up to 80 characters
in length.

The Attributes member contains a number of flags that describes certain
important characteristics of the audio controller.

The MMIOBase member contains the 32-bit physical base addresses pointing
to the start of up to 4 separate memory mapped register areas required by the
controller. The MMIOLen member contains the lengths of each of these
memory mapped IO areas in bytes. When the application maps the memory mapped
IO regions for the driver, the linear address of the mapped memory areas will
then be stored in the corresponding entries in the IOMemMaps array, and will
be used by the driver for accessing the memory mapped registers on the
controller. If any of these regions are not required, the MMIOBase
entries will be NULL and do not need to be mapped by the application.

The LockedMemSize contains the amount of locked, contiguous memory in bytes
that the audio driver requires for programming the hardware. If the audio
devices requires DMA transfers, this member can be set to the length of
the block of memory that is required by the driver. The driver loader code
will attempt to allocate a block of locked, physically contiguous memory
from the operating system and place a pointer to this allocated memory in
the LockedMem member for the driver, and the physical address of the start
of this memory block in LockedMemPhys. Note that the memory must be locked
so it cannot be paged out do disk, and it must be physically contiguous so
that DMA operations will work correctly across CPU page boundaries. If
the driver does not require DMA memory, this value should be set to 0.

The LockedMemFlags contains flags that define any special requirements
for the locked physical memory block, such as whether it needs to be
allocated below the 16Mb physical memory limit.

The IO member contains a structure describing the current I/O configuration
used by the driver.

The CommonIOConfig member is a pointer to list of common IO configurations
encountered for this device. This list is used by the device auto detection
code to attempt to determine the IO parameters automatically for legacy
ISA based audio devices. This field will be NULL for PCI audio devices.

The NumCommonIOConfig member is the number of common I/O configurations,
which indicates how many common IO configurations are listed in the
CommonIOConfig member. This field will be 0 for PCI audio devices.

The ServiceRate member is the rate (in Hz) required for the timer service
callback for the driver. Most drivers will not need to a periodic serivce
callback, but this is provided for devices that are not interrupt driven
(such as PCMCIA or parallel port devices).

The DriverStart member is a pointer to the start of the driver in memory,
and is used to lock down the driver for interrupt handling so that all the
memory in the driver can be accessed at interrupt time.

The DriverSize member is the size of the entire driver in memory in bytes,
and is used to lock down the driver in memory for interrupt handling.

The IOMemMaps member contains the mapped linear address of the memory mapped
register regions defined by the MMIOBase and MMIOLen members.

The LockedMem member contains a pointer to the locked DMA memory buffer
allocated for the loaded driver. The audio driver can use this pointer to
write data directly to the DMA buffer before transferring it to the hardware.
If the driver does not require DMA memory, this value will be set to NULL by
the loader.

The LockedMemPhys member contains the 32-bit physical memory address of the
locked DMA buffer memory allocated for the driver. The audio driver can use
this physical address to set up DMA transfer operations for memory contained
within the DMA transfer buffer. If the driver does not require DMA memory,
this value will be set to 0 by the loader.

HEADER:
snap/audio.h

MEMBERS:
Signature           - 'audio\0' 20 byte signature
Version             - Driver Interface Version (2.0)
DriverRev           - Driver revision number
OemVendorName       - Vendor Name string
OemCopyright        - Vendor Copyright string
DeviceIndex         - Device index for the driver when loaded from disk
Attributes          - Driver attributes
MMIOBase            - Base addresses of memory mapped I/O regions
MMIOLen             - Length of memory mapped I/O regions
LockedMemSize       - Amount of locked memory for driver
LockedMemFlags      - Flags for locked physical memory allocation
IO                  - Structure describing the I/O configuration for driver
CommonIOConfig      - Pointer to list of common IO configurations
NumCommonIOConfig   - Number of common I/O configurations
ServiceRate         - Service rate requires for timer service callback
DriverStart         - Pointer to the start of the driver in memory
DriverSize          - Size of the entire driver in memory in bytes
IOMemMaps           - Pointers to mapped I/O memory
LockedMem           - Ptr to allocated locked memory
LockedMemPhys       - Physical addr of locked memory
StartDMA            - Callback to OS to start a DMA transfer
****************************************************************************/
typedef struct {
    /*------------------------------------------------------------------*/
    /* Device driver header block                                       */
    /*------------------------------------------------------------------*/
    char            Signature[20];
    N_uint32        Version;
    N_uint32        DriverRev;
    AA_digitalInfo  *DigitalInfo;
    char            OemVendorName[80];
    char            OemCopyright[80];
    N_int32         DeviceIndex;
    N_uint32        Attributes;
    N_uint32        MMIOBase[4];
    N_uint32        MMIOLen[4];
    N_uint32        LockedMemSize;
    N_uint32        LockedMemFlags;
    AA_IOParams     IO;
    AA_IOParams     *CommonIOConfig;
    N_int32         NumCommonIOConfig;
    N_int32         ServiceRate;
    void            *DriverStart;
    N_uint32        DriverSize;
    N_uint32        res1[20];

    /*------------------------------------------------------------------*/
    /* Near pointers mapped by loader for driver                        */
    /*------------------------------------------------------------------*/
    void            _FAR_ *IOMemMaps[4];
    void            _FAR_ *LockedMem;
    void            _FAR_ *DMABufferA;
    void            _FAR_ *DMABufferB;
    N_uint32        LockedMemPhys;
    N_uint32        DMABufferAPhys;
    N_uint32        DMABufferBPhys;
    N_uint32        DMABufferSize;
    N_uint32        res2[20];

    /*------------------------------------------------------------------*/
    /* Callbacks to OS provided services                                */
    /*------------------------------------------------------------------*/
    void            (NAPIP StartDMA)(int channel,...);
    N_uint32        res3[20];

    /*------------------------------------------------------------------*/
    /* Driver initialization functions                                  */
    /*------------------------------------------------------------------*/
    N_int32         (NAPIP VerifyIOConfig)(AA_IOParams *IOParams);
    N_int32         (NAPIP OpenDevice)(void);
    void            (NAPIP CloseDevice)(void);
    void            (NAPIP ServiceHandler)(void);
    ibool           (NAPIP QueryFunctions)(N_uint32 id,N_int32 safetyLevel,void _FAR_ *funcs);
    } AA_devCtx;

/****************************************************************************
REMARKS:
Main device driver init functions, including setup and initialisation
functions.
{secret}
****************************************************************************/
typedef struct {
    N_uint32    dwSize;
    void        (NAPIP GetConfigInfo)(AA_configInfo *info);
    void        (NAPIP GetOptions)(AA_options *options);
    void        (NAPIP SetOptions)(AA_options *options);
    void        (NAPIP GetUniqueFilename)(char *filename,int type);
    } AA_initFuncs;

/****************************************************************************
REMARKS:
Device driver hardware digital audio playback functions.
{secret}
****************************************************************************/
typedef struct {
    N_uint32    dwSize;
    ibool       (NAPIP SetPlaybackMode)(N_int32 *sampleRate,N_int32 flags);
    void        (NAPIP StartPlayback)(N_int32 halfBufferSize,AA_DMACallback bufferEmpty,N_int32 restart);
    N_uint32    (NAPIP GetPlaybackPosition)(void);
    void        (NAPIP StopPlayback)(void);
    void        (NAPIP BufferFillCallback)(void);
    } AA_playbackFuncs;

/****************************************************************************
REMARKS:
Device driver hardware digital audio record functions.
{secret}
****************************************************************************/
typedef struct {
    N_uint32    dwSize;
    ibool       (NAPIP SetRecordMode)(N_int32 *sampleRate,N_int32 flags);
    void        (NAPIP StartRecord)(N_int32 halfBufferSize,AA_DMACallback bufferFull,N_int32 restart);
    N_uint32    (NAPIP GetRecordPosition)(void);
    void        (NAPIP StopRecord)(void);
    } AA_recordFuncs;

/****************************************************************************
REMARKS:
Device driver hardware MIDI functions go in here.
{secret}
****************************************************************************/
typedef struct {
    N_uint32    dwSize;
    } AA_MIDIFuncs;

/****************************************************************************
REMARKS:
Device driver hardware mixer functions.
{secret}
****************************************************************************/
typedef struct {
    N_uint32    dwSize;
    void        (NAPIP SelectOutput)(N_uint32 mask);
    N_uint32    (NAPIP GetOutputSelect)(void);
    ibool       (NAPIP SelectInput)(N_uint32 mask);
    N_uint32    (NAPIP GetInputSelect)(void);
    void        (NAPIP SetMasterVolume)(N_uint8 left,N_uint8 right);
    void        (NAPIP GetMasterVolume)(N_uint8 *left,N_uint8 *right);
    void        (NAPIP SetDigitalVolume)(N_uint8 left,N_uint8 right);
    void        (NAPIP GetDigitalVolume)(N_uint8 *left,N_uint8 *right);
    void        (NAPIP SetMIDIVolume)(N_uint8 left,N_uint8 right);
    void        (NAPIP GetMIDIVolume)(N_uint8 *left,N_uint8 *right);
    void        (NAPIP SetCDVolume)(N_uint8 left,N_uint8 right);
    void        (NAPIP GetCDVolume)(N_uint8 *left,N_uint8 *right);
    void        (NAPIP SetLineInVolume)(N_uint8 left,N_uint8 right);
    void        (NAPIP GetLineInVolume)(N_uint8 *left,N_uint8 *right);
    void        (NAPIP SetMicrophoneVolume)(N_uint8 volume);
    void        (NAPIP GetMicrophoneVolume)(N_uint8 *volume);
    void        (NAPIP SetMicrophoneAGC)(N_int32 enable);
    void        (NAPIP GetMicrophoneAGC)(N_int32 *enable);
    void        (NAPIP SetPCSpeakerVolume)(N_uint8 volume);
    void        (NAPIP GetPCSpeakerVolume)(N_uint8 *volume);
    void        (NAPIP SetAux1Volume)(N_uint8 left,N_uint8 right);
    void        (NAPIP GetAux1Volume)(N_uint8 *left,N_uint8 *right);
    void        (NAPIP SetAux2Volume)(N_uint8 left,N_uint8 right);
    void        (NAPIP GetAux2Volume)(N_uint8 *left,N_uint8 *right);
    void        (NAPIP SetBassVolume)(N_uint8 left,N_uint8 right);
    void        (NAPIP GetBassVolume)(N_uint8 *left,N_uint8 *right);
    void        (NAPIP SetTrebleVolume)(N_uint8 left,N_uint8 right);
    void        (NAPIP GetTrebleVolume)(N_uint8 *left,N_uint8 *right);
    void        (NAPIP SetInputGain)(N_uint8 left,N_uint8 right);
    void        (NAPIP GetInputGain)(N_uint8 *left,N_uint8 *right);
    void        (NAPIP SetOutputGain)(N_uint8 left,N_uint8 right);
    void        (NAPIP GetOutputGain)(N_uint8 *left,N_uint8 *right);
    } AA_volumeFuncs;

/****************************************************************************
REMARKS:
Device driver hardware mixer functions.
{secret}
****************************************************************************/
typedef struct {
    N_uint32    dwSize;
    } AA_mixerFuncs;

/****************************************************************************
REMARKS:
Device driver hardware 3D audio functions.
{secret}
****************************************************************************/
typedef struct {
    N_uint32    dwSize;
    } AA_3DFuncs;

/****************************************************************************
REMARKS:
Structure defining all the SciTech SNAP Audio API functions as exported from
the Binary Portable DLL.
{secret}
****************************************************************************/
typedef struct {
    ulong           dwSize;
    int             (NAPIP AA_status)(void);
    const char *    (NAPIP AA_errorMsg)(N_int32 status);
    int             (NAPIP AA_getDaysLeft)(void);
    int             (NAPIP AA_registerLicense)(uchar *license);
    int             (NAPIP AA_enumerateDevices)(void);
    AA_devCtx *     (NAPIP AA_loadDriver)(N_int32 deviceIndex);
    void            (NAPIP AA_unloadDriver)(AA_devCtx *dc);
    void            (NAPIP AA_saveOptions)(AA_devCtx *dc,AA_options *options);
    } AA_exports;

/****************************************************************************
REMARKS:
Structure defining all the SciTech SNAP Audio API functions as imported into
the Binary Portable DLL.
{secret}
****************************************************************************/
typedef struct {
    ulong           dwSize;
#ifndef __INTEL__
    uchar           (NAPIP outpb)(ulong port,uchar val);
    ushort          (NAPIP outpw)(ulong port,ushort val);
    ulong           (NAPIP outpd)(ulong port,ulong val);
    uchar           (NAPIP inpb)(ulong port);
    ushort          (NAPIP inpw)(ulong port);
    ulong           (NAPIP inpd)(ulong port);
#endif
    } AA_imports;

/****************************************************************************
REMARKS:
Function pointer type for the Binary Portable DLL initialisation entry point.
{secret}
****************************************************************************/
typedef AA_exports * (NAPIP AA_initLibrary_t)(const char *path,const char *bpdname,PM_imports *pmImp,N_imports *nImp,AA_imports *gaImp);

#pragma pack()

/*-------------------------- Function Prototypes --------------------------*/

#ifdef  __cplusplus
extern "C" {            /* Use "C" linkage when in C++ mode */
#endif

/* Error handling functions for SciTech SNAP Audio drivers */

int             NAPI AA_status(void);
const char *    NAPI AA_errorMsg(N_int32 status);

/* Function to get the number of days left in evaluation period */

int             NAPI AA_getDaysLeft(void);

/* Utility function to register a linkable library license */

int             NAPI AA_registerLicense(uchar *license);

/* Utility functions to load an audio driver and initialise it */

int             NAPI AA_enumerateDevices(void);
AA_devCtx *     NAPI AA_loadDriver(N_int32 deviceIndex);
void            NAPI AA_unloadDriver(AA_devCtx *dc);
void            NAPI AA_saveOptions(AA_devCtx *dc,AA_options *options);

/* Utility functions to force the I/O configuration for a device. If you
 * force the I/O parameters for a secondary ISA sound device,
 * AA_enumerateDevices will enumerate those devices automatically. Using
 * these functions is the only way to get multiple ISA sound cards
 * working, as auto-detection is not possible for secondary sound cards
 * (except where PnP is supported). Forcing the I/O configuration for
 * a primary ISA device is only necessary if we can't auto-detect it.
 */

char **         NAPI AA_enumerateISADrivers(void);
void            NAPI AA_setIOParams(char *deviceName,N_int32 deviceIndex,AA_IOParams *IO);
void            NAPI AA_unsetIOParams(char *deviceName,N_int32 deviceIndex);

// TODO: Implement the above!

#ifdef  __cplusplus
}                                   /* End of "C" linkage for C++       */
#endif

#endif  /* __SNAP_AUDIO_H */

