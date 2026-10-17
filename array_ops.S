/* GNU assembler, Intel syntax, Linux x86-64 System V ABI.
 * First three integer/pointer arguments: RDI, RSI, RDX; result: RAX.
 * Leaf functions: only caller-saved registers are modified. */
.intel_syntax noprefix
.text

.globl sum_i32
.type sum_i32, @function
sum_i32:
    xor eax, eax                 /* 64-bit accumulator becomes zero */
    xor ecx, ecx                 /* index */
.Lsum_loop:
    cmp rcx, rsi
    jae .Lsum_done               /* unsigned size_t comparison */
    movsxd rdx, DWORD PTR [rdi + rcx * 4]
    add rax, rdx                 /* sign-extend BEFORE addition */
    inc rcx
    jmp .Lsum_loop
.Lsum_done:
    ret
.size sum_i32, .-sum_i32

.globl count_equal_i32
.type count_equal_i32, @function
count_equal_i32:
    xor eax, eax
    xor ecx, ecx
.Lcount_loop:
    cmp rcx, rsi
    jae .Lcount_done
    cmp DWORD PTR [rdi + rcx * 4], edx
    jne .Lcount_next
    inc rax
.Lcount_next:
    inc rcx
    jmp .Lcount_loop
.Lcount_done:
    ret
.size count_equal_i32, .-count_equal_i32

.globl reverse_i32
.type reverse_i32, @function
reverse_i32:
    cmp rsi, 2
    jb .Lreverse_done            /* avoids underflow for an empty array */
    xor ecx, ecx                 /* left index */
    lea rdx, [rsi - 1]           /* right index */
.Lreverse_loop:
    mov eax, DWORD PTR [rdi + rcx * 4]
    mov r8d, DWORD PTR [rdi + rdx * 4]
    mov DWORD PTR [rdi + rcx * 4], r8d
    mov DWORD PTR [rdi + rdx * 4], eax
    inc rcx
    dec rdx
    cmp rcx, rdx
    jb .Lreverse_loop
.Lreverse_done:
    ret
.size reverse_i32, .-reverse_i32

/* This object does not require an executable stack. */
.section .note.GNU-stack,"",@progbits
