%ifndef __THREAD_INCLUDE__
%define __THREAD_INCLUDE__


%include "ring_queue.asm"

; Single processor critical section control
%macro ENTER_CRITICAL_SECTION 0.nolist
  pushfd
  cli
%endmacro
%define LEAVE_CRITICAL_SECTION popfd


struc _thread_timer_t
.procedure	resd 1
.execution_time	resd 2
.ring		resb _ring_queue_t_size
endstruc



; Realtime Thread Header
;------------------------------------------------------------------------------
; This structure is created for every realtime thread in the system and is
; located at the top of a thread's stack.
;
; The '*_link' are used to chain the thread header in both the timer queue or
; the priority execution queue.
;
; The execution 'start' and 'end' times are specified in unadjusted Uuu-Time
; difference since the scheduler initialization.
;
; The 'event notifier' is a callback function used to receive various
; notification about the execution of the thread, such as:
%define RT_EVENT_DELAYED_EXECUTION	0x01
%define RT_EVENT_THREAD_PREEMPTED	0x02
%define RT_EVENT_INSTRUCTION_FAULT	0x04
%define RT_EVENT_COPROCESSOR_FAULT	0x08
%define RT_EVENT_THREAD_EXPIRED		0x10
;
; The 'event mask' is used the above defined values for disabling certain event
; type notifications.
;
; The 'execution priority' is the priority associated to the thread.  It may
; or may not be at all time the currently executing priority, if for example
; a higher priority thread is lending time until a mutex is unlocked.
;
; The 'locked mutexes' is a count of locked mutexes, mostly used in deadlock
; prevention and help programmers in the development of their software.
;
; The 'execution status' indicate one of the following state:
%define RT_SCHED_STATUS_UNSCHEDULED	0x00
%define RT_SCHED_STATUS_SLEEPING	0x01
%define RT_SCHED_STATUS_RUNNING		0x02
%define RT_SCHED_STATUS_WAITING		0x03
;
; The 'flags' are used by the scheduler for various tracking functions:
;
;   bit	description
;
;     0	lended time run (0=no, 1=running under lended time)
%define RT_FLAGS_LENDED_TIME		0x00
;
;     1 realtime thread select (0=non-rt, 1=realtime)
%define RT_FLAGS_RTSELECT		0x01
;
;     2	initialized status (0=unitialized, 1=initialized)
%define RT_FLAGS_INIT_STATUS		0x02
;
;   3-7	reserved
;------------------------------------------------------------------------------
struc _thread_t			; ----- ; -------------------------------------
.start_timer		resb _thread_timer_t_size
.end_timer		resb _thread_timer_t_size
.resources_ring		resb _ring_queue_t_size
.top_of_stack           resd 1	; 20-23 ; active TOS (ESP)
.bottom_of_stack	resd 1	; 24-27 ; Lowest allowed ESP
.process_id             resd 1	; 28-2B ; ID of parent process
.event_notifier         resd 1	; 2C-2F ; callback for event forwarding
.event_mask		resd 1	; 30-33 ; mask some event types
.thread_pool		resd 1	; 34-37 ;
.execution_priority	resb 1	; 38-38 ; selected execution priority
.locked_mutexes		resb 1	; 39-39 ; number of locked mutexes
.execution_status	resb 1	; 3A-3A ; execution status
.flags			resb 1	; 3B-3B ; thread flags
.magic			resd 1	; 3C-3F ;
endstruc                        ; ----- ; -------------------------------------
;------------------------------------------------------------------------------


; Mutex
;------------------------------------------------------------------------------
; This is the structure used for mutexes, which are dynamically allocated 
; unless fine-tuning is done by a third-party in a fixed version development
; environment.
;
;------------------------------------------------------------------------------
struc _mutex_t			; ----- ; -------------------------------------
.holding_thread	resd 1		;   -   ; thread currently holding the lock
.magic		resd 1		;   -   ;
.wait_queue	resb _ring_queue_t_size	;
endstruc			; ----- ; -------------------------------------
;------------------------------------------------------------------------------


%endif
