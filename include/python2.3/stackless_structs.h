#ifndef STACKLESS_STRUCTS_H
#define STACKLESS_STRUCTS_H

#ifdef __cplusplus
extern "C" {
#endif



/*** important structures: tasklet ***/


/***************************************************************************

	Tasklet Flag Definition
	-----------------------

	active:			This tasklets is currently running. The frame
					and flags attributes of the tasklet are invalid
					and mapped to tstate. Maintenance of these fields
					is done during switching.
					This is now a computed attribute.

	atomic:			If true, schedulers will never switch. Driven by
					the code object or dynamically, see below.

	scheduled:		The tasklet likes to be auto-scheduled. User driven.

	blocked:		The tasklet is either waiting in a channel for
					writing (1) or reading (-1) or not blocked(0).
					Maintained by the channel logic. Do not change.

	block_trap:		Debugging aid. Whenever the tasklet would be
					blocked by a channel, an exception is raised.

    is_zombie:      This tasklet is almost dead, its deallocation has
                    started. The tasklet *must* die at some time, or the
                    process can never end.


  Policy for atomic/schedule and switching:
	-----------------------------------------
	A tasklet switch can always be done explicitly by calling schedule().
	Atomic and schedule are concerned with automatic features.

	atomic	scheduled

		1		any		Neither a scheduler nor a watchdog will
						try to switch this tasklet.

		0		0		The tasklet can be stopped on desire, or it
						can be killed by an exception.

		0		1		Like above, plus auto-scheduling is enabled.

	Default settings:
	-----------------
	The default value of scheduled is taken from the global variable
	enable_scheduling in stacklessmodule. It can be set or cleared
	for every tasklet at any time.
	The value of atomic is normally calculated from the executed code
	object. Unless the code object has a special flag set, atomic
	will be saved on entry of the code object, set to true, and reset
	on exit. This protects you from crashing any unknown Python code.
	For known code objects, this mechanism can be turned off, and the
	atomic flag is under your control.

 ***************************************************************************/

/* 
 * note: the tasklet flags are living in stackless_tstate.h
 */

typedef struct _tasklet {
	PyObject_HEAD
	struct _tasklet *next;
	struct _tasklet *prev;
	union {
		struct _frame *frame;
		struct _cframe *cframe;
	} f;
/*
	PyObject *channel;
*/
	PyFrameObject *topframe;
	PyObject *tempval;
	/* bits stuff */
	struct _tasklet_flags flags;
	int recursion_depth;
	struct _cstack *cstate;
    PyObject *tsk_weakreflist;
} PyTaskletObject;


/*** important structures: cstack ***/

typedef struct _cstack {
    PyObject_VAR_HEAD
	struct _cstack *next;
	struct _cstack *prev;
#ifdef have_long_long
    long_long serial;
#else
    long serial;
#endif
	struct _tasklet *task;
	int nesting_level;
	PyThreadState *tstate;
	int *startaddr;
    int *stack[1];
} PyCStackObject;


/*** important structures: channel ***/

typedef struct _channel {
	PyObject_HEAD
	struct _tasklet *queue;
	int balance;
    PyObject *chan_weakreflist;
} PyChannelObject;


/*** important stuctures: baseframe, cframe ***/

typedef struct _baseframe {
    PyObject_VAR_HEAD
    struct _frame *f_back;	/* previous frame, or NULL */
	PyFrame_ExecFunc *f_execute;

	/* 
	 * the above part is compatible with frames.
	 * Note that I have re-arranged some fields in the frames
	 * to keep cframes as small as possible.
	 */

} PyBaseFrameObject;


/* "derived" cframe */

typedef struct _cframe {
    PyBaseFrameObject bf;
	PyObject *callable;
	PyObject *args;
	PyObject *kwds;
} PyCFrameObject;


/*** important structures: slpmodule ***/

typedef struct _slpmodule {
	PyObject_HEAD
	PyObject *md_dict;
	/* the above is a copy of private PyModuleObject */
	PyTypeObject *__tasklet__;
	PyTypeObject *__channel__;
} PySlpModuleObject;


/*** associated type objects ***/

/* PyCFrame_Type in stackless_frame.h */

PyAPI_DATA(PyTypeObject) PyEnumFactory_Type;
#define PyEnumFactory_Check(op) PyObject_TypeCheck(op, &PyEnumFactory_Type)
#define PyEnumFactory_CheckExact(op) ((op)->ob_type == &PyEnumFactory_Type)

PyAPI_DATA(PyTypeObject) PyModuleDict_Type;
#define PyModuleDict_Check(op) PyObject_TypeCheck(op, &PyModuleDict_Type)
#define PyModuleDict_CheckExact(op) ((op)->ob_type == &PyModuleDict_Type)

PyAPI_DATA(PyTypeObject) PyCStack_Type;

PyAPI_DATA(PyTypeObject*) PyTasklet_TypePtr;
#define PyTasklet_Type (*PyTasklet_TypePtr)
#define PyTasklet_Check(op) PyObject_TypeCheck(op, PyTasklet_TypePtr)
#define PyTasklet_CheckExact(op) ((op)->ob_type == PyTasklet_TypePtr)

PyAPI_DATA(PyTypeObject*) PyChannel_TypePtr;
#define PyChannel_Type (*PyChannel_TypePtr)
#define PyChannel_Check(op) PyObject_TypeCheck(op, PyChannel_TypePtr)
#define PyChannel_CheckExact(op) ((op)->ob_type == PyChannel_TypePtr)

/*** these are in other bits of Python ***/
PyAPI_DATA(PyTypeObject) PyDictIter_Type;
PyAPI_DATA(PyTypeObject) PyListIter_Type;
PyAPI_DATA(PyTypeObject) Pyrangeiter_Type;
PyAPI_DATA(PyTypeObject) PyTupleIter_Type;
PyAPI_DATA(PyTypeObject) PyEnum_Type;

/*** the Stackless module itself ***/
PyAPI_DATA(PyObject *) slp_module;

#ifdef __cplusplus
}
#endif

#endif
