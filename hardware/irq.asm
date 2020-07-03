%include "interrupts.asm"

extern irq_module_handler

%macro c_irq_proxy 1
  global handler%1
  irq_client handler%1
  push byte 0x%1
  call irq_module_handler
  add esp, byte 4
  retn
%endmacro

c_irq_proxy 0
c_irq_proxy 1
c_irq_proxy 2
c_irq_proxy 3
c_irq_proxy 4
c_irq_proxy 5
c_irq_proxy 6
c_irq_proxy 7
c_irq_proxy 8
c_irq_proxy 9
c_irq_proxy A
c_irq_proxy B
c_irq_proxy C
c_irq_proxy D
c_irq_proxy E
c_irq_proxy F
