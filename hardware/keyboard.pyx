cdef extern char c_get_key "get_key" ()

def get_key():
    return chr(c_get_key())
