#include <unistd.h>
#include <stdlib.h>

extern int __syscall_getcwd(char* buf, size_t size);

char *getcwd(char *buf, size_t size) {
  buf[0] = '/';
  buf[1] = '\0';
  return buf;
}
