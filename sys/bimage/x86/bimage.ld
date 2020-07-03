/*
 * ld script for x86 boot image
 */

ENTRY(_start)

SECTIONS
{
  /* waste of space... */
  /DISCARD/ :
  {
    *(.note*)
    *(.comment)
  }

  /* set output to be fixed at 1M */
  . = 1M;

  .data	: { *(multiboot) *(.data) *(.rodata*) *(.eh_frame) }
  .text	: { *(.text) }
  .bss	: { *(.bss) }

  PROVIDE( memory_bottom = . );
}
