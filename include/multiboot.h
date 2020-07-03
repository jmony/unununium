#include <inttypes.h>

struct multiboot_module {
  void *mod_start;
  void *mod_end;
  char *string;
};

struct multiboot_info {
  uint32_t flags;
  uint32_t mem_lower;
  uint32_t mem_upper;
  uint8_t drive;
  uint8_t part1;
  uint8_t part2;
  uint8_t part3;
  char *cmdline;
  uint32_t mods_count;
  struct multiboot_module *mods_addr;
  uint32_t syms;
  uint32_t mmap_length;
  uint32_t mmap_addr;
};

extern struct multiboot_info *get_multiboot_info(void);
