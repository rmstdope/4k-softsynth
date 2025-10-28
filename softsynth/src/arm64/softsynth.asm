// Insights
// It is impossible to run 32-bit code on a 64-bit only CPU like Apple Mx Silicon. Learn to live with it!
// Please adhere to the ARM64 Procedure Call Standard (AAPCS) when writing functions.
// https://developer.arm.com/documentation/102374/0102/Procedure-Call-Standard
// Read up on:
// https://developer.arm.com/documentation/102374/0102/Program-flow---conditional-select-instructions

// LLDB
// -exec b <function_name>
// -exec b <file>:<line>
// -exec p <variable_name>

#include "common.asm"

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

// Standard softsynth entry point
.global _dope4ks_render
#define dope4ks_render _dope4ks_render

// For testing
.global _transform_values
#define transform_values _transform_values
.global _transformed_parameters
#define transformed_parameters _transformed_parameters
.global _envelope_function
#define envelope_function _envelope_function
.global _storeval_function
#define storeval_function _storeval_function
.global _operation_function
#define operation_function _operation_function
.global _oscillator_function
#define oscillator_function _oscillator_function
.global _output_function
#define output_function _output_function
.global _accumulate_function
#define accumulate_function _accumulate_function
.global _process_stack
#define process_stack _process_stack
.global _instrument_instructions_lookup
#define instrument_instructions_lookup _instrument_instructions_lookup
.global _new_instrument_note
#define new_instrument_note _new_instrument_note
.global _debug_start_instrument_note
#define debug_start_instrument_note _debug_start_instrument_note
.global _debug_next_instrument_sample
#define debug_next_instrument_sample _debug_next_instrument_sample
.global _synth_data
#define synth_data _synth_data

// Song data
.extern _instrument_instructions
#define instrument_instructions _instrument_instructions
.extern _instrument_parameters
#define instrument_parameters _instrument_parameters
.extern _instrument_patterns
#define instrument_patterns _instrument_patterns
.extern _pattern_array
#define pattern_array _pattern_array

.text

#ifdef DEBUG
/// Start a note on a specific instrument
///
/// Arguments:
///   instrument_num in x0
///   note_num in x1
debug_start_instrument_note:
    // x5 = instrument data
    LOAD_ADDR   x10, synth_data
    mov         x3, #instrument_length
    mul         x4, x0, x3
    add         x5, x10, x4
    mov         x14, x5
    mov         x16, #MAX_COMMANDS * MAX_COMMAND_PARAMS / 4
1:
    stp         xzr, xzr, [x14], #16
    subs        x16, x16, #1
    bne         1b
    // final 12 bytes
    str         xzr, [x14], #8
    str         wzr, [x14], #4
    // Set note value
    str         w1, [x5, #instrument_note]
    ret

/// Start a note on a specific instrument
///
/// Arguments:
///   instrument_num in x0
///   pointer to output buffer in x1
///   whatever should be in RELEASE in x2
debug_next_instrument_sample:
    PUSH_LINK_REGISTER
    // Constants
    fmov        s31, #0.5
    ldr         s30, inv_128_const
    ldr         s29, inv_12_const
    fmov        s28, #1.0
    ldr         s27, pi2_const
    fmov        s26, #-1.0    
    ///     x4 = current instrument parameters pointer
    ///     x6 = instrument instructions pointer
    bl          debug_set_instrument_pointers
    ///     x10 = synth data pointer
    LOAD_ADDR   x10, synth_data
    ///     x5 = instrument data pointer
    mov         x3, #instrument_length
    mul         x3, x0, x3
    add         x5, x10, x3
    /// Set release
    strb        w2, [x5, #instrument_release]
    ///     x8 = VM stack data pointer
    LOAD_ADDR   x8, vm_stack_data
    bl          render_instrument
    ldr         s0, [x5, #instrument_output]
    str         s0, [x1], #4
    POP_LINK_REGISTER
    ret

///
/// Set instruction and parameter pointers to the correct instrument
debug_set_instrument_pointers:
    // Instrument #
    mov         x3, #0
    // Start values
    LOAD_ADDR   x6, instrument_instructions
    LOAD_ADDR   x4, instrument_parameters
debug_set_instrument_pointers_loop:
    cmp     x3, x0
    b.eq    debug_set_instrument_pointers_end
    ldrb    w13, [x6], #1
    // ENVELOPE?
    cmp     w13, #ENVELOPE_ID
    b.ne    1f
    add     x4, x4, #5
1:
    cmp     w13, #OSCILLATOR_ID
    b.ne    2f
    add     x4, x4, #8
2:
    cmp     w13, #STOREVAL_ID
    b.ne    3f
    add     x4, x4, #3
3:
    cmp     w13, #OUTPUT_ID
    b.ne    4f
    add     x4, x4, #1
4:
    cmp     w13, #INSTRUMENT_END
    b.ne    5f
    add     x3, x3, #1
5:
    b       debug_set_instrument_pointers_loop
debug_set_instrument_pointers_end:
    ret

#endif // DEBUG

///
/// Entry point for rendering the synth
///
/// Input:
///   x1 = pointer to output buffer
/// Important registers:
///     x0 = current note #
///     x2 = current sample #
///     x3 = current instrument #
///     x4 = current instrument parameters pointer
///     x5 = instrument data pointer
///     x6 = instrument instructions pointer
///     x7 = instrument instruction workspace pointer
///     x8 = VM stack data pointer
///     x9 = transformed instrument instruction parameters pointer
///     x10 = synth data pointer
///     
dope4ks_render:
    PUSH_LINK_REGISTER
    // Initialize pointers
    LOAD_ADDR   x0, dope4ks_current_note
    // Constants
    fmov        s31, #0.5
    ldr         s30, inv_128_const
    ldr         s29, inv_12_const
    fmov        s28, #1.0
    ldr         s27, pi2_const
    fmov        s26, #-1.0
    // x0 is current note #
    ldr         w0, [x0]
    // x2 is current sample #
    mov         x2, #0
render_sampleloop:
    LOAD_ADDR   x4, instrument_parameters
    LOAD_ADDR   x6, instrument_instructions
    LOAD_ADDR   x8, vm_stack_data
    LOAD_ADDR   x10, synth_data
    mov         x5, x10
    // x3 is current instrument #
    mov         x3, #0
render_instrumentloop:
    // First sample = new note
    cbnz        w2, no_new_note
    bl          new_instrument_note
no_new_note:
    // Render the current instrument
    bl          render_instrument
    // Advance to next instrument
    add         x5, x5, #instrument_length
    add         x3, x3, #1
    // Are we done?
    cmp         x3, #MAX_NUM_INSTRUMENTS
    b.lt        render_instrumentloop
    // Fake a note on the synth vm to force rendering
    str         w5, [x5, #instrument_note]
    bl          process_stack
    ldr         s0, [x5, #instrument_output]
    fmin        s0, s0, s28
    fmax        s0, s0, s26
    str         s0, [x1], #4
    // Advance to nextsample
    add         x2, x2, #1                              // x2 = current sample + 1
    // Are we done?
    ldr         w17, near_samples_per_note
    cmp         x2, x17
    b.lt        render_sampleloop
    POP_LINK_REGISTER
    ret

near_samples_per_note:  .word SAMPLES_PER_NOTE

///
/// Render the current instrument and add to output buffer
///
///     x0 = current note #
///     x2 = current sample #
///     x3 = current instrument #
///     x4 = current instrument parameters pointer
///     x5 = instrument data pointer
///     x6 = instrument instructions pointer
///     x7 = instrument instruction workspace pointer
///     x8 = VM stack data pointer
///     x9 = transformed instrument instruction parameters pointer
///     x10 = synth data pointer
render_instrument:
    PUSH_LINK_REGISTER
    // Process the VM instructions for this instrument
    bl          process_stack
    // Load envelope state for the first envelope instruction of the instrument
    ldr         w12, [x5, #(instrument_workspaces + ENVELOPE_WS_STATE)]
    // Kill the note if ENV_STATE_OFF
    cmp         w12, #ENV_STATE_OFF
    bne         render_instrument_done
    // Kill note if envelope is done
    str     wzr, [x5, #instrument_note]
render_instrument_done:
    POP_LINK_REGISTER
    ret


///
/// Setup instrument for the next note
///
///     x0 = current note #
///     x2 = current sample #
///     x3 = current instrument #
///     x4 = current instrument parameters pointer
///     x5 = instrument data pointer
///     x6 = instrument instructions pointer
///     x7 = instrument instruction workspace pointer
///     x8 = VM stack data pointer
///     x9 = transformed instrument instruction parameters pointer
///     x10 = synth data pointer
new_instrument_note:
    // x16 = current pattern index (note# / NOTES_PER_PATTERN)
    // x15 = note in current pattern (note# % NOTES_PER_PATTERN)
    mov         x17, #NOTES_PER_PATTERN
    udiv        x16, x0, x17
    msub        x15, x16, x17, x0
    // x14 = pattern index (instrument# * PATTERNS_PER_INSTRUMENT + pattern_index)
    mov         x14, #PATTERNS_PER_INSTRUMENT
    madd        x14, x3, x14, x16
    // x14 = pattern # (instrument_patterns[pattern_index])
    LOAD_ADDR   x13, instrument_patterns
    ldrb        w14, [x13, x14]
    // x17 = note offset into pattern list
    madd        x17, x14, x17, x15
    // x17 = note #
    LOAD_ADDR   x13, pattern_array
    ldrb        w17, [x13, x17]
    // If HLD, skip note setup
    cmp         w17, #HLD
    b.eq        .skip_note_setup
    // Ensure we have released the note by storing something != 0 there
    str         w5, [x5, #instrument_release]
    // If zero, skip note setup
    b.lt        .skip_note_setup
    // Zero MAX_COMMANDS * MAX_COMMAND_PARAMS + 3 dwords at [x5] without modifying x5
    mov         x14, x5
    mov         x16, #MAX_COMMANDS * MAX_COMMAND_PARAMS / 4
.zero_loop:
    stp         xzr, xzr, [x14], #16
    subs        x16, x16, #1
    bne         .zero_loop
    // final 12 bytes
    str         xzr, [x14], #8
    str         wzr, [x14], #4
    // Set note value
    str         w17, [x5, #instrument_note]
.skip_note_setup:
    ret

///
/// Process the VM instructions for the current instrument
///
///     x0 = current note #
///     x2 = current sample #
///     x3 = current instrument #
///     x4 = current instrument parameters pointer
///     x5 = instrument data pointer
///     x6 = instrument instructions pointer
///     x7 = instrument instruction workspace pointer
///     x8 = VM stack data pointer
///     x9 = transformed instrument instruction parameters pointer
///     x10 = synth data pointer
process_stack:
    PUSH_LINK_REGISTER
    // Load workspace pointer (instrument data + 8)
    add         x7, x5, #instrument_workspaces
stack_loop:
    // Get command byte and increment pointer
    ldrb        w15, [x6], #1
    // Are we done with this instrument?
    cbz         w15, .process_instrument_done
    // Not done? Call function from instrument instruction jump table
    LOAD_ADDR   x14, instrument_instructions_lookup
    ldr         x13, [x14, x15, lsl #3]
    blr         x13
    // Move to next command workspace slot
    add         x7, x7, #(MAX_COMMAND_PARAMS * 4)
    // Loop over all commands
    b           stack_loop            // jump back to loop
.process_instrument_done:
    POP_LINK_REGISTER
    ret

///
/// Envelope function
///
/// Input registers:
///     x0 = current note #
///     x2 = current sample #
///     x3 = current instrument #
///     x4 = current instrument parameters pointer
///     x5 = instrument data pointer
///     x6 = instrument instructions pointer
///     x7 = instrument instruction workspace pointer
///     x8 = VM stack data pointer
///     x9 = transformed instrument instruction parameters pointer
///     x10 = synth data pointer
/// Destroyed registers:
///     x17
envelope_function:
    PUSH_LINK_REGISTER
    // Transform parameters (5 values)
    mov         x17, #5
    bl          transform_values
    // Check if the envelope is active by checking if note = 0
    ldr         w16, [x5]
    cbnz        w16, envelope_is_active
    // Push 0.0 onto the VM stack
    str         wzr, [x8], #4
    b           envelope_done
envelope_is_active:
    // Are we in release mode?
    ldr         w17, [x5, #instrument_release]
    cbz         w17, envelope_process
    // Not in release mode
    mov         w17, #ENV_STATE_RELEASE
    str         w17, [x7, #ENVELOPE_WS_STATE]
envelope_process:
    // Load current level
	ldr         s0, [x7, #ENVELOPE_WS_LEVEL]
    // Check the envelope state
    ldr         w17, [x7, #ENVELOPE_WS_STATE]
	cmp		    w17, #ENV_STATE_SUSTAIN
    beq         envelope_gain
envelope_attack:
	cmp         w17, #ENV_STATE_ATTACK
    bne         envelope_decay
    bl          envelope_map
    fadd        s0, s0, s1
    // If value > 1, then end of attack
    fmov        s1, #1.0
    fcmp        s0, s1
    blt         envelope_decay
    fmov        s0, s1
    b           envelope_state_change
envelope_decay:
    cmp         w17, #ENV_STATE_DECAY
    bne         envelope_release
    bl          envelope_map
    fsub        s0, s0, s1
    // If value < sustain, then end of decay
    ldr         s1, [x9, #ENVELOPE_PARAM_SUSTAIN]
    fcmp        s0, s1
    bgt         envelope_release
    fmov        s0, s1
    b           envelope_state_change
envelope_release:
    cmp         w17, #ENV_STATE_RELEASE
    bne         envelope_leave
    bl          envelope_map
    fsub        s0, s0, s1
    // If value < 0, then end of release
    //fmov        s1, #0.0
    fcmp        s0, #0.0
    bgt         envelope_leave
    fmov        s0, wzr
envelope_state_change:
    add         w17, w17, #1
    str         w17, [x7, #ENVELOPE_WS_STATE]
envelope_leave:
	str         s0, [x7, #ENVELOPE_WS_LEVEL]
envelope_gain:
    // Multiply s0 with gain parameter and store result in [x8], then advance x8 by 4 bytes
    ldr     s1, [x9, #ENVELOPE_PARAM_GAIN]
    ldr     s2, [x7, #ENVELOPE_WS_GAIN_MOD]
    fadd    s1, s1, s2
    fmul    s0, s0, s1
    str     s0, [x8], #4
envelope_done:
    POP_LINK_REGISTER
    ret

///
///
///
/// Input registers:
///     x0 = current note #
///     x2 = current sample #
///     x3 = current instrument #
///     x4 = current instrument parameters pointer
///     x5 = instrument data pointer
///     x6 = instrument instructions pointer
///     x7 = instrument instruction workspace pointer
///     x8 = VM stack data pointer
///     x9 = transformed instrument instruction parameters pointer
///     x10 = synth data pointer
/// Output registers:
///     s1 = computed value
/// Destroyed registers:
///     x9, x11, x12, x13, x14, x15
///     s1, s2, s3, s4, s5
envelope_map:
    // Load correct ADSR parameter value into s1, multiply with 24 and negate
    ldr     s1, [x9, w17, uxtw #2]
    ldr     s2, twenty_four_const
    fmul    s1, s1, s2
    fneg    s1, s1

/// Compute pow(2, s1) = 2^s1
/// Input: s1 = x
/// Output: s1 = 2^x
/// Destroyed registers: x11, s2, s3, s4, s5, s6, s7, s8
pwr:
    // Method: 2^x = exp(x * ln(2))
    // First compute x * ln(2)
    ldr     s2, ln2_const           // s2 = ln(2) ≈ 0.693147
    fmul    s3, s1, s2              // s3 = x * ln(2)
    
    // Now compute exp(s3) using Taylor series approximation
    // exp(x) ≈ 1 + x + x²/2! + x³/3! + x⁴/4! + x⁵/5!
    
    // For better accuracy over larger range, we split x into integer and fractional parts
    // exp(x) = exp(int_part + frac_part) = exp(int_part) * exp(frac_part)
    // exp(int_part) = 2^(int_part / ln(2))
    
    // Split into integer and fractional parts
    fcvtzs  w12, s3                 // w12 = integer part of x*ln(2)
    scvtf   s4, w12                 // s4 = float(integer part)
    fsub    s5, s3, s4              // s5 = fractional part
    
    // Compute exp(fractional_part) using Taylor series
    // exp(x) ≈ 1 + x + x²/2 + x³/6 + x⁴/24 + x⁵/120
    fmov    s6, #1.0                // s6 = 1.0 (result accumulator)
    
    // First term: x
    fadd    s6, s6, s5              // s6 = 1 + x
    
    // Second term: x²/2
    fmul    s7, s5, s5              // s7 = x²
    fmov    s8, #2.0
    fdiv    s7, s7, s8              // s7 = x²/2
    fadd    s6, s6, s7              // s6 = 1 + x + x²/2
    
    // Third term: x³/6
    fmul    s7, s7, s5              // s7 = x³ (reusing previous x²)
    fmov    s8, #3.0
    fdiv    s7, s7, s8              // s7 = x³/6
    fadd    s6, s6, s7              // s6 = 1 + x + x²/2 + x³/6
    
    // Fourth term: x⁴/24
    fmul    s7, s7, s5              // s7 = x⁴
    fmov    s8, #4.0
    fdiv    s7, s7, s8              // s7 = x⁴/24
    fadd    s6, s6, s7              // s6 = 1 + x + x²/2 + x³/6 + x⁴/24
    
    // Now handle the integer part: 2^(int_part / ln(2))
    cmp     w12, #0
    beq     .pwr_no_int_part
    bmi     .pwr_negative_int_part
    
    // Positive integer part: multiply by 2^int_part
    mov     w11, #1
    lsl     w11, w11, w12           // w11 = 2^int_part
    scvtf   s7, w11                 // s7 = 2^int_part as float
    fmul    s6, s6, s7              // s6 = exp(frac) * 2^int
    b       .pwr_no_int_part
    
.pwr_negative_int_part:
    // Negative integer part: divide by 2^abs(int_part)
    neg     w12, w12                // w12 = abs(int_part)
    mov     w11, #1
    lsl     w11, w11, w12           // w11 = 2^abs(int_part)
    scvtf   s7, w11                 // s7 = 2^abs(int_part) as float
    fdiv    s6, s6, s7              // s6 = exp(frac) / 2^abs(int)
    
.pwr_no_int_part:
    // Result is in s6, move to s1
    fmov    s1, s6
    
    ret

///
/// Oscillator function
///
/// Input registers:
///     x0 = current note #
///     x2 = current sample #
///     x3 = current instrument #
///     x4 = current instrument parameters pointer
///     x5 = instrument data pointer
///     x6 = instrument instructions pointer
///     x7 = instrument instruction workspace pointer
///     x8 = VM stack data pointer
///     x9 = transformed instrument instruction parameters pointer
///     x10 = synth data pointer
_oscillator_function:
    PUSH_LINK_REGISTER
    // Transform parameters
    mov         x17, #7
    bl          transform_values
    // Load oscillator type into w17
    ldrb        w17, [x4], #1
    // Perhaps check for end of note?
    // Stereo?
    // s0 = transpose value [-128..128]
    ldr         s0, [x9, #OSCILLATOR_PARAM_TRANSPOSE]
    fsub        s0, s0, s31
    ldr         s1, [x7, #OSCILLATOR_WS_TRANSPOSE_MOD]
    fadd        s0, s0, s1
    fdiv        s0, s0, s30
    // s0 = transpose value [-128..128] + detune value [-1..1]
    ldr         s1, [x9, #OSCILLATOR_PARAM_DETUNE]
    fsub        s1, s1, s31
    fadd        s0, s1, s1
    ldr         s2, [x7, #OSCILLATOR_WS_DETUNE_MOD]
    fadd        s0, s0, s2
    tst         w17, #OSCILLATOR_LFO
    b.ne        .no_note
    // s0 = note + transpose + detune (for LFO, only transpose + detune)
    ldr         w16, [x5, #instrument_note]
    scvtf       s1, w16
    fadd        s0, s0, s1
.no_note:
    // Convert to frequency in octaves
    fmul        s1, s0, s29
    bl          pwr
    tst         w17, #OSCILLATOR_LFO
    b.eq        .normalize_note
    ldr         s2, LFO_frequency_base
    b          .normalized
.normalize_note:
    ldr         s2, frequency_base
.normalized:
    fmul        s0, s1, s2
    // Add the phase and frequency modulation
    ldr         s1, [x7, #OSCILLATOR_WS_PHASE]
    fadd        s0, s0, s1
    ldr         s1, [x7, #OSCILLATOR_WS_FREQUENCY_MOD]
    fadd        s0, s0, s1
    // Normalize phase to [0, 1) range: extract fractional part
    fadd        s0, s0, s28
    frintm      s1, s0
    fsub        s0, s0, s1
    // Store current phase
    str         s0, [x7, #OSCILLATOR_WS_PHASE]
    // Add phase modulation
    ldr         s1, [x7, #OSCILLATOR_WS_PHASE_MOD]
    fadd        s0, s0, s1
    // Add phase offset
    ldr         s1, [x9, #OSCILLATOR_PARAM_PHASE]
    fadd        s0, s0, s1
    // Renormalize phase
    fadd        s0, s0, s28
    frintm      s1, s0
    fsub        s0, s0, s1
    // Add color
    ldr         s1, [x9, #OSCILLATOR_PARAM_COLOR]
    ldr         s2, [x7, #OSCILLATOR_WS_COLOR_MOD]
    fadd        s1, s1, s2
    // So, s0 is now phase and s1 is color. Let's create the waveform
    tst         w17, #OSCILLATOR_SINE
    b.eq        .not_sine
    bl          cosine_waveform
.not_sine:
    tst         w17, #OSCILLATOR_NOISE
    b.eq        .not_noise
    // Simple white noise
    // seed = seed * 16007
    LOAD_ADDR   x11, rand_seed
    ldr         w13, [x11]
    mov         w12, #16007
    mul         w13, w13, w12
    str         w13, [x11]
    // // s0 = (float)seed / (float)c_RandDiv
    scvtf       s0, w13
    LOAD_ADDR   x12, rand_div
    ldr         s1, [x12]
    fdiv        s0, s0, s1
    // fmov            s0, #0.75
.not_noise:
    // TODO Implement more waveforms
    ldr         s1, [x9, #OSCILLATOR_PARAM_GAIN]
    ldr         s2, [x7, #OSCILLATOR_WS_GAIN_MOD]
    fadd        s1, s1, s2
    fmul        s0, s0, s1
    str         s0, [x8], #4
    POP_LINK_REGISTER
    ret

// Input: s0 = phase, s1 = color
// Output: s1 ≈ cos(2*pi*phase/color)
// Uses: s2, s3, s4, s5, s6,
cosine_waveform:
    // If color > phase, output 0.0
    fcmp    s0, s1
    b.ge    .do_cosine
    fmov    s0, #0.0
    ret
.do_cosine:
    // Calculate s1 = 2pi * phase / color
    fdiv    s1, s0, s1
    fmul    s1, s1, s27
    // // Reduce x to [0, 2*pi)
    // LOAD_ADDR x3, pi2_const
    // ldr s2, [x3]                // s2 = 2*pi
    // fdiv s3, s1, s2             // s3 = x / (2*pi)
    // frintm s3, s3               // s3 = floor(x / 2*pi)
    // fmul s3, s3, s2             // s3 = floor(x/2*pi) * 2*pi
    // fsub s1, s1, s3             // s1 = x - floor(x/2*pi)*2*pi, now s1 in [0, 2*pi)


    // If x > pi, cos(x) = -cos(x - pi)
    LOAD_ADDR x3, pi_const
    ldr s4, [x3]                // s4 = pi
    fcmp s1, s4
    b.le 1f
    fsub s1, s1, s4             // s1 = x - pi
    mov w11, #1                 // flip sign
    b 2f
1:
    mov w11, #0                 // don't flip sign
2:
    // Now s1 in [0, pi]
    // If s1 > pi/2, use cos(x) = -cos(pi - x)
    fmov s5, #0.5
    fmul s6, s4, s5             // s6 = pi/2
    fcmp s1, s6
    b.le 3f
    fsub s1, s4, s1             // s1 = pi - s1
    eor w11, w11, #1            // flip sign
3:
    // Now s1 in [0, pi/2], w11 = 1 if sign should be flipped
    // Compute x^2 and x^4
    fmul s2, s1, s1             // s2 = x^2
    fmul s3, s2, s2             // s3 = x^4

    // Load coefficients
    fmov s4, #0.5
    LOAD_ADDR x7, cos_c4
    ldr s5, [x7]

    // Compute polynomial: 1 - 0.5*x^2 + 0.0416666*x^4
    fmov s6, #1.0
    fmul s7, s2, s4             // s7 = 0.5*x^2
    fsub s6, s6, s7             // s6 = 1 - 0.5*x^2
    fmul s7, s3, s5             // s7 = 0.0416666*x^4
    fadd s1, s6, s7             // s1 = 1 - 0.5*x^2 + 0.0416666*x^4

    // Flip sign if needed
    cbz w11, 4f
    fneg s1, s1
4:
    ret


///
/// Store value function
///
/// Input registers:
///     x0 = current note #
///     x2 = current sample #
///     x3 = current instrument #
///     x4 = current instrument parameters pointer
///     x5 = instrument data pointer
///     x6 = instrument instructions pointer
///     x7 = instrument instruction workspace pointer
///     x8 = VM stack data pointer
///     x9 = transformed instrument instruction parameters pointer
///     x10 = synth data pointer
/// Destroyed registers:
storeval_function:
    PUSH_LINK_REGISTER
    // Transform parameters (1 value)
    mov         x17, #1
    bl          transform_values
    ldr         s1, [x9, #STOREVAL_PARAM_AMOUNT]
    // Remap s1 from [0,1] to [-1,1]: s1 = (s1 - 0.5) / 0.5
    fmov        s2, #0.5
    fsub        s1, s1, s2
    fdiv        s1, s1, s2
    // // Multiply with value at top of VM stack
    ldr         s2, [x8, #-4]
    fmul        s1, s1, s2
    // Load 16-bit value from [x4], advance x4 by 2
    ldrh        w17, [x4], #2
    and         w16, w17, #STOREVAL_MASK
    // Pop the value from the VM stack if needed
    tst         w17, #STOREVAL_POP
    b.eq        .no_pop
    sub         x8, x8, #4
.no_pop:
    // Add current value if needed
    tst         w17, #STOREVAL_ADD
    b.eq        .no_add
    // Load and add current value
    ldr         s2, [x5, w16, uxtw #0]
    fadd        s1, s1, s2
.no_add:
    // Store result
    str         s1, [x5, w16, uxtw #0]
    POP_LINK_REGISTER
    ret

///
/// Operation function
///
/// Input registers:
///     x0 = current note #
///     x2 = current sample #
///     x3 = current instrument #
///     x4 = current instrument parameters pointer
///     x5 = instrument data pointer
///     x6 = instrument instructions pointer
///     x7 = instrument instruction workspace pointer
///     x8 = VM stack data pointer
///     x9 = transformed instrument instruction parameters pointer
///     x10 = synth data pointer
/// Destroyed registers:
operation_function:
    ldr         x17, [x4], #1
    cmp         x17, #OPERATOR_MULP
    b.eq        .not_mulp
    // Multiplication + pop
    ldr         s1, [x8, #-8]
    ldr         s2, [x8, #-4]
    fmul        s1, s1, s2
    str         s1, [x8, #-8]
    sub         x8, x8, #4
.not_mulp:
    ret

///
/// Output function
///
/// Input registers:
///     x0 = current note #
///     x2 = current sample #
///     x3 = current instrument #
///     x4 = current instrument parameters pointer
///     x5 = instrument data pointer
///     x6 = instrument instructions pointer
///     x7 = instrument instruction workspace pointer
///     x8 = VM stack data pointer
///     x9 = transformed instrument instruction parameters pointer
///     x10 = synth data pointer
/// Destroyed registers:
output_function:
    PUSH_LINK_REGISTER
    // Transform parameters (gain)
    mov         x17, #1
    bl          transform_values
    ldr         s1, [x9, #OUTPUT_PARAM_GAIN]
    ldr         s2, [x7, #OUTPUT_WS_GAIN_MOD]
    fadd        s1, s1, s2
    sub         x8, x8, #4
    ldr         s0, [x8]
    fmul        s0, s0, s1
    str         s0, [x5, #instrument_output]
    POP_LINK_REGISTER
    ret

///
/// Accumulate function
///
/// Input registers:
///     x0 = current note #
///     x2 = current sample #
///     x3 = current instrument #
///     x4 = current instrument parameters pointer
///     x5 = instrument data pointer
///     x6 = instrument instructions pointer
///     x7 = instrument instruction workspace pointer
///     x8 = VM stack data pointer
///     x9 = transformed instrument instruction parameters pointer
///     x10 = synth data pointer
/// Destroyed registers:
accumulate_function:
    PUSH_LINK_REGISTER
    mov         x13, x10
    mov         x11, #MAX_NUM_INSTRUMENTS
    fmov        s0, wzr
.accumulate_loop:
    // Load instrument output
    ldr         s1, [x13, #instrument_output]
    fadd         s0, s0, s1
    add         x13, x13, #instrument_length
    subs        x11, x11, #1
    b.ne        .accumulate_loop
    str         s0, [x8], #4
    POP_LINK_REGISTER
    ret

///
/// Convert [x17] 8-bit values in [x4] to floats in [_transformed_parameters]
///
/// Input registers:
///     x0 = current note #
///     x2 = current sample #
///     x3 = current instrument #
///     x4 = current instrument parameters pointer
///     x5 = instrument data pointer
///     x6 = instrument instructions pointer
///     x7 = instrument instruction workspace pointer
///     x8 = VM stack data pointer
///     x9 = transformed instrument instruction parameters pointer
///     x10 = synth data pointer
/// Output registers:
///     x4 = point to next 8-bit value
///     x9 = point to transformed parameters
/// Destroyed registers:
///     x9, w14, x17
///     s0, s3
transform_values:
    // x9 = pointer to transformed parameters
    LOAD_ADDR   x9, transformed_parameters
    mov         x11, x9
    // Load 1/128 constant from memory into s3
    ldr         s3, inv_128_const
1:
    // Set s0 to next value and advance pointer
    ldrb        w14, [x4], #1
    scvtf       s0, w14
    // Divide by 128
    fmul        s0, s0, s3
    // Store result and advance pointer
    str         s0, [x11], #4
    // Are we done?
    subs        w17, w17, #1
    bne         1b
    ret

inv_128_const:      .float  0.0078125       // 1/128
inv_12_const:       .float  0.0833333       // 1/12
pi2_const:          .float  6.283185307    // 2*pi
pi_const:           .float  3.1415927
frequency_base:     .float  0.000092696138  // 220.0/(2^(69/12)) / 44100.0
LFO_frequency_base: .float  0.000041106       // 90.0/(2^(69/12)) / 44100.0
cos_c4:             .float  0.04166667


twenty_four_const:  .float  24.0
three_const:        .float  3.0
ln2_const:          .float  0.693147   // ln(2)
inv_ln2_const:      .float  1.442695   // 1/ln(2)
frac_const1:        .float  0.6931     // coefficient for 2^x approximation
frac_const2:        .float  0.2402     // coefficient for 2^x approximation


.data
///
/// Lookup table for instrument instructions
/// 
.align 3
instrument_instructions_lookup:
                    .quad 0
                    .quad envelope_function
                    .quad oscillator_function
                    .quad storeval_function
                    .quad operation_function
                    .quad 0 // filter_function (not implemented)
                    .quad 0 // panning_function (not implemented)
                    .quad output_function
                    .quad accumulate_function

rand_seed:          .word 1
rand_div:           .float 2147483648.0

.bss

/// Synth data
synth_data:                 .space   synth_data_size
transformed_parameters:     .space   MAX_COMMAND_PARAMS * 4

/// The current note being rendered
dope4ks_current_note:       .space   4

/// VM Stack data (for all instruments)
vm_stack_data:             .space   16 * 4

/// Legacy variables for softsynth_wrapper.asm
_get_noise_waveform:
_get_sawtooth_waveform:
_get_square_waveform:
_get_sine_waveform:
_instrument_definition:
_instrument_hold:
_instrument_ticks:
_pattern_list:
_pattern_index:
_softsynth_init:
_softsynth_play:
_ticks:
_track_index:
_track_list:
f_instrument_delta:
f_instrument_offset:
f_instrument_modo:
f_instrument_value:
get_instrument_value:
note_table:
sampling_freq_const: