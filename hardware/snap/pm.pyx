cdef extern from "pmapi.h":
    void PM_init ()


def init():
    PM_init()
