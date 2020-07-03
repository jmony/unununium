#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include <stdio.h>
#include <malloc.h>
#include <stdarg.h>
#include <python2.3/Python.h>

// define these to use C routines for stdin/out/err that work, which is
// useful for debugging the usual python console stuffs.

//#define IGNORE_STDOUT
//#define IGNORE_STDIN

unsigned screen_pos = 0;
uint16_t *screen = (uint16_t *)0xb8000;

int ioctl(int d, int request, ...);
int kill(pid_t pid, int sig);
pid_t waitpid(pid_t pid, int *status, int options);

#define memfs_limit_fds		64
#define memfs_limit_files	32

unsigned screen_width = 80;
unsigned screen_height = 25;


struct _memfs_fd
{
  PyObject *file;
  unsigned char in_use;
} memfs_fd[memfs_limit_fds];



static PyObject *uuu_open(
    const char *path,
    int read,
    int write,
    int create,
    int truncate,
    int append,
    int mode )
{
  PyObject *uuumodule, *root_vfs, *file;

  uuumodule = PyDict_GetItemString( PyImport_GetModuleDict(), "uuu" );
  if( ! uuumodule ) { return NULL; }
  root_vfs = PyObject_GetAttrString( uuumodule, "root_vfs" );
  if( ! root_vfs ) { return NULL; }
  file = PyObject_CallMethod( root_vfs, "open", "siiiiii",
      path, read, write, create, truncate, append, mode );
  Py_DECREF( root_vfs );
  return file;
}



#ifdef IGNORE_STDOUT
static int fallback_write( const char *string, size_t count )
{
  size_t remaining = count;
  unsigned i;

  while( remaining )
  {
    if( screen_pos >= screen_width * screen_height )
    {
      memmove( screen, &screen[screen_width], screen_width * (screen_height-1) * sizeof(unsigned) );
      for( i = screen_width * (screen_height-1) ; i < screen_width * screen_height ; ++i ) {
        screen[i] = 0x0720;
      }
      screen_pos = screen_width * (screen_height-1);
    }

    switch( *string )
    {
      case '\n':
        screen_pos += screen_width;
        screen_pos -= screen_pos % screen_width;
        break;

      case '\b':
        screen[--screen_pos] = 0x0720;
        break;

      default:
        screen[screen_pos++] = *string + 0x0700;
    }

    ++string;
    --remaining;
  }
  return count;
}
#endif



int write(int fd, const void *buf, size_t count)
{
  PyObject *type, *value, *traceback;

#ifdef IGNORE_STDOUT
  if( (fd == 1 || fd == 2) ) {
      return fallback_write( buf, count );
  }
#endif
  if( ! memfs_fd[fd].in_use ) goto invalid_no_error;

  PyErr_Fetch( &type, &value, &traceback );

  PyObject *result;
  int length;

  result = PyObject_CallMethod( memfs_fd[fd].file, "write", "s#", buf, count );
  if( ! result ) {
    goto invalid;
  }

  if( ! PyInt_Check(result) ) {
    Py_DECREF(result);
    goto invalid;
  }

  length = (int)PyInt_AsLong( result );
  Py_DECREF(result);
  PyErr_Restore( type, value, traceback );
  return length;

invalid:
  PyErr_Restore( type, value, traceback );
invalid_no_error:
  errno = EINVAL;
  return -1;
}
int __libc_write(const char*fn,int flags,...) __attribute__((weak,alias("write")));



int read(int fd, void *buf, size_t count)
{
  PyObject *type, *value, *traceback;

  if( count == 0 ) {
    return 0;
  }

#ifdef IGNORE_STDIN
  if( fd == 0 ) {
    char key;
    int bytes_read = 0;
    // it's stdin
    while( count-- ) {
      asm( "call get_key\n" : "=a"(key) : : "ecx","edx","cc" );
      if( key == '\r' ) key = '\n';
      if( key == '\b' ) {
	if( bytes_read ) {
	  bytes_read -= 1;
	  write( 1, &key, 1 );
	}
	continue;
      }
      write( 1, &key, 1 );
      ((char *)buf)[bytes_read++] = key;
      if( key == '\n' ) break;
    }
    return bytes_read;
  }
#endif
  if( ! memfs_fd[fd].in_use ) goto invalid_no_error;

  PyErr_Fetch( &type, &value, &traceback );

  PyObject *result;
  unsigned string_length;

  result = PyObject_CallMethod( memfs_fd[fd].file, "read", "i", count );
  if( ! result ) {
    goto invalid;
  }

  if( ! PyString_CheckExact(result) ) {
    Py_DECREF(result);
    goto invalid;
  }
  string_length = PyString_GET_SIZE( result );
  if( count < string_length ) string_length = count;
  memcpy( buf, PyString_AS_STRING(result), string_length );
  Py_DECREF(result);
  PyErr_Restore( type, value, traceback );
  return string_length;


invalid:
  PyErr_Restore( type, value, traceback );
invalid_no_error:
  errno = EINVAL;
  return -1;
}
int __libc_read(const char*fn,int flags,...) __attribute__((weak,alias("read")));



off_t lseek(int fd, off_t offset, int whence)
{
  PyObject *result;
  off_t tell_offset;
  PyObject *type, *value, *traceback;

  if( fd < 3 ) {
    errno = ESPIPE;
    return (off_t)-1;
  }
  if( ! memfs_fd[fd].in_use ) {
    errno = EBADF;
    return (off_t)-1;
  }

  PyErr_Fetch( &type, &value, &traceback );

  result = PyObject_CallMethod( memfs_fd[fd].file, "seek", "li", offset, whence );
  if( !result ) {
    goto error;
  }
  Py_DECREF(result);

  result = PyObject_CallMethod( memfs_fd[fd].file, "tell", NULL );
  if( !result ) {
    goto error;
  }
  if( !PyInt_Check(result) ) {
    Py_DECREF(result);
    goto error;
  }
  tell_offset = (off_t)PyInt_AsLong( result );
  Py_DECREF(result);
  return tell_offset;

error:
  PyErr_Restore( type, value, traceback );
  errno = EINVAL;
  return (off_t)-1;
}



int close(int fd)
{
  PyObject *type, *value, *traceback;

  if( fd < 3 ) return 0;

  if( ! memfs_fd[fd].in_use ) {
    errno = EBADF;
    return -1;
  }

  PyObject *result;
  PyErr_Fetch( &type, &value, &traceback );

  result = PyObject_CallMethod( memfs_fd[fd].file, "close", NULL );
  if( ! result ) {
    errno = ENOSYS;
    PyErr_Restore( type, value, traceback );
    return -1;
  }
  Py_DECREF(result);
  memfs_fd[fd].in_use = 0;
  PyErr_Restore( type, value, traceback );
  return 0;
}
int __libc_close(const char*fn,int flags,...) __attribute__((weak,alias("close")));



int open(const char *pathname, int flags, ...)
{
  PyObject *file;
  PyObject *type, *value, *traceback;
  int mode;
  int fd;
  va_list args;

  va_start( args, flags );
  mode = va_arg( args, int );
  va_end( args );

  PyErr_Fetch( &type, &value, &traceback );

  file = uuu_open(
      pathname,
      (flags & O_ACCMODE) == O_RDONLY || (flags & O_ACCMODE) == O_RDWR,
      (flags & O_ACCMODE) == O_WRONLY || (flags & O_ACCMODE) == O_RDWR,
      flags & O_CREAT,
      flags & O_TRUNC,
      flags & O_APPEND,
      mode );
  if( ! file ) {
    goto not_found;
  }

  for( fd=3; memfs_fd[fd].in_use; fd+=1 ) {
    if( fd >= memfs_limit_fds ) {
      Py_DECREF(file);
      errno = ENFILE;
      return -1;
    }
  }

  memfs_fd[fd].in_use = 1;
  memfs_fd[fd].file = file;
  //printf( "%s is fd %i\n", pathname, fd );
  PyErr_Restore( type, value, traceback );
  return fd;

not_found:
  PyErr_Restore( type, value, traceback );
  //printf( "%s: file not found\n", pathname );
  errno = ENOENT;
  return -1;
}
int __libc_open(const char*fn,int flags,...) __attribute__((weak,alias("open")));



int rename(const char *oldpath, const char *newpath)
{
  // PYTHON HERE
  errno = EROFS;
  return -1;
}

  //(*__errno_location())=ENOMEM;
time_t time(time_t *t) {
  static time_t fake_time = 1073591226;
  fake_time += 1;	// my...time is odd around here!
  if( t ) *t = fake_time;
  return fake_time;
}

int access (const char *__name, int __type) {
  // PYTHON HERE
  return 0;
}

int unlink(const char *pathname) {
  // PYTHON HERE
  (*__errno_location()) = EROFS;
  return -1;
}

int ioctl(int d, int request, ...) {
  // PYTHON HERE
  (*__errno_location()) = EINVAL;
  return -1;
}

pid_t getpid(void) {
  static pid_t pid = 2;
  return pid++;
}

int kill(pid_t pid, int sig) {
  return 0; // we arn't so violent here
}

int rmdir(const char *pathname) {
  (*__errno_location()) = EROFS;
  return -1;
}

pid_t fork(void) {
  (*__errno_location()) = ENOMEM;
  return -1; // yeah..out of memory! that's it!
}

pid_t waitpid(pid_t pid, int *status, int options) {
  (*__errno_location()) = ECHILD;
  return -1;
}

int execve(const char *filename, char *const argv [], char *const envp[]) {
  (*__errno_location()) = EACCES;
  return -1;
}

int fstat(int fd, struct stat *buf)
{
  PyObject *type, *value, *traceback;
  //printf( "fstat( %i, %p )\n", fd, buf );
  if( fd >= memfs_limit_fds || ! memfs_fd[fd].in_use ) {
    (*__errno_location()) = EBADF;
    return -1;
  }

  PyObject *stat;
  PyObject *member;

  memset( buf, 0, sizeof(struct stat) );

  PyErr_Fetch( &type, &value, &traceback );

  stat = PyObject_CallMethod( memfs_fd[fd].file, "stat", NULL );
  if( ! stat ) {
    errno = ENOSYS;
    PyErr_Restore( type, value, traceback );
    return -1;
  }

  // dev?
  member = PyObject_GetAttrString( stat, "st_ino" );
  if( member && PyInt_Check(member) ) {
    buf->st_ino = (ino_t)PyInt_AsLong(member);
    Py_DECREF(member);
  }
  member = PyObject_GetAttrString( stat, "st_mode" );
  if( member && PyInt_Check(member) ) {
    buf->st_mode = (mode_t)PyInt_AsLong(member);
    Py_DECREF(member);
  }
  member = PyObject_GetAttrString( stat, "st_nlink" );
  if( member && PyInt_Check(member) ) {
    buf->st_nlink = (nlink_t)PyInt_AsLong(member);
    Py_DECREF(member);
  }
  member = PyObject_GetAttrString( stat, "st_uid" );
  if( member && PyInt_Check(member) ) {
    buf->st_uid = (uid_t)PyInt_AsLong(member);
    Py_DECREF(member);
  }
  member = PyObject_GetAttrString( stat, "st_gid" );
  if( member && PyInt_Check(member) ) {
    buf->st_gid = (gid_t)PyInt_AsLong(member);
    Py_DECREF(member);
  }
  // rdev?
  member = PyObject_GetAttrString( stat, "st_size" );
  if( member && PyInt_Check(member) ) {
    buf->st_size = (off_t)PyInt_AsLong(member);
    Py_DECREF(member);
  }
  /*
  member = PyObject_GetAttrString( stat, "st_blksize" );
  if( member && PyInt_Check(member) ) {
    buf->st_blksize = (blksize_t)PyInt_AsLong(member);
    Py_DECREF(member);
  }
  member = PyObject_GetAttrString( stat, "st_blocks" );
  if( member && PyInt_Check(member) ) {
    buf->st_blocks = (blkcnt_t)PyInt_AsLong(member);
    Py_DECREF(member);
  }
  */
  member = PyObject_GetAttrString( stat, "st_atime" );
  if( member && PyInt_Check(member) ) {
    buf->st_atime = (time_t)PyInt_AsLong(member);
    Py_DECREF(member);
  }
  member = PyObject_GetAttrString( stat, "st_mtime" );
  if( member && PyInt_Check(member) ) {
    buf->st_mtime = (time_t)PyInt_AsLong(member);
    Py_DECREF(member);
  }
  member = PyObject_GetAttrString( stat, "st_ctime" );
  if( member && PyInt_Check(member) ) {
    buf->st_ctime = (time_t)PyInt_AsLong(member);
    Py_DECREF(member);
  }
  PyErr_Restore( type, value, traceback );
  return 0;
}

int stat(const char *__file, struct stat *__buf) {
  errno = ENOSYS;
  return -1;

  // PYTHON HERE
}

int llseek(int fd, unsigned long hi, unsigned long lo, loff_t *p_offset, int whence)
{
  PyObject *type, *value, *traceback;
  PyObject *result;

  if( fd >= memfs_limit_fds || ! memfs_fd[fd].in_use ) {
    (*__errno_location()) = EBADF;
    return -1;
  }

  if( whence < 0 || whence > 2 ) goto no_clear_error;

  PyErr_Fetch( &type, &value, &traceback );

  result = PyObject_CallMethod( memfs_fd[fd].file, "seek", "L", ( (unsigned long long)hi << 32 | lo ) );
  if( ! result ) goto error;
  Py_DECREF(result);

  result = PyObject_CallMethod( memfs_fd[fd].file, "tell", "i", whence );
  if( ! result ) goto error;

  *p_offset = (loff_t)PyLong_AsLongLong( result );
  return 0;

error:
  PyErr_Restore( type, value, traceback );
no_clear_error:
  errno = EINVAL;
  return -1;
}



static PyObject *set_stdin( PyObject *self, PyObject *args )
{
  PyObject *file;
  if(!PyArg_ParseTuple(args, "O:set_stdin", &file)) return NULL;

  file = PyObject_CallMethod( file, "open", "iiii",
      1, 0, 0, 0 );
  if( !file ) return NULL;

  memfs_fd[0].file = file;
  memfs_fd[0].in_use = 1;

  Py_INCREF( Py_None );
  return Py_None;
}

static PyObject *set_stdout( PyObject *self, PyObject *args )
{
  PyObject *file;
  if(!PyArg_ParseTuple(args, "O:set_stdout", &file)) return NULL;

  file = PyObject_CallMethod( file, "open", "iiii",
      0, 1, 1, 0 );
  if( !file ) return NULL;

  memfs_fd[1].file = file;
  memfs_fd[1].in_use = 1;

  Py_INCREF( Py_None );
  return Py_None;
}

static PyObject *set_stderr( PyObject *self, PyObject *args )
{
  PyObject *file;
  if(!PyArg_ParseTuple(args, "O:set_stderr", &file)) return NULL;

  file = PyObject_CallMethod( file, "open", "iiii",
      0, 1, 1, 0 );
  if( !file ) return NULL;

  memfs_fd[2].file = file;
  memfs_fd[2].in_use = 1;

  Py_INCREF( Py_None );
  return Py_None;
}



static PyMethodDef LibcMethods[] = {
  {"set_stdin", set_stdin, METH_VARARGS,
    "Set standard input to a given node."},
  {"set_stdout", set_stdout, METH_VARARGS,
    "Set standard output to a given node."},
  {"set_stderr", set_stderr, METH_VARARGS,
    "Set standard error to a given node."},
  {NULL, NULL, 0, NULL}
};

void initlibc() {
  Py_InitModule( "libc", LibcMethods );
}
