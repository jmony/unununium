import block_device

cached_disks = {}

class CachedDisk( block_device.BlockDevice ):
    '''An adapter to add a cache do a disk.

    parameters:
    -----------
    - `read`: if true, check the cache for data before calling the original
      `read_sectors`.
    - `write`: determines the type of write caching:
        - 0: `write_sectors` is unchanged.
        - 1: writes update the cache, and are never flushed, not even with
          `sync`. This can be used to make a read-only device appear writable.
        - 2: writes update the cache, then go to disk immediately
        - 3: writes update the cache, and are flushed to disk later
    '''

    def __init__( self, device, read=True, write=2 ):
        self._original = device
        self._cache = {}
        if read:
            self.read_sectors = self._read_sectors_cached
        if write == 0:
            pass
        elif write == 1:
            self.write_sectors = self._write_sectors_shadow
        elif write == 2:
            self.write_sectors = self._write_sectors_thru
        elif write == 3:
            self.write_sectors = self._write_sectors_cached
        else:
            raise ValueError( 'invalid write parameter %r' % write )
        cached_disks[self] = None


    def sync_cache( self ):
        '''Write dirty pages in the cache to disk.'''
        dirty_sectors = []
        for sector, (dirty, data) in self._cache.iteritems():
            if dirty:
                dirty_sectors.append(sector)
        dirty_sectors.sort()

        for sector in dirty_sectors:
            self._original.write_sectors( sector, self._cache[sector][1] )
            self._cache[sector][0] = False


    def void_cache( self ):
        '''Remove all pages from the cache.
        
        The cache is first synced if needed.'''

        self.sync_cache()
        self._cache.clear()


    def disable_cache( self ):
        '''Completely disable the cache.

        The cache is first synced, then voided, then disabled. There is
        no way to enable it again. This is generally used at shutdown.'''

        self.void_cache()
        self.read_sectors = self._original.read_sectors
        self.write_sectors = self._original.write_sectors
        del cached_disks[self]


    def _read_sectors_cached( self, first, count ):
        if not self._original.allow_read:
            raise IOError( 'device does not support reading' )

        class needed:
            first = None
            count = 0

        def read_needed():
            r = self._original.read_sectors( needed.first, needed.count )
            self._update_cache( needed.first, r, False )
            assert len(r) == needed.count * self._original.block_size
            needed.first = None
            needed.count = 0
            return r

        r = ''
        for sector in xrange( first, first+count ):
            try:
                from_cache = self._cache[sector][1]
            except KeyError:
                if needed.first is None:
                    needed.first = sector
                needed.count += 1
            else:
                if needed.count:
                    r += read_needed()
                assert len(from_cache) == self._original.block_size
                r += from_cache

        if needed.count:
            r += read_needed()

        assert len(r) == count * self._original.block_size
        return r


    def _update_cache( self, first, data, dirty ):
        for sector in xrange( len(data)//self._original.block_size ):
            sector_data = data[
                sector*self._original.block_size :
                (sector+1)*self._original.block_size ]
            assert len(sector_data) == self._original.block_size
            self._cache[first+sector] = [ dirty, sector_data ]


    def _write_sectors_thru( self, first, data ):
        if not self._original.allow_write:
            raise IOError( 'device does not support writing' )
        self._update_cache( first, data, False )
        self._original.write_sectors( first, data )


    def _write_sectors_cached( self, first, data ):
        if not self._original.allow_write:
            raise IOError( 'device does not support writing' )
        self._update_cache( first, data, True )


    def _write_sectors_shadow( self, first, data ):
        self._update_cache( first, data, False )


    def __getattr__( self, attr ):
        return getattr( self._original, attr )


    def __getitem__( self, key ):
        return self._original[key]


    def __del__( self ):
        self.disable_cache()
