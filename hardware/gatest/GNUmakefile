UUUROOT=../..

OBJS = main.o

all: $(OBJS)
clean: basic-clean
	rm -f *.o

include $(UUUROOT)/Make.config
-include $(OBJS:.o=.d)
