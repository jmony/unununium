UUUROOT=../../..

OBJS = test.o

all: $(OBJS)
clean: basic-clean
	rm -f *.o

include $(UUUROOT)/Make.config
-include $(OBJS:.o=.d)

test.o: ../../../python_modules/block_device.py \
        ../../../python_modules/floppy.py \
        ../../../python_modules/ata.py \
        ../../../python_modules/ext2.py \
        ../../../python_modules/vfs.py \
        ../../../python_modules/uuu.py \
        ../../../python_modules/ramfs.py \
        ../../../python_modules/shell.py \
        init.py \
        ../../../python_modules/disk_cache.py \
        ../../../python_modules/simpleconsole.py
