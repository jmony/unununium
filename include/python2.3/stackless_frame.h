#ifndef STACKLESS_FRAME_H
#define STACKLESS_FRAME_H

PyAPI_DATA(PyTypeObject) PyCFrame_Type;
PyAPI_DATA(PyTypeObject) PyBaseFrame_Type;

#define PyBaseFrame_Check(op) PyObject_TypeCheck(op, &PyBaseFrame_Type)
#define PyBaseFrame_CheckExact(op) ((op)->ob_type == &PyBaseFrame_Type)
#define PyCFrame_Check(op) PyObject_TypeCheck(op, &PyCFrame_Type)
#define PyCFrame_CheckExact(op) ((op)->ob_type == &PyCFrame_Type)

/* support for soft stackless */

typedef PyObject *(PyFrame_ExecFunc) (struct _frame *);

#endif

