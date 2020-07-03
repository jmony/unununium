#include <python2.3/Python.h>
#include <string.h>


static PyObject *inb(PyObject *self, PyObject *args)
{
  int port;
  unsigned int in;
  if(!PyArg_ParseTuple(args, "i", &port)) return NULL;

  asm( "in (%%dx),%%al" : "=a"(in) : "d"(port) );
  in &= 0xff;

  return PyInt_FromLong( (long)in );
}

static PyObject *inw(PyObject *self, PyObject *args)
{
  int port;
  unsigned int in;
  if(!PyArg_ParseTuple(args, "i", &port)) return NULL;

  asm( "in (%%dx),%%ax" : "=a"(in) : "d"(port) );
  in &= 0xffff;

  return PyInt_FromLong( (long)in );
}

static PyObject *inl(PyObject *self, PyObject *args)
{
  int port;
  unsigned int in;
  if(!PyArg_ParseTuple(args, "i", &port)) return NULL;

  asm( "in (%%dx),%%eax" : "=a"(in) : "d"(port) );

  return PyInt_FromLong( (long)in );
}



static PyObject *outb(PyObject *self, PyObject *args)
{
  unsigned int out;
  int port;
  if(!PyArg_ParseTuple(args, "iI", &port, &out)) return NULL;

  asm( "out %%al, (%%dx)" : : "a"(out), "d"(port) );

  Py_INCREF( Py_None );
  return Py_None;
}

static PyObject *outw(PyObject *self, PyObject *args)
{
  unsigned int out;
  int port;
  if(!PyArg_ParseTuple(args, "iI", &port, &out)) return NULL;

  asm( "out %%ax, (%%dx)" : : "a"(out), "d"(port) );

  Py_INCREF( Py_None );
  return Py_None;
}

static PyObject *outl(PyObject *self, PyObject *args)
{
  unsigned int out;
  int port;
  if(!PyArg_ParseTuple(args, "iI", &port, &out)) return NULL;

  asm( "out %%eax, (%%dx)" : : "a"(out), "d"(port) );

  Py_INCREF( Py_None );
  return Py_None;
}



static PyObject *mem_to_string(PyObject *self, PyObject *args)
{
  const char *buf;
  int len;
  if(!PyArg_ParseTuple(args, "Ii", &buf, &len)) return NULL;
  return PyString_FromStringAndSize( buf, len );
}

static PyObject *string_to_mem(PyObject *self, PyObject *args)
{
  const char *dest;
  const char *src;
  int len;
  if(!PyArg_ParseTuple(args, "Is#", &dest, &src, &len)) return NULL;
  memcpy( dest, src, len );

  Py_INCREF( Py_None );
  return Py_None;
}

static PyObject *mem_to_mem(PyObject *self, PyObject *args)
{
  const char *dest;
  const char *src;
  unsigned len;
  if(!PyArg_ParseTuple(args, "III", &dest, &src, &len)) return NULL;
  memmove( dest, src, len );

  Py_INCREF( Py_None );
  return Py_None;
}



static PyMethodDef IoMethods[] = {
  {"inb", inb, METH_VARARGS,
    "Input a byte."},
  {"inw", inw, METH_VARARGS,
    "Input two bytes."},
  {"inl", inl, METH_VARARGS,
    "Input four bytes."},
  {"outb", outb, METH_VARARGS,
    "Output a byte."},
  {"outw", outw, METH_VARARGS,
    "Output two bytes."},
  {"outl", outl, METH_VARARGS,
    "Output four bytes."},
  {"mem_to_string", mem_to_string, METH_VARARGS,
    "Construct a string from bytes anywhere in RAM."},
  {"string_to_mem", string_to_mem, METH_VARARGS,
    "Write a string anywhere in RAM."},
  {"mem_to_mem", mem_to_mem, METH_VARARGS,
    "Copy one block of memory to another, like memmove in C."},
  {NULL, NULL, 0, NULL}
};

void init_iomodule() {
  Py_InitModule( "io", IoMethods );
}
