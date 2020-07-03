; $Header: /var/cvsroot/uuu/uuu/include/ref_count.asm,v 1.3 2004/01/25 15:11:12 indigo Exp $

%ifndef __REF_COUNT_INCLUDE__
%define __REF_COUNT_INCLUDE__


struc ref_counted
  .ref:		resd 1
  .destroy:	resd 1
endstruc


;! <proc name="ref_counted.destroy">
;!   All procedures used in ref_counted.destroy conform to this interface.
;!
;!   <p type="pointer" reg="eax" brief="object to destroy"/>
;!
;!   <ret brief="success"/>
;!   <ret brief="other"/>
;! </proc>


;-----------------------------------------------------------------------.
;						dec_ref			;

; decrement the reference count of something, and if it reaches 0, call the
; destructor. Keep in mind that the DESTROYED and OTHER return states call
; procedures, so they destroy registers.
;
; usage: dec_ref OBJECT, NONZERO, DESTROYED, OTHER
;
; OBJECT is a pointer to the object of which to decrement the reference count.
; It must be either an immediate label or a register.
;
; NONZERO is the return point if the reference count was decremented but it
; didn't reach zero, thus the destructor was not called. It may be "CONT".
;
; DESTROYED is the return point in the case that the destructor was called and
; succeeded. In the style of ecall, it may be "CONT".
;
; OTHER is the return point in the case that the destructor was called and
; returned other, or if something bad happened, such as an attempt to
; decrement the count past zero was made. In the style of ecall, it may be
; "CONT".

%macro dec_ref 4
  dec dword[%1+ref_counted.ref]

  %ifidn %2, CONT
    jz %%continue
  %else
    jz %2
  %endif

  %ifdef SANITY_CHECKS
    %ifidn %3, CONT
      jc %%continue
    %else
      jc %3
    %endif
  %endif

  mov eax, %1
  call [eax+ref_counted.destroy]
  %ifidn %3, CONT
    dd %%continue
  %else
    dd %3
  %endif
  %ifidn %4, CONT
    dd %%continue
  %else
    dd %4
  %endif

  %%continue:
%endmacro



%endif
