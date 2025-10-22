#include "common_arm64.s"
//#include "debug.inc"

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

;; From softsynth.asm
.extern	get_instrument_value
.extern	note_table
.extern	sampling_freq_const
.extern	f_instrument_delta
.extern	_instrument_ticks
#define instrument_ticks _instrument_ticks
.extern	f_instrument_offset
.extern	f_instrument_modo

;; For AED
.global	_get_instrument_value_c
#define get_instrument_value_c _get_instrument_value_c
.global	_start_instrument
#define start_instrument _start_instrument

.text
;; Output:	eax <- Value

// ARM64 version: int get_instrument_value_c(int instrument)
// Argument: x0 = instrument
// Return:   w0 = result (int)
get_instrument_value_c:
    PUSH_LINK_REGISTER
	// Save callee-saved registers if needed (none used here)
	// Prepare argument for get_instrument_value (x5 = instrument * 4)
	mov x5, x0
	bl get_instrument_value
	// get_instrument_value returns result in s1 (float)
	fcvtzs w0, s1   // Convert float in s1 to signed int in w0
    POP_LINK_REGISTER
	ret

;; 440Hz -> 2 * Pi * 440 / 44100 increase per tick

// ARM64 version: void start_instrument(int instrument, int tone)
// Arguments: x0 = instrument, x1 = tone
// No return value
start_instrument:
	// x0 = instrument, x1 = tone
	lsl x2, x0, #2                // x2 = instrument * 4 (offset)
	lsl x3, x1, #2                // x3 = tone * 4 (offset)
	LOAD_ADDR x4, note_table
	ldr  s0, [x4, x3]             // s0 = note_table[tone]
	// Load pi from memory (cannot use fmov for arbitrary float)
	LOAD_ADDR x10, pi_const
	ldr  s1, [x10]                // s1 = pi
	fadd s1, s1, s1               // s1 = 2 * pi
	fmul s0, s0, s1               // s0 = 2 * pi * freq
	LOAD_ADDR x5, sampling_freq_const
	ldr  s1, [x5]                 // s1 = f_sampling_freq
	fdiv s0, s0, s1               // s0 = 2 * pi * freq / f_sampling_freq
	LOAD_ADDR x6, f_instrument_delta
	str  s0, [x6, x2]             // f_instrument_delta[instrument] = result
	fmov s0, #0.0                 // s0 = 0.0
	LOAD_ADDR x7, instrument_ticks
	str  wzr, [x7, x2]            // instrument_ticks[instrument] = 0
	LOAD_ADDR x8, f_instrument_offset
	str  wzr, [x8, x2]            // f_instrument_offset[instrument] = 0
	LOAD_ADDR x9, f_instrument_modo
	str  wzr, [x9, x2]            // f_instrument_modo[instrument] = 0
	ret

// Constant for pi (if not already present in this file)
.data
.align 4
pi_const: .float 3.1415927
