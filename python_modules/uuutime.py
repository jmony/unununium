from _uuutime import set_uuutime, get_uuutime
import io

def set_from_rtc():
    def read_chunk( index ):
        io.outb( 0x70, index )
        chunk = io.inb( 0x71 )
        print 'read %x' % chunk
        return (chunk & 0xf0) * 10 + (chunk & 0x0f)

    year = read_chunk( 0x09 ) + 2000
    month = read_chunk( 0x08 )
    day = read_chunk( 0x07 )
    hour = read_chunk( 0x04 )
    minute = read_chunk( 0x02 )
    sec = read_chunk( 0x00 )

    print 'year',year
    print 'month',month
    print 'day',day
    print 'hour',hour
    print 'minute',minute
    print 'sec',sec
