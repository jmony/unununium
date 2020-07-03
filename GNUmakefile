UUUROOT=$(CURDIR)

all: unununium.o

include $(UUUROOT)/Make.config
include $(UUUROOT)/sys/bimage/$(ARCH)/Make.config
-include sourcefiles

.PHONY: lib/c/bin-i386/dietlibc.a
lib/c/bin-i386/dietlibc.a $(UUUDIET):
	$(entering) $(CURDIR)/lib/c
	$(MAKE) -C lib/c
	$(entering) $(CURDIR)

.PHONY: unununium.o
unununium.o: lib/c/bin-i386/dietlibc.a $(PYTHONDIR)/libpython2.3.a $(BIMAGE_OBJS) $(MORE_BIMAGE_OBJS)
	$(linking) '$^ >  $@'
	$(BARECC) -nostdlib -static -o '$@' -Xlinker -T -Xlinker sys/bimage/$(ARCH)/bimage.ld $(BIMAGE_OBJS) $(MORE_BIMAGE_OBJS) $(PYTHONDIR)/libpython2.3.a lib/c/bin-i386/dietlibc.a -lgcc -lm
	strip -d unununium.o
	echo
	echo "Build of Unununium completed successfully."
	

.PHONY: diskimage
diskimage:
	$(entering) $(CURDIR)/sys/bootloader
	$(MAKE) -C sys/bootloader $(UUUROOT)/diskimage diskimage=$(UUUROOT)/diskimage
	$(entering) $(CURDIR)

.PHONY: grub
grub: unununium.o
	$(entering) $(CURDIR)/sys/bootloader
	$(MAKE) -C sys/bootloader stage2
	$(entering) $(CURDIR)

.PHONY: clean
clean:
	for dir in $(sort $(dir $(BIMAGE_OBJS)) $(dir $(SOURCEFILES)) ); do \
	  $(cleaning) "$$dir"; \
	  $(MAKE) -C "$$dir" clean; \
	done
	$(cleaning) '$(CURDIR)/lib/c'
	$(MAKE) -C '$(CURDIR)/lib/c' clean
	$(cleaning) '$(CURDIR)/uuudoc'
	$(MAKE) -C '$(CURDIR)/uuudoc' clean
	$(cleaning) '$(PYTHONDIR)'
	[ -f $(PYTHONDIR)/Makefile ] && $(MAKE) -C '$(PYTHONDIR)' clean || true
	$(cleaning) '$(SNAPDIR)'
	rm -f $(SNAPDIR)/lib/debug/uuu/gcc/x86/a/libn_ga.a \
	$(SNAPDIR)/lib/debug/uuu/gcc/x86/a/libgconsole.a \
	$(SNAPDIR)/lib/debug/uuu/gcc/x86/a/libpm.a
	$(cleaning) '$(CURDIR)'
	rm -f diskimage unununium.o sourcefiles
	rm -f uuudoc/uuudoc.xml
	rm -f include/ret_counts.asm

.PHONY: $(BIMAGE_OBJS)
$(BIMAGE_OBJS): include/ret_counts.asm $(UUUDIET)
	$(entering) '$(dir $@)'
	$(MAKE) -C '$(dir $@)' '$(notdir $@)'
	$(entering) $(CURDIR)

.PHONY: $(PYTHONDIR)/libpython2.3.a
$(PYTHONDIR)/libpython2.3.a: configure-python $(UUUDIET)
	$(entering) '$(PYTHONDIR)'
	$(MAKE) -C $(PYTHONDIR) libpython2.3.a

.PHONY: configure-python
configure-python: $(UUUDIET)
	if [ ! -f $(PYTHONDIR)/Makefile ]; then \
	  cd $(PYTHONDIR) ;\
	  CC='$(CC)' ./configure --disable-unicode --prefix=$(UUUROOT) ;\
	fi


.PHONY: snap
snap \
$(SNAPDIR)/lib/debug/uuu/gcc/x86/a/libn_ga.a \
$(SNAPDIR)/lib/debug/uuu/gcc/x86/a/libgconsole.a \
$(SNAPDIR)/lib/debug/uuu/gcc/x86/a/libpm.a:
	cd '$(SNAPDIR)' && source start-sdk.uuu && cd src && dmake build UUUDIET=$(UUUDIET)


.PHONY: new_files
new_files:
	rm -f sourcefiles

.PHONY: doc
doc:
	$(entering) $(CURDIR)/uuudoc
	$(MAKE) -C uuudoc all
	$(entering) $(CURDIR)

uuudoc/uuudoc.xml uuudoc/uuudoc.html: $(SOURCEFILES)
	$(entering) $(CURDIR)/uuudoc
	$(MAKE) -C uuudoc $(notdir $@)
	$(entering) $(CURDIR)

sourcefiles: $(SOURCEFILES)
	$(generating) '$@'
	echo 'SOURCEFILES = \' > '$@'
	for file in `find $(addprefix $(UUUROOT)/,$(SOURCE_DIRS)) -name '*.asm'`; do echo "$$file \\" >> '$@'; done
	echo >> '$@'

include/ret_counts.asm: uuudoc/ret_counts.xsl uuudoc/uuudoc.xml
	$(generating) '$@'
	$(XSLTPROC) $^ > '$@'
