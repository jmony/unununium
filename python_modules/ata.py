import block_device
import vfs
import uuu
import struct
import array
import disk_cache
import io
import uuutime


default_irq = {
    0x1f0: 14,
    0x170: 15,
    0x1e8: 11,
    0x168: 10,
    0x1e0: 8,
    0x160: 12
}

class ATAError( Exception ):
    '''Base class for all ATA exceptions.'''

class TimeoutError( ATAError ):
    '''Timeout waiting for interrupt or ready flag.'''

class ProbeError( ATAError ):
    '''Attempt to create a Drive, but the drive is not installed or
    supported.'''

class IsATAPIDeviceError( ProbeError ):
    '''Attempt to create a Drive, but the device is ATAPI.'''



def _reg_property( offset, read=True, write=True ):
    '''Return a property that manipulates the register at `offset`.'''

    if read: fget = lambda self: io.inb( self.io_base+offset )
    else: fget = None

    if write: fset = lambda self, v: io.outb( self.io_base+offset, v )
    else: fset = None

    return property( fget, fset )
        
        


class Controller( object ):
    data_offset = 0
    error_offset = 1
    sector_count_offset = 2
    lba_low_offset = 3
    lba_mid_offset = 4
    lba_high_offset = 5
    device_offset = 6
    status_offset = 7
    command_offset = 7
    #control_offset = 8
    #irq_offset = 9

    cmd_identify = 0xec
    cmd_read_sectors = 0x20

    busy_timeout = 1000000


    def __init__( self, io_base=0x1f0, irq=None ):
        self.io_base = io_base
        if irq is None:
            self.irq = default_irq[io_base]
        else:
            self.irq = irq


    def lock( self ):
        pass


    def unlock( self ):
        pass


    def wait_not_busy( self, drq=None, drdy=None, dsc=None, error=None ):
        '''Wait for BSY in the status register to be set to 0.
        
        The other parameters are used to check that the coresponding bit in the
        status register is in the given state (True or False; do not use
        integers). If not so, ATAError is raised.
        '''
        mask = 0x80
        value = 0x00

        for state, bit in [(drq,0x08), (drdy,0x40), (dsc,0x10), (error,0x01)]:
            if state is not None:
                mask |= bit
                if state:
                    value |= bit

        start = uuutime.get_time()
        while uuutime.get_time() - start < self.busy_timeout:
            r = self.status_reg
            if error is False:
                if r & 0x81 == 0x01:
                    raise ATAError( 'status: 0x%02x' % r )
            if r & mask == value:
                return r
        raise TimeoutError( 'Timeout waiting for ATA controller, status 0x%02x' % r )


    sector_count_reg = _reg_property( sector_count_offset )
    lba_low_reg = _reg_property( lba_low_offset )
    lba_mid_reg = _reg_property( lba_mid_offset )
    lba_high_reg = _reg_property( lba_high_offset )
    status_reg = _reg_property( status_offset, write=False )
    device_reg = _reg_property( device_offset )
    command_reg = _reg_property( command_offset, read=False )
    error_reg = _reg_property( error_offset, write=False )
    data_reg = property(
        lambda self: io.inw( self.io_base+self.data_offset ),
        lambda self, v: io.outw( self.io_base+self.data_offset, v ) )



class Drive( block_device.BlockDevice, vfs.Node ):

    block_size = 512
    allow_write = False
    allow_read = True

    def __init__( self, controller, drive ):
        if drive not in [0,1]:
            raise ValueError( 'invalid drive number' )
        controller.lock()
        try:
            controller.wait_not_busy( drq=False )
            controller.device_reg = drive << 4
            # ATA-6 requires DRDY be true before executing this command, but
            # not all controllers do it.
            # controller.wait_not_busy( drdy=True )
            controller.command_reg = controller.cmd_identify
            probe = array.array('H')
            try:
                controller.wait_not_busy( drq=True, error=False )
            except ATAError:
                # ATA/ATAPI-6 draft says sector count register should be 0x01,
                # but my CDROM returns 0x03. Maybe this is an ATAPI version?
                if controller.lba_low_reg == 0x01 \
                and controller.lba_mid_reg == 0x14 \
                and controller.lba_high_reg == 0xeb:
                    raise IsATAPIDeviceError
                raise ProbeError( 'error while reading identify data' )
            for _ in xrange(256):
                probe.append( controller.data_reg )
            status = controller.wait_not_busy( error=False )
            if status & 0xE9 != 0x40:
                raise ProbeError( 'Error probing drive %i; status 0x%02x, error 0x%02x' % (drive,status,controller.error_reg) )
        finally:
            controller.unlock()
        if probe[0] & 0x80:
            raise ProbeError( 'ATA drive %i is not installed' % drive )
        if not probe[49] & 0x0200:
            raise ProbeError( 'ATA drive %i does not support LBA' % drive )
        self.total_sectors = (probe[61] << 16) + probe[60]
        model_number = ''
        for b in probe[27:47]:
            model_number += chr(b >> 8) + chr(b & 0xff)
        self.model_number = model_number.strip()
        self._controller = controller
        self._drive = drive
        super( Drive, self ).__init__()
        self.filesystem = self


    def read_sectors( self, first, count ):
        'Read any number of sectors from the drive, and return them as a string.'

        if first < 0 or count < 0:
            raise ValueError( 'sector address and count must be positive' )
        if first+count > self.total_sectors:
            raise ValueError( 'request for sectors beyond disk capacity.' )

        self._controller.lock()
        try:
            r = array.array('H')
            while count:
                nsectors = min( count, 256 )
                self._controller.wait_not_busy( drq=False )
                self._controller.sector_count_reg = nsectors & 0xff   # 0 means 256 to ATA
                self._controller.lba_low_reg = first & 0xff
                self._controller.lba_mid_reg = (first >> 8) & 0xff
                self._controller.lba_high_reg = (first >> 16) & 0xff
                self._controller.device_reg = 0xE0 | (self._drive<<4) | ((first >> 24) & 0x0f)
                self._controller.wait_not_busy( drdy=True )
                self._controller.command_reg = self._controller.cmd_read_sectors
                for _ in xrange( nsectors ):
                    status = self._controller.wait_not_busy( drq=True, error=False )
                    if status & 0x01:
                        raise ATAError( 'error while reading sectors' )
                    for _ in xrange( 256 ):
                        r.append( self._controller.data_reg )
                first += nsectors
                count -= nsectors
            status = self._controller.wait_not_busy( error=False )
            if (status & 0xE9) != 0x40:
                raise ATAError( 'read command did not complete correctly; status 0x%02x' % status )
            return r.tostring()
        finally:
            self._controller.unlock()


    def write_sectors( self, first, data ):
        raise IOError( 'ata driver does not support writing' )



class Partition( block_device.BlockDevice, vfs.Node ):

    def __init__( self, drive, start, length ):
        self._offset = start
        self._length = length
        self._drive = drive
        self.block_size = drive.block_size
        self.allow_write = drive.allow_write
        self.allow_read = drive.allow_read
        self.filesystem = drive.filesystem


    def read_sectors( self, first, count ):
        if first < 0 or count < 0:
            raise ValueError( 'sector address and count must be positive' )
        if first+count > self._length:
            raise ValueError( 'request for sectors beyond disk capacity' )
        return self._drive.read_sectors( first+self._offset, count )


    def write_sectors( self, first, data ):
        if first < 0:
            raise ValueError( 'sector address must be positive' )
        count = (len(data)+self.block_size-1) // self.block_size
        if first+count > self._length:
            raise ValueError( 'request for sectors beyond disk capacity' )
        return self._drive.write_sectors( first+self._offset, data )


    def __repr__( self ):
        return '<ata.Partition object at 0x%x, drive 0x%x, %s to %s>' % ( id(self), id(self._drive), self._offset, self._offset+self._length )



def _register_partitions( root_device, device, path, name='' ):

    partition_table = device.read_bytes( 0x1be, 66 )
    signature = partition_table[0x40:]
    if signature != '\x55\xaa':
        return

    for partition in xrange(4):
        flags, start_chs, part_type, end_chs, start_lba, size = struct.unpack(
            '< B 3s B 3s I I',
            partition_table[partition*0x10 : partition*0x10+0x10] )
        if not part_type or not size:
            continue
        if part_type == 0x0f or part_type == 0x05:
            _register_partitions(
                root_device,
                Partition(root_device, start_lba, size),
                path,
                name + str(partition) )
        else:
            uuu.root_vfs.bind( [Partition(root_device, start_lba, size)], path + [name+str(partition)] )



controllers = [ Controller(0x1f0) ]
# use this instead to also probe the secondary controller
#controllers = [ Controller(0x1f0), Controller(0x170) ]

for controller in xrange(len(controllers)):
    for drive in xrange(2):
        hd_path = uuu.dev_path + ['ata',str(controller*2+drive)]
        try:
            node = disk_cache.CachedDisk( Drive(controllers[controller], drive) )
        except IsATAPIDeviceError:
            print '%s: ATAPI device (not supported)' % hd_path
            continue
        except ProbeError:
            continue
        size = node.total_sectors * node.block_size
        if size < 1000:
            size = str(size) + 'B'
        elif size < 1000000:
            size = str(size/1000) + 'kB'
        elif size < 1000000000:
            size = str(size/1000000) + 'MB'
        else:
            size = str(size/1000000000) + 'GB'
        print '%s: %s, %s' % (hd_path, size, node.model_number)
        uuu.root_vfs.bind( [node], hd_path )
        _register_partitions( node, node, hd_path )
