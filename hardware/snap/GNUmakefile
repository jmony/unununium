UUUROOT=../..

OBJS = gconsole.o ga.o pm.o

.PHONY: all
all: $(OBJS)

ga.c: ga.pxd gconsole.pxd common.pxd
gconsole.c: gconsole.pxd common.pxd

.PHONY: clean
clean: basic-clean
	rm -f *.o gconsole.c ga.c pm.c

include $(UUUROOT)/Make.config
-include $(OBJS:.o=.d)
