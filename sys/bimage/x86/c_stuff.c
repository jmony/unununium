#include <python2.3/Python.h>
#include <stdio.h>
#include <errno.h>
#include <stdlib.h>

extern void _start_hydro3d();
extern void initmultiboot(void);
extern void initgatest(void);
extern void init_irqmodule(void);
extern void init_iomodule(void);
extern void init_uuutimemodule(void);
extern void initpm(void);
extern void initga(void);
extern void initgconsole(void);
extern void initkeyboard(void);
extern void initlibc(void);

extern void block_device_py;
extern void floppy_py;
extern void ata_py;
extern void ext2_py;
extern void vfs_py;
extern void uuu_py;
extern void ramfs_py;
extern void shell_py;
extern void init_py;
extern void disk_cache_py;
extern void simpleconsole_py;

void load_module(char *name, char *filename, char *data);

static PyObject*
hydro3d_run(PyObject *self, PyObject *args)
{
    if(!PyArg_ParseTuple(args, ":numargs"))
        return NULL;
    _start_hydro3d();
    return NULL;
}

static PyMethodDef Hydro3dMethods[] = {
    {"run", hydro3d_run, METH_VARARGS,
     "Run the Hydro3D demo."},
    {NULL, NULL, 0, NULL}
};


void c_stuff() {
  PyObject *globals;
  PyObject *runresult;

  setenv( "PYTHONHOME", "/", 1 );

  Py_Initialize();
  initpm();
  initga();
  initgconsole();
  initgatest();
  load_module( "shell", "/lib/python2.3/shell.py", (char *)&shell_py );
  Py_InitModule( "hydro3d", Hydro3dMethods );

  globals = PyDict_Copy( PyModule_GetDict( PyImport_AddModule( "__main__" ) ) );
  if( ! globals ) { PyErr_Print(); goto run; }
  runresult = PyRun_String( (char *)&init_py, Py_file_input, globals, globals );
  if( runresult == NULL ) { PyErr_Print(); }
  else {
    Py_DECREF( runresult );
  }
  Py_DECREF( globals );
run:
  PyRun_InteractiveLoop( stdin, "<stdin>" );
  // Py_Finalize is called in test.asm
}

static void fatal_error( const char *message )
{
  unsigned short *vram = (unsigned short *)0xb8000;
  while( *message ) {
    *vram++ = *message++ + 0x4f00;
  }
  while(0xdeadbeef) asm( "cli; hlt" );
}

int unununium_init()
{
  PyObject *simpleconsole, *libc, *console, *r;

  init_iomodule();
  initkeyboard();
  initlibc();
  load_module( "vfs", "/lib/python2.3/vfs.py", (char *)&vfs_py );
  load_module( "simpleconsole", "/lib/python2.3/simpleconsole.py", (char *)&simpleconsole_py );

  simpleconsole = PyDict_GetItemString( PyImport_GetModuleDict(), "simpleconsole" );
  if( ! simpleconsole ) fatal_error( "could not get simpleconsole module" );
  libc = PyDict_GetItemString( PyImport_GetModuleDict(), "libc" );
  if( ! libc ) fatal_error( "could not get libc module" );
  console = PyObject_CallMethod( simpleconsole, "Console", NULL );
  if( ! console ) fatal_error( "could not create console" );
  r = PyObject_CallMethod( libc, "set_stdin", "O", console );
  if( ! r ) fatal_error( "could not set stdin" );
  Py_DECREF( r );
  r = PyObject_CallMethod( libc, "set_stdout", "O", console );
  if( ! r ) fatal_error( "could not set stdout" );
  Py_DECREF( r );
  r = PyObject_CallMethod( libc, "set_stderr", "O", console );
  if( ! r ) fatal_error( "could not set stderr" );
  Py_DECREF( r );
  Py_DECREF(console);

  initmultiboot();
  init_irqmodule();
  init_uuutimemodule();
  load_module( "ramfs", "/lib/python2.3/ramfs.py", (char *)&ramfs_py );
  load_module( "uuu", "/lib/python2.3/uuu.py", (char *)&uuu_py );
  load_module( "block_device", "/lib/python2.3/block_device.py", (char *)&block_device_py );
  load_module( "ext2", "/lib/python2.3/ext2.py", (char *)&ext2_py );
  load_module( "disk_cache", "/lib/python2.3/disk_cache.py", (char *)&disk_cache_py );
  load_module( "floppy", "/lib/python2.3/floppy.py", (char *)&floppy_py );
  load_module( "ata", "/lib/python2.3/ata.py", (char *)&ata_py );
  return 1;
}

int __dietlibc_fstat64(int __fd, struct stat64 *__buf)
{
  errno = ENOSYS;
  return -1;
}

int __dietlibc_stat64(const char *__file, struct stat64 *__buf)
{
  errno = ENOSYS;
  return -1;
}

void load_module(char *name, char *filename, char *data)
{
    PyObject *co;
    PyObject *module;

    co = Py_CompileString( data, filename, Py_file_input );
    if( co == NULL ) {
        PyErr_Print();
        return;
    }
    module = PyImport_ExecCodeModule( name, co );
    Py_DECREF(co);
    if( module == NULL ) {
        PyErr_Print();
        return;
    }
    Py_DECREF(module);
}
