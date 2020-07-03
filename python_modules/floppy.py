import io
import sys
import irq
import uuutime
import block_device
import vfs
import uuu
import disk_cache

_show_errors = True

_tracks = 80
_sectors_per_track = 18
_heads = 2
_total_sectors = _tracks * _sectors_per_track * _heads

_motor_spinup_time = 500000  # µs
_data_timeout = 1000000      # µs
_busy_timeout = 5000000      # µs

_seek_retries = 4        # retry seeks this many times
_rw_retries = 3          # retry read/write this many times
_int_status_retries = 10 # retry interrupt status this many times

_dor_port = 0x3f2
_msr_port = 0x3f4
_data_port = 0x3f5
_ccr_port = 0x3f7

_dor_not_reset = 1 << 2
_dor_dma = 1 << 3
_dor_mota = 1 << 4
_dor_motb = 1 << 5
_dor_motc = 1 << 6
_dor_motd = 1 << 7

_msr_acta = 1 << 0
_msr_actb = 1 << 1
_msr_actc = 1 << 2
_msr_actd = 1 << 3
_msr_busy = 1 << 4
_msr_ndma = 1 << 5
_msr_dio = 1 << 6
_msr_rqm = 1 << 7

_gap_3 = 27       # this is a standard value
_sector_size = 2  # 128 * 2^N (2 is the standard - 512 bytes)

_cmd_read_sectors = 0x46     # read, high desnity
_cmd_write_sectors = 0x45    # write, high desnity
_cmd_int_status = 0x08
_cmd_calibrate = 0x07

_buffer_address = 0x7c00     # let's use the bootloader's memory :)


class FloppyError( Exception ):
    pass

class SeekError( Exception ):
    '''The heads could not be positioned after `_seek_retries` attempts.'''

class IncompleteError( FloppyError ):
    '''A command was accepted, but could not complete.'''

class InvalidCommandError( FloppyError ):
    '''The FDC recieved an invalid command.'''

class NotReadyError( FloppyError ):
    '''The FDC became "not ready" while a command was in progress.'''

class StateError( FloppyError ):
    '''The FDC is in an unexpected state. For example, it's expecting a read on
    the data port, when we expect a write.'''

class TimeoutError( StateError ):
    '''Timeout waiting for interrupt or ready flag.'''



def lba_to_chs( lba ):
  '''Convert a cylinder, head, and sector to an LBA sector. Returns a tuple
  (c,h,s)'''
  c = lba // (_sectors_per_track * _heads)
  s = lba % (_sectors_per_track * _heads)
  h = 0
  if s >= _sectors_per_track:
    h = 1
    s -= _sectors_per_track
  return (c,h,s+1)


class Drive( block_device.BlockDevice, vfs.Node ):

    allow_write = True
    allow_read = True
    block_size = 512
    _current_cyl = None
    _need_calibrate = True

    def __init__( self ):
        self.irq = 6
        irq.monitor( self.irq )
        self.motor_on = False
        self._reset()
        super( Drive, self ).__init__()
        self.filesystem = self


    def read_sectors( self, first, count ):
        'Read any number of sectors from the drive, and return them as a string.'

        if first < 0 or count < 0 or first+count > _total_sectors:
            raise ValueError( 'request for sectors beyond disk capacity' )

        if count == 0:
            return ''

        result = ''
        self.set_motor(True)
        try:
            self._set_datarate( 0 )
            while count:
                while True:
                    # retry the command ignoring errors until the spinup
                    # time has passed. This way no time will be wasted by
                    # waiting too long, and no chance of error exists
                    # because reads are CRC checked.
                    try:
                        result += self._read_sector( *lba_to_chs(first) )
                    except IncompleteError:
                        if uuutime.get_time() - self.motor_on_at > _motor_spinup_time:
                            raise
                    else:
                        break
                first += 1
                count -= 1

            return result
        finally:
            self.set_motor(False)


    def write_sectors( self, first, data ):
        'Write any number of sectors from the drive. `data` must be a multiple of 512 bytes in length.'

        if( len(data) % self.block_size ):
            raise ValueError( 'data must be a multiple of the block size in length' )
        count = len(data) / self.block_size

        if first < 0 or count < 0 or first+count > _total_sectors:
            raise ValueError( 'request for sectors beyond disk capacity' )

        self.set_motor(True)
        try:
            self._set_datarate( 0 )
            data_pos = 0
            while count:
                this_data = data[data_pos:data_pos+512]
                self._write_sector( lba_to_chs(first), this_data )
                first += 1
                count -= 1
                data_pos += 512
        finally:
            self.set_motor(False)


    def set_motor( self, state ):
        if state and (self.motor_on is False):
            io.outb( _dor_port, _dor_not_reset | _dor_dma | _dor_mota )
            self.motor_on_at = uuutime.get_time()
            self.motor_on = True
#        elif (not state) and (self.motor_on is True):
#            io.outb( _dor_port, _dor_not_reset )
#            del self.motor_on_at
#            self.motor_on = False


    def _reset( self ):
        io.outb( _dor_port, 0 )
        io.outb( _dor_port, _dor_not_reset )
        self._set_datarate( 0 )
        for _ in xrange( 4 ):
            self._check_interrupt_status()


    def _write_sector( self, (cyl, head, sector), data ):
        if len(data) != 512:
            raise ValueError( 'data length must be exactly 512 bytes' )
        io.string_to_mem( _buffer_address, data )
        for retry in xrange( _rw_retries ):
            self._seek_heads( cyl )
            self._program_dma( 0x4a, self.block_size, _buffer_address )
            while uuutime.get_time() - self.motor_on_at < _motor_spinup_time:
                pass
            self._wait_not_busy()
            irq.reset( self.irq )
            self._write_data( _cmd_write_sectors )
            self._write_sector_id( cyl, head, sector )
            irq.sleep_until( self.irq )
            st0, st1, st2, _, _, _, _ = self._read_result()
            try:
                self._check_st( st0, st1, st2 )
            except FloppyError, x:
                if retry == _rw_retries-1:
                    raise
                if _show_errors:
                    print 'error writing %i %i %i:' % (cyl, head, sector), x, '(retrying)'
            else:
                return
        assert False


    def _read_sector( self, cyl, head, sector ):
        for retry in xrange( _rw_retries ):
            self._seek_heads( cyl )
            self._program_dma( 0x46, self.block_size, _buffer_address )
            self._wait_not_busy()
            irq.reset( self.irq )
            self._write_data( _cmd_read_sectors )
            self._write_sector_id( cyl, head, sector )
            irq.sleep_until( self.irq )
            st0, st1, st2, _, _, _, _ = self._read_result()
            try:
                self._check_st( st0, st1, st2 )
            except FloppyError, x:
                if retry == _rw_retries-1:
                    raise
                if _show_errors:
                    print 'error reading %i %i %i:' % (cyl, head, sector), x, '(retrying)'
            else:
                return io.mem_to_string( _buffer_address, 512 )
        assert False


    def _read_result( self ):
        '''Read and return the usual result phase from the FDC.

        Result is a tuple:
        (st0, st1, st2, cyl, head, sector number, sector size)
        '''
        return (
            self._read_data(),
            self._read_data(),
            self._read_data(),
            self._read_data(),
            self._read_data(),
            self._read_data(),
            self._read_data() )


    def _write_sector_id( self, cyl, head, sector ):
        if cyl >= _tracks or cyl < 0:
            raise ValueError( 'cylinder is out of range' )
        if head >= _heads or head < 0:
            raise ValueError( 'head is out of range' )
        if sector > _sectors_per_track or sector <= 0:
            raise ValueError( 'sector is out of range' )
        self._write_data( head << 2 )   # TODO: support drive B
        self._write_data( cyl )
        self._write_data( head )
        self._write_data( sector )
        self._write_data( _sector_size )
        self._write_data( _sectors_per_track )
        self._write_data( _gap_3 )
        self._write_data( 0xff )


    def _seek_heads( self, cyl ):
        '''Seek the heads to `cyl` iff they are not already there.'''
        if cyl == self._current_cyl:
            return
        if self._need_calibrate:
            self._calibrate()
        for retry in xrange( _seek_retries ):
            if cyl >= _tracks or cyl < 0:
                raise ValueError( 'cylinder is out of range' )
            self._wait_not_busy()
            irq.reset( self.irq )
            self._write_data( 0x0f )
            self._write_data( 0 )   # TODO: support drive b
            self._write_data( cyl )
            irq.sleep_until( self.irq )
            st0, current_cyl = self._check_interrupt_status()
            self._check_st( st0 )
            if current_cyl == cyl:
                self._current_cyl = cyl
                return
            if _show_errors:
                print 'seek failed, attempt %i' % retry
                if retry & 1:
                    # calibrate every other attempt
                    self._need_calibrate = True
        raise SeekError( 'could not seek to cylinder %i' % cyl )


    def _check_st( self, st0, st1=None, st2=None ):
        '''Check the given value for st0 and raise an exception on error.'''

        ic = (st0 & 0xc0) >> 6
        if not ic:
            return

        errors = []
        if st0 & 0x20:
            errors.append( 'SE: seek end' )
        if st0 & 0x10:
            errors.append( 'EC: unit check: drive fault or could not find track' )
        if st0 & 0x08:
            errors.append( 'NR: drive not ready' )
        #errors.append( 'head %i active' % ((st0 & 0x04) >> 2) )
        #errors.append( 'drive %i selected' % (st0 & 0x03) )

        if st1 is not None:
            if st1 & 0x80:
                errors.append( 'EN: end of cylinder' )
            if st1 & 0x20:
                errors.append( 'DE: data error' )
            if st1 & 0x10:
                errors.append( 'OR: timeout/overrun' )
            if st1 & 0x04:
                errors.append( 'ND: no data' )
            if st1 & 0x02:
                errors.append( 'NW: not writable' )
            if st1 & 0x01:
                errors.append( 'MA: no address mark' )

        if st2 is not None:
            if st2 & 0x40:
                errors.append( 'CM: deleted address mark' )
            if st2 & 0x20:
                errors.append( 'DD: CRC error' )
            if st2 & 0x10:
                errors.append( 'WC: wrong cylinder' )
            if st2 & 0x08:
                errors.append( 'SH: seek equal' )
            if st2 & 0x04:
                errors.append( 'SN: seek error' )
            if st2 & 0x02:
                errors.append( 'BC: bad cylinder' )
            if st2 & 0x01:
                errors.append( 'MD: not data address mark DAM' )

        errors = '\n'.join(errors)
        if ic == 0x01:
            raise IncompleteError( errors )
        elif ic == 0x10:
            raise InvalidCommandError( errors )
        elif ic == 0x11:
            raise NotReadyError( errors )


    def _wait_not_busy( self ):
        '''Wait until the floppy indicates it's not busy or positioning heads.'''
        start = uuutime.get_time()
        while uuutime.get_time() - start < _busy_timeout:
            msr = self._read_msr()
            msr &= 0x10
            if not msr:
                return
        raise TimeoutError( 'timeout waiting for FDC to complete command. MSR: %x' % msr )


    def _check_interrupt_status( self ):
        '''Execute check interrupt status command and return result.

        Result is a pair (st0, current cylinder).
        '''
        time = uuutime.get_time()
        msr = None
        # For some odd reason, sometimes my FDC will return only one byte from
        # this command, and assuming it returns st0, it doesn't indicate an
        # error. Retrying the command makes it work. If I add a 3s delay here,
        # the problem subsides. However, I can't find anything that
        # consistantly changes within that time that indicates the command
        # should be issued. <indigo@unununium.org>
        for retry in xrange( _int_status_retries ):
            self._wait_not_busy()
            self._write_data( _cmd_int_status )
            st0 = self._read_data()
            try:
                # if this command is issued without pending interrupts, FDC treats it
                # as an invalid command.
                
                cyl = self._read_data()
            except StateError, x:
                self._check_st( st0 )
                if retry == _int_status_retries-1:
                    raise
                if _show_errors:
                    print 'int status failed, retrying: %r' % x
                continue
            return st0, cyl
        assert False


    def _wait_rqm( self ):
        '''Wait for RQM to be set in the MSR.
        
        Returns the last value of the MSR, which can be used to check DIO.
        '''
        start = uuutime.get_time()
        while uuutime.get_time() - start < _data_timeout:
            msr = self._read_msr()
            if msr & _msr_rqm:
                return msr
        raise FloppyError( 'timeout waiting for MQR' )


    def _write_data( self, byte ):
        '''Wait for FDC to become ready, then write `byte` to the data register.'''
        msr = self._wait_rqm()
        if msr & _msr_dio:
            raise StateError( 'trying to write, but FDC expects a read' )
        io.outb( _data_port, byte )


    def _read_data( self ):
        '''Wait for FDC to become ready, read and return byte from data register.'''
        msr = self._wait_rqm()
        if not msr & _msr_dio:
            raise StateError( 'trying to read, but FDC expects a write' )
        return io.inb( _data_port )


    def _read_msr( self ):
        '''Read the MSR and return the result.'''
        return io.inb( _msr_port )


    def _calibrate( self ):
        for retry in xrange( _seek_retries ):
            self._wait_not_busy()
            irq.reset( self.irq )
            self._write_data( _cmd_calibrate )
            self._write_data( 0 ) # TODO: support drive B
            irq.sleep_until( self.irq )
            st0, current_cyl = self._check_interrupt_status()
            self._check_st( st0 )
            if current_cyl == 0:
                self._need_calibrate = False
                return
            if _show_errors:
                print 'calibrate failed, attempt %i' % retry
        raise SeekError( 'could not calibrate heads' )


    def _program_dma( self, mode, length, dest ):
        io.outb( 0x0a, 6 )
        io.outb( 0x0c, 0 )
        io.outb( 0x0b, mode )
        length -= 1
        io.outb( 0x05, length & 0xff )
        io.outb( 0x05, length >> 8 )
        io.outb( 0x81, dest >> 16 )
        io.outb( 0x04, dest & 0xff )
        io.outb( 0x04, (dest >> 8) & 0xff )
        io.outb( 0x0a, 2 )


    def _set_datarate( self, rate ):
        '''Set the data rate in the CCR.

        Datarate should be one of:
        00 = 500kbits/s
        01 = 300kbits/s
        10 = 250kbits/s
        11 - 1Mbits/s

        500kbits/s is the default for 1.44M floppies.
        '''
        if rate & ~0x03:
            raise ValueError( 'invalid data rate for floppy' )
        io.outb( _ccr_port, rate )



uuu.root_vfs.bind( [disk_cache.CachedDisk(Drive(), write=3)], uuu.dev_path + ['floppy','0'] )
