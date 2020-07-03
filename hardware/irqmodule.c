#include <python2.3/Python.h>

#define IRQ_MAX 0x0F

unsigned int monitoredflag=0;
#define MONITORED(irq) (monitoredflag & (1 << irq) )

unsigned volatile int irqflags[IRQ_MAX+1] = { 0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 };

void irq_module_handler( int irq )
{
  irqflags[irq] += 1;
}

extern void handler0(void);
extern void handler1(void);
extern void handler2(void);
extern void handler3(void);
extern void handler4(void);
extern void handler5(void);
extern void handler6(void);
extern void handler7(void);
extern void handler8(void);
extern void handler9(void);
extern void handlerA(void);
extern void handlerB(void);
extern void handlerC(void);
extern void handlerD(void);
extern void handlerE(void);
extern void handlerF(void);

void (*hfunarray[IRQ_MAX+1])() = {
  handler0, handler1, handler2, handler3,
  handler4, handler5, handler6, handler7,
  handler8, handler9, handlerA, handlerB,
  handlerC, handlerD, handlerE, handlerF
};

static int hook_irq(unsigned char irq, void (*handler)())
{
  int result;
  int trash;
  asm volatile(
      "call irq.connect\n"
      ".long continue%=\n"
      ".long fail%=\n"
      "fail%=:\n"
      "xor %0, %0\n"
      "inc %0\n"
      "jmp done%=\n"
      "continue%=:\n"
      "xor %0, %0\n"
      "done%=:\n"
      : "=a"(result), "=b"(trash) : "a"(irq), "b"(handler) : "ecx","edx","cc"
     );
  return result;
}

static int unhook_irq(unsigned char irq, void (*handler)())
{
  int result;
  int trash;
  asm volatile(
      "call irq.disconnect\n"
      ".long continue%=\n"
      ".long fail%=\n"
      "fail%=:\n"
      "xor %0, %0\n"
      "inc %0\n"
      "jmp done%=\n"
      "continue%=:\n"
      "xor %0, %0\n"
      "done%=:\n"
      : "=a"(result), "=b"(trash) : "a"(irq), "b"(handler) : "ecx","edx","cc"
     );
  return result;
}

//Poll until specified IRQ is set, unset it, and return
static PyObject *sleep_until(PyObject *self, PyObject *args)
{
  unsigned char irq;

  if(!PyArg_ParseTuple(args, "b", &irq)) return NULL;

  if ( ! MONITORED(irq) ) {
    /* Raise ValueError */
    PyErr_SetString(PyExc_ValueError, "Cannot poll an IRQ that is not being monitored.");
    return NULL;
  }
  while (! irqflags[irq]); // TODO: make this a thread sleep
  irqflags[irq] -= 1;

  Py_INCREF( Py_None );
  return Py_None;
}

//Monitor IRQ
static PyObject *monitor(PyObject *self, PyObject *args)
{
  unsigned char irq;

  if(!PyArg_ParseTuple(args, "b", &irq)) return NULL;

  if (MONITORED(irq)) {
    PyErr_SetString(PyExc_ValueError, "Already monitoring specified IRQ.");
    return NULL;
  } else {
    monitoredflag |= 1 << irq;
    if( hook_irq(irq, hfunarray[irq]) ) {
      PyErr_SetString(PyExc_Exception, "could not connect to IRQ" );
      return NULL;
    }
  }

  Py_INCREF( Py_None );
  return Py_None;
}

//Stop monitoring IRQ
static PyObject *unmonitor(PyObject *self, PyObject *args) {
  unsigned char irq;

  if(!PyArg_ParseTuple(args, "b", &irq)) return NULL;

  if( !MONITORED(irq) ) {
    /* If bit is not set, raise ValueError */
    PyErr_SetString(PyExc_ValueError, "Specified IRQ is not being monitored.");
    return NULL;
  }
  monitoredflag &= ~(1 << irq);
  if( unhook_irq(irq, hfunarray[irq]) ) {
    PyErr_SetString(PyExc_Exception, "could not disconnect from IRQ" );
    return NULL;
  }

  Py_INCREF( Py_None );
  return Py_None;
}

static PyObject *reset(PyObject *self, PyObject *args) {
  unsigned char irq;

  if(!PyArg_ParseTuple(args, "b", &irq)) return NULL;

  irqflags[irq] = 0;

  Py_INCREF( Py_None );
  return Py_None;
}

static PyMethodDef IrqMethods[] = {
  {"sleep_until", sleep_until, METH_VARARGS,
    "Poll until the specified IRQ is set, unset it, and return."},
  {"monitor", monitor, METH_VARARGS,
    "Monitor an IRQ."},
  {"unmonitor", unmonitor, METH_VARARGS,
    "Stop monitoring an IRQ."},
  {"reset", reset, METH_VARARGS,
    "Reset the specified IRQ flag."},
  {NULL, NULL, 0, NULL}
};

void init_irqmodule() {
  Py_InitModule( "irq", IrqMethods );
}
