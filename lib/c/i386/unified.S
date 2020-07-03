.weak exit
exit:
.global _exit
.type	_exit,@function
_exit:
	jmp exit_syscall
exit_end:
.size _exit,exit_end-_exit

#include "dietuglyweaks.h"

	ret
