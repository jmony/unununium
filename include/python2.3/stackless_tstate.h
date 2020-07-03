/*** addition to tstate ***/

typedef struct _tasklet_flags {
    unsigned int atomic: 1;
	unsigned int ignore_nesting: 1;
    int blocked: 2;
    unsigned int block_trap: 1;
	unsigned int is_zombie: 1;
	unsigned int pending_irq: 1;
} PyTaskletFlagStruc;

typedef struct _sts {
    /* the blueprint for new stacks */
    struct _cstack *initial_stub;
    /* the counter that ensures that we always switch to the most recent stub */
#ifdef have_long_long
    long_long serial;
    long_long serial_last_jump;
#else
    long serial;
    long serial_last_jump;
#endif
    /* the list of all stacks of this thread */
    struct _cstack *cstack_chain;
    /* the base address for hijacking stacks */
    int *cstack_base;
    /* flags of the running tasklet */
    struct _tasklet_flags flags;
    /* main tasklet */
    struct _tasklet *main;
    /* runnable tasklets */
    struct _tasklet *current;
    int runcount;

    /* scheduling */
    int ticker;
    int interval;
    PyObject * (*interrupt) (void);    /* the fast scheduler */
    /* passing return values in soft switching mode */
    PyObject * tempval;
    /* trap recursive scheduling via callbacks */
    int schedlock;

    /* number of nested interpreters (1.0/2.0 merge) */
    int nesting_level;
    /* common return frame for all tasklets (3.0) */
	/* XXX this is about to be removed, since we always hacve cframes on top now */
    struct _frame *tasklet_runner;
} PyStacklessState;


/* these macros go into pystate.c */
#define STACKLESS_PYSTATE_NEW \
    tstate->st.initial_stub = NULL; \
    tstate->st.serial = 0; \
    tstate->st.serial_last_jump = 0; \
    tstate->st.cstack_chain = NULL; \
    tstate->st.cstack_base = NULL; \
    *(int*)&tstate->st.flags = 0; \
    tstate->st.ticker = 0; \
    tstate->st.interval = 0; \
    tstate->st.interrupt = NULL; \
    tstate->st.tempval = NULL;\
    tstate->st.schedlock = 0; \
    tstate->st.main = NULL; \
    tstate->st.current = NULL; \
    tstate->st.runcount = 0; \
    tstate->st.nesting_level = 0; \
    tstate->st.tasklet_runner = NULL;

/* note that the scheduler knows how to zap. It checks if it is in charge
   for this tstate and then clears everything. This will not work if
   we use ZAP, since it clears the pointer before deallocating.
 */

struct _ts; /* Forward */

void slp_kill_tasks_with_stacks(struct _ts *tstate);

#define STACKLESS_PYSTATE_ZAP \
    slp_kill_tasks_with_stacks(tstate); \
    ZAP(tstate->st.initial_stub); \
    ZAP(tstate->st.tasklet_runner);
