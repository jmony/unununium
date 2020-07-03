;---------------===============\                 /===============---------------
				section multiboot	noalloc align=4
;---------------===============/                 \===============---------------

align 4

%define MBOOT_HDR_MAGIC	0x1BADB002

; possible flags...
%define MBOOT_HDR_MODULE_ALIGN	1	; align modules on page boundries
%define MBOOT_HDR_MEMINFO	2	; ask for memory information
%define MBOOT_HDR_NOT_ELF	0x1000	; don't use this; we use ELF ;)

; ...and the flags we actually want
%define MBOOT_HDR_FLAGS		MBOOT_HDR_MEMINFO
%include "bochs.asm"

%define MBOOT_EAX_MAGIC 0x2BADB002



dd MBOOT_HDR_MAGIC
dd MBOOT_HDR_FLAGS
dd - MBOOT_HDR_MAGIC - MBOOT_HDR_FLAGS

;---------------===============\             /===============---------------
				section .text
;---------------===============/             \===============---------------


global _start
_start:
  cmp eax, MBOOT_EAX_MAGIC
  jnz .not_mboot
  mov [multiboot_info], ebx
  mov eax, [ebx]
  test al, 0x1
  jz .no_mem_info
  mov ecx, [ebx+0x8]	; ecx = upper memory, in KiB (ie, ram in system / 1024 - 1024)
  add ecx, 1024
  shl ecx, 10
  extern memory_frame
  extern memory_frame_top
  mov [memory_frame], ecx
  mov [memory_frame_top], ecx

  mov edi, 0xb8000
  mov ecx, 0x2000
  mov eax, 0x07200720
  rep stosd

  extern __interrupt_init
  call __interrupt_init
  extern __scheduler_init
  call __scheduler_init

  extern c_stuff
  call c_stuff
  jmp exit_syscall

.not_mboot:
  mov esi, .not_mboot_error
  jmp short .fatal_error

.no_mem_info:
  mov esi, .no_mem_info_error
  jmp short .fatal_error

[section .data]
.not_mboot_error: db "not loaded from multiboot bootloader",0
.no_mem_info_error: db "multiboot bootloader did not provide memory information",0
__SECT__

.fatal_error:
  mov edi, 0xb8000
  mov ah, 0x4f
.print_char:
  lodsb
  test al, al
  jz .die
  stosw
  jmp short .print_char
.die:
  cli
  hlt
  jmp .die



global exit_syscall
exit_syscall:
  ; anything using exit() in C will come here. For now that's just Python.
  extern Py_Finalize
  call Py_Finalize
  mov al, 0xFE
  out 0x64, al
  mov al, 0x01
  out 0x92, al
  cli
  jmp short $



global get_multiboot_info
get_multiboot_info:
  mov eax, [multiboot_info]
  retn



;---------------===============\            /===============---------------
				section .bss
;---------------===============/            \===============---------------

multiboot_info: resd 1



;---------------===============\             /===============---------------
				section .data
;---------------===============/             \===============---------------

global block_device_py
block_device_py:
incbin "../../../python_modules/block_device.py"
dd 0

global floppy_py
floppy_py:
incbin "../../../python_modules/floppy.py"
dd 0

global ata_py
ata_py:
incbin "../../../python_modules/ata.py"
dd 0

global ext2_py
ext2_py:
incbin "../../../python_modules/ext2.py"
dd 0

global vfs_py
vfs_py:
incbin "../../../python_modules/vfs.py"
dd 0

global uuu_py
uuu_py:
incbin "../../../python_modules/uuu.py"
dd 0

global ramfs_py
ramfs_py:
incbin "../../../python_modules/ramfs.py"
dd 0

global shell_py
shell_py:
incbin "../../../python_modules/shell.py"
dd 0

global init_py
init_py:
incbin "init.py"
dd 0

global disk_cache_py
disk_cache_py:
incbin "../../../python_modules/disk_cache.py"
dd 0

global simpleconsole_py
simpleconsole_py:
incbin "../../../python_modules/simpleconsole.py"
dd 0
