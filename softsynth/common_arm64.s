.macro PUSH_LINK_REGISTER
    str x30, [sp, #-16]!   // Push x30 onto the stack (decrement sp by 16, store x30)
.endmacro

.macro POP_LINK_REGISTER
    ldr x30, [sp], #16     // Pop x30 from the stack (load x30, increment sp by 16)
.endmacro

.macro LOAD_ADDR reg, symbol
    adrp    \reg, \symbol@GOTPAGE
    ldr     \reg, [\reg, \symbol@GOTPAGEOFF]
.endmacro
