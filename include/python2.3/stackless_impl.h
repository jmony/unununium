#ifndef STACKLESS_IMPL_H
#define STACKLESS_IMPL_H

#include "Python.h"

#ifdef STACKLESS

#ifdef __cplusplus
extern "C" {
#endif

#include "structmember.h"
#include "compile.h"
#include "frameobject.h"

#include "flextype.h"
#include "stackless_frame.h"
#include "stackless_structs.h"

#undef STACKLESS_SPY
/* 
 * if a platform wants to support self-inspection via _peek,
 * it must provide a function or macro CANNOT_READ_MEM(adr, len)
 * which allows to spy at memory without causing exceptions.
 * This would usually be done in place with the assembly macros.
 */

/* extract the lower bit of Py_TPFLAGS_HAVE_STACKLESS_EXTENSION */

#define Py_TPFLAGS_HAVE_STACKLESS_CALL \
	(Py_TPFLAGS_HAVE_STACKLESS_EXTENSION & (Py_TPFLAGS_HAVE_STACKLESS_EXTENSION >> 1))

/********************************************************************
 *
 * This section defines/references stuff from stacklesseval.c
 *
 ********************************************************************/

/*** access to system-wide globals from stacklesseval.c ***/

PyAPI_DATA(int) slp_enable_softswitch;
PyAPI_DATA(int) slp_try_stackless;

PyAPI_FUNC(PyCStackObject *) slp_cstack_new(PyCStackObject **cst, int *stackref, PyTaskletObject *task);
PyAPI_FUNC(int) slp_cstack_save(PyCStackObject *cstprev);
PyAPI_FUNC(void) slp_cstack_restore(PyCStackObject *cst);

PyAPI_FUNC(int) slp_transfer(PyCStackObject **cstprev, PyCStackObject *cst, PyTaskletObject *prev);

PyAPI_FUNC(int) _PyStackless_InitTypes(void);
PyAPI_FUNC(void) _PyStackless_Init(void);

/* clean-up up at the end */

PyAPI_FUNC(void) PyStacklessEval_Fini(void);

PyAPI_FUNC(void) PyStackless_kill_tasks_with_stacks(void);

/* the special version of eval_frame */
PyAPI_FUNC(PyObject *) slp_eval_frame(struct _frame *f);

/* the frame dispatcher */
PyAPI_FUNC(PyObject *) slp_frame_dispatch(PyFrameObject *f, PyFrameObject *stopframe);

/* the frame dispatcher for toplevel tasklets */
PyAPI_FUNC(PyObject *) slp_frame_dispatch_top(PyFrameObject *f);

/* the now exported eval_frame */
PyAPI_FUNC(PyObject *) PyEval_EvalFrame(struct _frame *f);

/* the new eval_frame loop with or without value or resuming an iterator */
PyAPI_FUNC(PyObject *) PyEval_EvalFrame_value(struct _frame *f);
PyAPI_FUNC(PyObject *) PyEval_EvalFrame_noval(struct _frame *f);
PyAPI_FUNC(PyObject *) PyEval_EvalFrame_iter(struct _frame *f);

/* rebirth of software stack avoidance */

PyAPI_DATA(PyObject *) Py_UnwindToken;

/* frame cloning both needed in tasklets and generators */

PyAPI_FUNC(struct _frame *) slp_clone_frame(struct _frame *f);
PyAPI_FUNC(struct _frame *) slp_ensure_new_frame(struct _frame *f);

/* exposing the generator type */

PyAPI_DATA(PyTypeObject) PyGenerator_Type;
PyAPI_FUNC(PyObject *) PyGenerator_New(struct _frame *f);

/* macros for setting/resetting the stackless flag */

#define STACKLESS_GETARG() int stackless = (stackless = slp_try_stackless, slp_try_stackless = 0, stackless)

#define STACKLESS_PROMOTE(func) \
    (stackless ? slp_try_stackless = \
		(func)->ob_type->tp_flags & Py_TPFLAGS_HAVE_STACKLESS_CALL : 0)

#define STACKLESS_PROMOTE_FLAG(flag) \
	(stackless ? slp_try_stackless = (flag) : 0)

#define STACKLESS_PROMOTE_ALL() (slp_try_stackless = stackless, NULL)

#define STACKLESS_PROPOSE(func) {int stackless = 1; STACKLESS_PROMOTE(func);}

#define STACKLESS_PROPOSE_FLAG(flag) {int stackless = 1; STACKLESS_PROMOTE_FLAG(flag);}

#define STACKLESS_PROPOSE_ALL() slp_try_stackless = 1;

#define STACKLESS_RETRACT() slp_try_stackless = 0;

#define STACKLESS_ASSERT() assert(!slp_try_stackless)

/*

  How this works:
  There is one global variable slp_try_stackless which is used
  like an implicit parameter. Since we don't have a real parameter,
  the flag is copied into the local variable "stackless" and cleared.
  This is done by the GETARG() macro, which should be added to
  the top of the function's declarations.
  The idea is to keep the changes to introduce error to the minimum.
  A function can safely do some tests and return before calling
  anything, since the flag is in a local variable.
  Depending on context, this flag is propagated to other called
  functions. They *must* obey the protocol. To make this sure,
  the ASSERT() macro has to be called after every such call.

  Many internal functions have been patched to support this protocol.

  GETARG()

	move the slp_ry_stackless flag into the local variable "stackless".

  PROMOTE(func)
  
	if stackless was set and the function's type has set
	Py_TPFLAGS_HAVE_STACKLESS_CALL, then this flag will be
	put back into slp_try_stackless, and we expect that the
	function handles it correctly.

  PROMOTE_FLAG(flag)

	is used for special cases, like PyCFunction objects. PyCFunction_Type
	says that it supports a stackless call, but the final action depends
	on the METH_STACKLESS flag in the object to be called. Therefore,
	PyCFunction_Call uses PROMOTE_FLAG(flags & METH_STACKLESS) to
	take care of PyCFunctions which doen't care about it.

	Another example is the "next" method of iterators. To support this,
	the wrapperobject's type has the Py_TPFLAGS_HAVE_STACKLESS_CALL
	flag set, but wrapper_call then examines the wrapper descriptors
	flags if PyWrapperFlag_STACKLESS is set. "next" has it set.
	It also checks whether Py_TPFLAGS_HAVE_STACKLESS_CALL is set
	for the iterator's type.

  PROMOTE_ALL()

	is used for cases where we know that the called function will take
	care of our object, and we need no test. For example, PyObject_Call
	uses PROMOTE, itself, so we don't need to check further.

  ASSERT()

	make sure that slp_ry_stackless was cleared. This debug feature
	tries to ensure that no unexpected nonrecursive call can happen.
	
  Some functions which are known to be stackless by nature
  just use the PROPOSE macros. They do not care about prior state.
  Most of them are used in ceval.c and other contexts which are
  stackless by definition. All possible nonrecursive calls are
  initiated by these macros.

*/


/********************************************************************
 *
 * This section defines/references stuff from stacklessmodule.c
 *
 ********************************************************************/

PyAPI_DATA(PyTypeObject) PyBaseFrame_Type;
PyAPI_DATA(PyTypeObject) PyCFrame_Type;

/* generic ops for chained objects */

/*  Tasklets are in doubly linked lists. We support
    deletion and insertion */

#define SLP_CHAIN_INSERT(__objtype, __chain, __task, __next, __prev) \
{ \
    __objtype *l, *r; \
	assert((__task)->__next == NULL); \
	assert((__task)->__prev == NULL); \
    if (*(__chain) == NULL) { \
        (__task)->__next = (__task)->__prev = (__task); \
        *(__chain) = (__task); \
    } \
    else { \
        /* insert at end */ \
        r = *(__chain); \
        l = r->__prev; \
        l->__next = r->__prev = (__task); \
        (__task)->__prev = l; \
        (__task)->__next = r; \
    } \
}

#define SLP_CHAIN_REMOVE(__objtype, __chain, __task, __next, __prev) \
{ \
    __objtype *l, *r; \
    if (*(__chain) == NULL) { \
        (__task) = NULL; \
    } \
    else { \
        /* remove current */ \
        (__task) = *(__chain); \
        l = (__task)->__prev; \
        r = (__task)->__next; \
        l->__next = r; \
        r->__prev = l; \
        *(__chain) = r; \
        if (*(__chain)==(__task)) \
            *(__chain) = NULL;  /* short circuit */ \
        (__task)->__prev = NULL; \
        (__task)->__next = NULL; \
    } \
}

/* operations on chains */

PyAPI_FUNC(void) slp_current_insert(PyTaskletObject *task);
PyAPI_FUNC(void) slp_current_insert_after(PyTaskletObject *task);
PyAPI_FUNC(PyTaskletObject *) slp_current_remove(void);
PyAPI_FUNC(void) slp_channel_insert(PyChannelObject *channel, PyTaskletObject *task, int dir);
PyAPI_FUNC(PyTaskletObject) * slp_channel_remove(PyChannelObject *channel, int dir);
PyAPI_FUNC(PyTaskletObject) * slp_channel_remove_specific(PyChannelObject *channel, int dir, PyTaskletObject *task);

/* tasklet operations */
PyAPI_FUNC(PyObject *) slp_tasklet_new(PyTypeObject *type, PyObject *args, PyObject *kwds);

PyAPI_FUNC(int) slp_schedule_task(PyTaskletObject *prev, PyTaskletObject *next);
PyAPI_FUNC(int) slp_schedule_nr_maybe(PyTaskletObject *prev, PyTaskletObject *next);

PyObject * slp_run_tasklet(PyFrameObject *f);
int initialize_main_and_current(PyFrameObject *f);

/* handy abbrevations */

PyObject * slp_type_error(const char *msg);
PyObject * slp_runtime_error(const char *msg);
PyObject * slp_value_error(const char *msg);
PyObject * slp_null_error(void);

/* this seems to be needed for gcc */

/* Define NULL pointer value */

#undef NULL
#ifdef  __cplusplus
#define NULL    0
#else
#define NULL    ((void *)0)
#endif

#define TYPE_ERROR(str, ret) (slp_type_error(str), ret)
#define RUNTIME_ERROR(str, ret) (slp_runtime_error(str), ret)
#define VALUE_ERROR(str, ret) (slp_value_error(str), ret)

PyBaseFrameObject * slp_baseframe_new(PyFrame_ExecFunc *exec, unsigned int linked, 
                                      unsigned int extra);
PyCFrameObject * slp_cframe_new(PyObject *func, PyObject *args, PyObject *kwds, unsigned int linked);

PyFrameObject * slp_get_frame(PyTaskletObject *task);
PyTaskletFlagStruc * slp_get_flags(PyTaskletObject *task);
void slp_check_pending_irq(void);
int slp_return_wrapper(PyObject *retval);
int slp_int_wrapper(PyObject *retval);
int slp_current_wrapper( int(*func)(PyTaskletObject*), PyTaskletObject *task);
int slp_revive_main(void);

/* debugging/monitoring */

typedef void (slp_schedule_hook_func) (PyTaskletObject *from, PyTaskletObject *to);
PyAPI_DATA(slp_schedule_hook_func) *_slp_schedule_fasthook;
PyAPI_DATA(PyObject* ) _slp_schedule_hook;
void slp_schedule_callback(PyTaskletObject *prev, PyTaskletObject *next);

#include "stackless_api.h"

#else /* STACKLESS */

/* turn the stackless flag macros into dummies */

#define STACKLESS_GETARG() int stackless = 0
#define STACKLESS_PROMOTE(func) stackless = 0
#define STACKLESS_PROMOTE_FLAG(flag) stackless = 0
#define STACKLESS_PROMOTE_ALL() stackless = 0
#define STACKLESS_PROPOSE(func) assert(1)
#define STACKLESS_PROPOSE_FLAG(flag) assert(1)
#define STACKLESS_PROPOSE_ALL() assert(1)
#define STACKLESS_RETRACT() assert(1)
#define STACKLESS_ASSERT() assert(1)

#endif /* STACKLESS */

#ifdef __cplusplus
}
#endif

#endif
