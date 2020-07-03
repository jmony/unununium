# $Header: /cvsroot/uuu/uuu/sys/interrupts/x86/GNUmakefile,v 1.1 2004/01/04 18:05:42 instinc Exp $

UUUROOT=../../..

OBJS = iridia.o

.PHONY: all
all: $(OBJS)

.PHONY: clean
clean: basic-clean
	rm -f *.o

include $(UUUROOT)/Make.config
-include $(OBJS:.o=.d)
