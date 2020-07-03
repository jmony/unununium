UUUROOT=..

OBJS = ata.o atamodule.o vga_textmodule.o iomodule.o irqmodule.o

.PHONY: all
all: $(OBJS)

.PHONY: clean
clean: basic-clean
	rm -f *.o

include $(UUUROOT)/Make.config
-include $(OBJS:.o=.d)
