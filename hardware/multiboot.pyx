'''A module to provide access to information from a multiboot bootloader.'''

cdef extern from "Python.h":
    object PyString_FromStringAndSize(char *s, int len)


cdef extern from "multiboot.h":

    ctypedef unsigned uint32_t
    ctypedef unsigned char uint8_t

    cdef struct multiboot_module:
        void *mod_start
        void *mod_end
        char *string

    cdef struct multiboot_info:
        uint32_t flags
        uint32_t mem_lower
        uint32_t mem_upper
        uint8_t drive
        uint8_t part1
        uint8_t part2
        uint8_t part3
        char *cmdline
        multiboot_module *mods_addr
        uint32_t mods_count
        uint32_t syms
        uint32_t mmap_length
        uint32_t mmap_addr

    multiboot_info *get_multiboot_info()


cdef multiboot_info *info
cdef multiboot_module *module
cdef int i
info = get_multiboot_info()
if info.flags & 0x00000001:
    mem_lower = info.mem_lower
    mem_upper = info.mem_upper
if info.flags & 0x00000002:
    drive = info.drive
    part1 = info.part1
    part2 = info.part2
    part3 = info.part3
if info.flags & 0x00000004:
    cmdline = info.cmdline
if info.flags & 0x00000008:
    modules = []
    i = 0
    module = info.mods_addr
    while i < info.mods_count:
        modules.append( (module.string,
            PyString_FromStringAndSize(
                <char*>module.mod_start,
                module.mod_end-module.mod_start)) )
        i = i+1
        module = module+1
    # ...
info = NULL
