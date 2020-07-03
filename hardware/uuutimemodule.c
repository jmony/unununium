#include <python2.3/Python.h>
#include <inttypes.h>

static PyObject *get_time(PyObject *self, PyObject *args)
{
  uint64_t time;
  if(!PyArg_ParseTuple(args, "")) return NULL;

  asm( "call system_time.get_uuutime\n"
       ".long continue%=\n"
       ".long continue%=\n"
       "continue%=:"
       : : "a"(&time) : "ebx","ecx","edx","cc" );

  return Py_BuildValue( "L", time );
}


static PyObject *set_time(PyObject *self, PyObject *args)
{
  uint64_t time;
  if(!PyArg_ParseTuple(args, "L", &time)) return NULL;

  asm( "call system_time.set_uuutime\n"
       ".long continue%=\n"
       ".long continue%=\n"
       "continue%=:"
       : : "a"(&time) : "ebx","ecx","edx","cc" );

  Py_INCREF( Py_None );
  return Py_None;
}



static PyMethodDef UuutimeMethods[] = {
  {"get_time", get_time, METH_VARARGS,
    "Return the uuutime reported by Avalon."},
  {"set_time", set_time, METH_VARARGS,
    "Set avalon's uuutime."},
  {NULL, NULL, 0, NULL}
};

void init_uuutimemodule() {
  Py_InitModule( "uuutime", UuutimeMethods );
}
