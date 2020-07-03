global __dietlibc_fstat64
global __syscall_getcwd
global __dietlibc_stat64
global stat
global llseek
global __rt_sigprocmask
global times
global __rt_sigaction
global __assert_fail
global initposix

__rt_sigprocmask:
  mov eax, 6
  cli
  mov esp, 0xdeadbeef
  jmp $
$times:
  mov eax, 7
  cli
  mov esp, 0xdeadbeef
  jmp $
__assert_fail:
  mov eax, 9
  cli
  mov esp, 0xdeadbeef
  jmp $
initposix:
  mov eax, 10
  cli
  mov esp, 0xdeadbeef
  jmp $
