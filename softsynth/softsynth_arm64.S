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

#include "common_arm64.s"

;; For AED
.global	_softsynth_init
#define softsynth_init _softsynth_init
.global	_softsynth_play
#define softsynth_play _softsynth_play
.global	_instrument_definition
#define instrument_definition _instrument_definition
.global	_instrument_hold
#define instrument_hold _instrument_hold
.global	_instrument_ticks
#define instrument_ticks _instrument_ticks
.global	_pattern_list
#define pattern_list _pattern_list
.global	_pattern_index
#define pattern_index _pattern_index
.global	_track_list
#define track_list _track_list
.global	_track_index
#define track_index _track_index
.global	_ticks
#define ticks _ticks
.global	_sample_data
#define sample_data _sample_data
.global	_get_sine_waveform
#define get_sine_waveform _get_sine_waveform
.global	_get_noise_waveform
#define get_noise_waveform _get_noise_waveform
.global	_get_square_waveform
#define get_square_waveform _get_square_waveform
.global	_get_sawtooth_waveform
#define get_sawtooth_waveform _get_sawtooth_waveform

;; For softsynth_wrapper.asm
.global	get_instrument_value
.global	note_table
.global	f_instrument_delta
.global	f_instrument_offset
.global	f_instrument_modo
.global sampling_freq_const

#define c1x 0
#define C1x 1
#define d1x 2
#define D1x 3
#define e1x 4
#define f1x 5
#define F1x 6
#define g1x 7
#define G1x 8
#define a1x 9
#define A1x 10
#define b1x 11
#define c2x 12
#define C2x 13
#define d2x 14
#define D2x 15
#define e2x 16
#define f2x 17
#define F2x 18
#define g2x 19
#define G2x 20
#define a2x 21
#define A2x 22
#define b2x 23
#define c3x 24
#define C3x 25
#define d3x 26
#define D3x 27
#define e3x 28
#define f3x 29
#define F3x 30
#define g3x 31
#define G3x 32
#define a3x 33
#define A3x 34
#define b3x 35
#define c4x 36
#define C4x 37
#define d4x 38
#define D4x 39
#define e4x 40
#define f4x 41
#define F4x 42
#define g4x 43
#define G4x 44
#define a4x 45
#define A4x 46
#define b4x 47
#define c5x 48
#define C5x 49
#define d5x 50
#define D5x 51
#define e5x 52
#define f5x 53
#define F5x 54
#define g5x 55
#define G5x 56
#define a5x 57
#define A5x 58
#define b5x 59
#define c6x 60
#define C6x 61
#define d6x 62
#define D6x 63
#define e6x 64
#define f6x 65
#define F6x 66
#define g6x 67
#define G6x 68
#define a6x 69
#define A6x 70
#define b6x 71

#define MAX_NUM_INSTRUMENTS 10
#define NUM_INSTRUMENTS MAX_NUM_INSTRUMENTS
#define BEATS_PER_MINUTE 125
#define NOTES_PER_BEAT 4
#define ROW_TICKS (60 * 44100 / (BEATS_PER_MINUTE * NOTES_PER_BEAT))

#define ECHO_LENGTH (ROW_TICKS * 3)
#define ECHO_AMPLITUDE 2.0
#define RANDOM_SEED 0x038fa39bc
#define SINE_AMP 32767.0

#define END_PATTERN -2

#define END_TRACK -2
#define LOOP_TRACK -3
#define STOP -4
#define ECHO_ON -5
#define ECHO_OFF -6
#define HOLD_5 -7
#define HOLD_4 -8
#define HOLD_3 -9
#define HOLD_2 -10
#define HOLD_1 -11
#define HOLD_ADD -HOLD_1 + 1

.equ inst_waveform,    0
.equ inst_attack,      8
.equ inst_decay,      12
.equ inst_sustain,    16
.equ inst_release,    20
.equ inst_modulation, 24
.equ inst_sweep,      28
.equ inst_size,       32

.text

#ifdef DEBUG
.macro PRINT_DEBUG
    PUSH_LINK_REGISTER
    bl      write_hello
    POP_LINK_REGISTER
.endmacro
write_hello:
    /* syscall write(int fd, const void *buf, size_t count) */
    mov     x0, #1      /* fd := STDOUT_FILENO */
    LOAD_ADDR x1, msg
    ldr     x2, =len    /* count := len (length of msg) */
    movz    x16, #0x200, lsl #16   /* write syscall number for macOS (upper 16 bits) */
    movk    x16, #0x4              /* write syscall number for macOS (lower 16 bits) */
    svc     #0x80             /* invoke syscall */
    ret
#else
.macro PRINT_DEBUG
.endmacro
#endif

;
; The init routine of the softsynth
;

softsynth_init:
    ; The number of floats to copy (5 octaves, 12 notes each)
    mov     x2, #5*12
    fmov    s3, #0.5
    LOAD_ADDR x0, note_table_rework_dst
    LOAD_ADDR x1, note_table_rework_src
.loop:
    ldr     s1, [x1], #-4        // load float from [src], decrease src
    fmul    s1, s1, s3          // s1 = s1 * 0.5
    str     s1, [x0], #-4        // store float to [dst], decrease dst
    subs    x2, x2, #1          // n--
    b.ne    .loop
.done:
    ret

// x1= stream, x2=len
softsynth_play:
    PUSH_LINK_REGISTER
do_sample:
    LOAD_ADDR x16, ticks
    ldr     w0, [x16]
    mov     w3, #ROW_TICKS
    udiv    w4, w0, w3
    msub    w5, w4, w3, w0      // x5 = ticks % ROW_TICKS
    cbz     w5, new_row         // If 0, get new row (remainder is zero)
    b       sum_instruments     // No new row

new_row:
    LOAD_ADDR x10, track_index
    LOAD_ADDR x11, pattern_index
    LOAD_ADDR x12, track_list
    LOAD_ADDR x13, pattern_list
    mov     x5, #0              //	xor	ecx, ecx            ; Clear ecx
row_loop:
    ldr w15, [x10, x5, lsl #2]           // mov	eax,[track_index+ecx]		; Get track index for instr
instrument_not_done:
    ldr w9, [x11, x5, lsl #2]
    add w9, w9, #1
    str w9, [x11, x5, lsl #2]           // inc	dword [pattern_index+ecx]	; Do next pattern
    cmp     w15, #-1                     // cmp	eax,-1				; Check if track index is -1
    beq     new_pos                     // je	new_pos				; If so, get new pos
    bl      get_command                 //	call	get_command			; Get command
    cmp     w7, #END_PATTERN            //	cmp	al,END_PATTERN			; Check if command is END_PATT
    b.ne    no_new_pos                  //	jne	no_new_pos			; No new pos
new_pos:
    ldr w15, [x10, x5, lsl #2]
    add w15, w15, #1
    str w15, [x10, x5, lsl #2]          // inc	dword [track_index+ecx]		; Do next track
                                        //	mov     eax,[track_index+ecx]		; Get track index
    ldr x9, [x12, x5, lsl #3]           //	mov     ebx,[track_list+ecx]		; Get track pointer
    add x9, x9, w15, sxtw               //	add     ebx,eax				; Add index to pointer
    ldrsb w9, [x9]                      //	mov     al,[ebx]			; Get pointed value
                                        //	xor	edx,edx				; Clear edx
    cmp     w9, #LOOP_TRACK             //	cmp	al,LOOP_TRACK			; Check if this is a LOOP_TRACK
    b.ne    no_loop                     //	jne	no_loop				; If not, jump
    str wzr, [x10, x5, lsl #2]          //	mov	[track_index+ecx],edx		; Clear track index
no_loop:
    str wzr, [x11, x5, lsl #2]          //	mov	[pattern_index+ecx],edx		; Clear pattern index
no_new_pos:
    bl      get_command                 //	call    get_command			; Get command
    cbz     w7, instrument_done         //	or      al,al				; Check if zero
                                        //	jz      instrument_done			; If so, jump
    cmp     w7, #STOP                   //	cmp     al,STOP				; Check if STOP command
    b.ne    no_stop                     //	jne     no_stop				; If not, jump
    b.eq    instrument_done             //	je      instrument_done			; Instrument done
no_stop:
    cmp     w7, #ECHO_ON                //	cmp     al,ECHO_ON			; Check if ECHO_ON command
    b.ne    no_echo_on                  //	jne     no_echo_on			; If not, jump
    LOAD_ADDR x6, instrument_echo
    strb    w7, [x6, x5]                //    mov     [ecx+instrument_echo],al	; Set echo on
    b      instrument_not_done       //	je      instrument_not_done		; Instrument done
no_echo_on:
    cmp     w7, #ECHO_OFF               //    cmp     al,ECHO_OFF           ; Check if ECHO_OFF command
    b.ne    no_echo_off                 //    jne     no_echo_off           ; If not, jump
    LOAD_ADDR x6, instrument_echo
    strb    wzr, [x6, x5]               //    mov     [ecx+instrument_echo],0	; Set echo off
    b      instrument_not_done  //	je      instrument_not_done		; Instrument done
.global no_echo_off
no_echo_off:
    // Start instrument
    LOAD_ADDR x6, note_table
    ldr s0, [x6, w7, uxtw #2]            //    fld	dword [note_table+eax]		; Get value from note_table
    ldr s1, pi2_const                   //	fldpi					; Load Pi
                                        //	fadd	st0,st0				; 2 * Pi -> st0
    fmul s0, s0, s1                     //	fmulp	st1,st0				; 2 * Pi * Freq -> st0
    ldr s1, sampling_freq_const
    fdiv s0, s0, s1                     //	fdiv	dword [f_sampling_freq]		; 2 * Pi * Freq / 44100 -> st0
    LOAD_ADDR x6, f_instrument_delta
    str s0, [x6, x5, lsl #2]            //	fstp	dword [f_instrument_delta+ecx]	; Store delta
    LOAD_ADDR x6, instrument_ticks      //	fldz					; Load 0.0 in st0
    str wzr, [x6, x5, lsl #2]           //	fist	dword [instrument_ticks+ecx]	; Clear instrument ticks
    LOAD_ADDR x6, f_instrument_offset
    str wzr, [x6, x5, lsl #2]           //	fst	dword [f_instrument_offset+ecx]	; Clear instrument offset
    LOAD_ADDR x6, f_instrument_modo
    str wzr, [x6, x5, lsl #2]           //	fst	dword [f_instrument_modo+ecx]	; Clear instrument modulation
    LOAD_ADDR x6, instrument_hold
    str wzr, [x6, x5, lsl #2]           //	fist	dword [instrument_hold+ecx]	; Clear instrument hold time

    cmp w14, #HOLD_5                    //	cmp	bl,HOLD_5			; Check if HOLD_x command
    b.gt no_hold                        //	jg	no_hold				; If not, jump
    add w14, w14, #HOLD_ADD             //	add	bl,HOLD_ADD			; Add HOLD_ADD to bl
                                        //	xor	bh,bh				; Clear bh
    mov w9, #ROW_TICKS                  //	mov	ax, ROW_TICKS
    mul w14, w14, w9                     //	mul	bx				; Mul ROW_TICKS with ax
    scvtf s1, w14
    str s1, [x6, x5, lsl #2]            //	mov	[ecx+instrument_hold],eax	; Set instrument_hold
    ldr w9, [x11, x5, lsl #2]
    add w9, w9, #1
    str w9, [x11, x5, lsl #2]            // inc	dword [pattern_index+ecx]	; Skip next pattern note
no_hold:
	
instrument_done:
    add     x5, x5, #1            //	add	ecx,4				; Add 4 (next instrument)
    cmp     x5, #NUM_INSTRUMENTS //	cmp	ecx,NUM_INSTRUMENTS * 4		; Check if done
    b.lt    row_loop              //	jl	row_loop			; loop back

	;; The summing loop
sum_instruments:
    fmov s0, #0.0                   //	fldz					; Clear sum
    mov x5, #0                      //	xor	ecx,ecx				; Clear ecx
    //	mov     esi,echo_data			; Set esi to echo

sum_loop:
	;; First, do echo
//	mov     eax,[ticks]			; Get ticks
//	inc     eax				; Increase
//	call    get_echo_pointer		; Call echo
//	fld	dword [edx]			; Load echo value
//	fld	st0				; Load once again
//	fld	dword [f_two]			; Load two
//	fdivp	st1, st0			; Divide by two
	
//	mov     eax,[ticks]			; Get ticks again
//	call    get_echo_pointer		; Call echo
//	fstp	dword [edx]			; Store half echo value
//	faddp	st1, st0			; Add echo value to sum
//	push	edx				; Push echo pointer

    bl get_instrument_value             //	call	get_instrument_value
    fadd s0, s0, s1                     //	fadd	st1,st0				; Add value to sum
//	pop	ebx				; Restore echo pointer
//	test    byte [instrument_echo+ecx],0ffh	; Check if echo should be added
//	jz      no_echo				; If not, jump
//	fld	dword [f_echo_amp]		; Load echo amplitude
//	fdivp	st1, st0			; Divide sample with amp
//	fadd	dword [ebx]			; Store as new echo
//	fstp	dword [ebx]
//	jmp	skipchan        
no_echo:
                                    //	fcomp	st0				; Pop stack
	
skipchan:
//	add     esi,65536*4			; Point esi to next instrument
    add x5, x5, #1                  //	add     ecx,4				; Add four to ecx
    cmp x5, #NUM_INSTRUMENTS        //	cmp     ecx,NUM_INSTRUMENTS * 4		; Check if all instruments done
                                    //	je      instruments_summed		; If so, jump
    b.ne sum_loop                   //	jmp     sum_loop			; Loop back

instruments_summed:
    fmov s1, #3.0                  // Load 3.0
    fdiv s0, s0, s1               // Divide sum by 3.0
    frintz s0, s0                 // Round to integer (towards zero)
    fcvtzs w15, s0                 // Convert float to signed int (32-bit)
    mov w17, #-32767               // Lower clamp
    cmp w15, w17
    b.ge clip2
    mov w15, #-32767
clip2:
    mov w17, #32767                // Upper clamp
    cmp w15, w17
    b.le done
    mov w15, #32767
done:
    mov w3, #1
    // It seems the Xt and Xn versions are swapped on Apple Silicon for ldadd
    ldadd w3, wzr, [x16]            //	inc     dword [ticks]			; Increase ticks
    mov x3, #2
    strh w15, [x1]
    add x1, x1, x3                 // Add two to destination pointer
    subs x2, x2, #2                // Sub two from length
    b.ne do_sample                 // If not zero, loop
all_done:   
    POP_LINK_REGISTER
    ret

get_command:
    ldr w7, [x10, x5, lsl #2]               //	mov     eax,[track_index+ecx]		; Get track index
    ldr x4, [x12, x5, lsl #3]               //	mov     ebx,[track_list+ecx]		; Get track pointer
                                            //	add     ebx,eax				; Add index to pointer
    ldrb w7, [x4, w7, uxtw]                 //	mov     al,[ebx]			; Get pointed value
                                            //	shl     eax,2				; Mul with 4 (8 on 64-bit)
    ldr x4, [x13, w7, uxtw #3]              //	mov     ebx,[pattern_list+eax]		; Get pattern pointer
    ldr w9, [x11, x5, lsl #2] 
                                            //	add     ebx,[pattern_index+ecx]		; Add pattern index
    ldrsb w7, [x4, w9, sxtw]                //	mov     al,[ebx]			; Get pointer value
    add w9, w9, #1
    ldrsb w14, [x4, w9, sxtw]               //	mov     bl,[ebx+1]			; Get possible hold value
    ret
    // Return: w7 = pointer value, w14 = possible hold value

get_echo_pointer:
//	mov     ebx,ECHO_LENGTH			; Get echo length
//	cdq					; Convert to quad word
//	div     ebx				; Divide eax with echo length
//	shl     edx,2				; Mul remainder with 4
//	add     edx,esi				; Add esi to edx
//	ret					; Return

// TODO Make inline as there is only one caller
rnd:
    LOAD_ADDR x6, random_number   // x6 = &random_number
    ldr w0, [x6]                  // w0 = random_number (eax)
    movz w3, #(0x39bc)              // lower 16 bits
    movk w3, #(0x8fa3), lsl #16     // upper 16 bits
    add w0, w0, w3                // w0 += RANDOM_SEED
    eor w0, w0, w3                // w0 ^= RANDOM_SEED
    ror w0, w0, #1                // w0 = ror(w0, 1)
    str w0, [x6]                  // random_number = w0
    ret

	;; Output:	eax <- Value
// TODO Make inline as there is only one caller
get_instrument_value:
    PUSH_LINK_REGISTER
                                        //	push	ebp
                                        //	mov	eax,ecx				; Move ecx to eax
                                        //	shr	eax,2				; eax = instr
                                        //	mov	edx,inst.size			; Move inst.size to edx
                                        //	mul	edx				; eax = instr * inst.size
    mov x3, #inst_size
    mul x3, x3, x5                     // x3 is inst_size * instr_num
    LOAD_ADDR x4, instrument_definition
                                        // x3 = &instrument_definition[instr]
    ldr x3, [x4, x3]
    LOAD_ADDR x7, f_instrument_offset
    LOAD_ADDR x6, f_instrument_delta
    ldr s1, [x7, x5, lsl #2]                    // s1 = Load offset
    ldr s2, [x6, x5, lsl #2]                    // s2 = Load delta
    fadd s2, s2, s1                             // s2 = offset + delta
    str s2, [x7, x5, lsl #2]                    // Store new offset
    blr x3                                      // Call waveform function
    // Two two rows below for debugging ADSR
    //LOAD_ADDR x3, f_sine_amp
    //ldr s1, [x3]
    bl get_adsr_enveloping                      // Call ADSR function  
    fmul s1, s1, s2

//	mov	ebp,eax				; Move eax to ebp
//	add	ebp,instrument_definition	; Add instrument def. to ebp
//	fld	dword [f_instrument_offset+ecx]	; Load offset
	;; Get basic waveform
// 	call	dword [ebp+inst.waveform]; Get waveform value
	;; Add ADSR volume enveloping
//	call	get_adrs_enveloping		; Get volume value
//	fmulp	st1,st0				; Multiply waveform with volume
	;; Add modulation
//	fld	dword [f_instrument_modo+ecx]	; Load modulation offset
//	call	get_sine_waveform		; Get sine waveform
//	mov	dword [temp_dword],16		; Put 16 in temp dword
//	fild	dword [temp_dword]		; Load 16
//	fdivp	st1,st0				; Divide modulation with 16 and pop
//	fmulp	st1,st0				; Multiply waveform with modulation
//	mov	dword [temp_dword],256 * 16	; Put 256 * 16 in temp dword
//	fild	dword [temp_dword]		; Load 256 * 16
//	fdivp	st1,st0				; Divide modulation with 16 and pop
	;; Increase values
                                    //	fld	dword [f_instrument_offset+ecx]	; Load offset
                                    //	fadd	dword [f_instrument_delta+ecx]	; Add delta to offset
                                    //	fstp	dword [f_instrument_offset+ecx]	; Store result in offset
//	fld	dword [f_instrument_delta+ecx]	; Load delta
//	fadd	dword [ebp+inst.sweep]		; Add sweep to delta
//	fstp	dword [f_instrument_delta+ecx]	; Store result in delta
//	fld	dword [f_instrument_modo+ecx]	; Load modulation offset
//	fadd	dword [ebp+inst.modulation]	; Add delta to modulation offset
//	fstp	dword [f_instrument_modo+ecx]	; Store modulation offset
//	pop	ebp
    POP_LINK_REGISTER
    ret

	;; Input:	s1 <- Position
	;; Output:	s1 <- Value
_get_sine_waveform:
    PUSH_LINK_REGISTER
    bl cosf                          //	fcos					; sin(st0) -> st0
    LOAD_ADDR x3, f_sine_amp
    ldr s2, [x3]
    fmul s1, s1, s2                 //	fmul	dword [f_sine_amp]		; st0 * amp -> st0
    POP_LINK_REGISTER
	ret

	;; Output:	s1 <- Value
_get_noise_waveform:
    PUSH_LINK_REGISTER
    bl rnd                 //	call    rnd				; Get a random value in eax
    and w0, w0, #0xffff     //	and     eax,0ffffh			; Set range to [0..65536]
    sub w0, w0, #32768      //	sub     eax,32768			; Set range to [-32767..32768]
    scvtf s1, w0              //	mov	[temp_dword], eax		; Move to temp dword
                                //	fild	dword [temp_dword]		; Load temp dword
    POP_LINK_REGISTER
    ret

	;; Input:	s1 <- Position
	;; Output:	s1 <- Value
_get_square_waveform:
    PUSH_LINK_REGISTER
    bl cosf                     // cos(s1) -> s1
    fcmp s1, #0.0
    LOAD_ADDR x3, f_sine_amp
    ldr s1, [x3]
    b.ge 1f
    fneg s1, s1
1:
    POP_LINK_REGISTER
	ret

	;; Input:	s1 <- Position
	;; Output:	s1 <- Value
_get_sawtooth_waveform:
    // Calculate s1 mod (2*pi), result in s1
    LOAD_ADDR x3, pi2_const
    ldr s2, [x3]            // s2 = 2*pi
    fdiv s3, s1, s2         // s3 = s1 / (2*pi)
    frintm s3, s3           // s3 = floor(s1 / (2*pi))
    fmul s3, s3, s2         // s3 = floor(s1/(2*pi)) * 2*pi
    fsub s1, s1, s3         // s1 = s1 - floor(s1/(2*pi))*2*pi
    // Now s1 in [0, 2*pi)
    // Scale to [-32767..32767]
    fdiv s1, s1, s2         // s1 = s1 / (2*pi), now in [0..1)
    LOAD_ADDR x3, f_sine_amp
    ldr s2, [x3]            // s2 = 32767
    fmul s1, s1, s2         // s1 = s1 * 32767
    fmov s4, #2.0
    fmul s1, s1, s4       // s1 = s1 * 2
    fsub s1, s1, s2         // s1 = s1 - 32767
    ret

// Input: s1 = x
// Output: s1 ≈ cos(x)
cosf:
    // Argument: s1 = x >= 0
    // Return: s1 = cos(x)
    // Uses: s2, s3, s4, s5, s6,
    // Reduce x to [0, 2*pi)
    LOAD_ADDR x3, pi2_const
    ldr s2, [x3]                // s2 = 2*pi
    fdiv s3, s1, s2             // s3 = x / (2*pi)
    frintm s3, s3               // s3 = floor(x / 2*pi)
    fmul s3, s3, s2             // s3 = floor(x/2*pi) * 2*pi
    fsub s1, s1, s3             // s1 = x - floor(x/2*pi)*2*pi, now s1 in [0, 2*pi)

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

/*newcos:
    fcvt d1, s1               // d1 = double(x)
    adr x0,PI_2
	ldr d2,[x0]
	fsub d1,d2,d1
newsin:
	adr x0,PI_4
	ldr d2,[x0] // d2 <- PI_4
	mov x2,x30 // save lr for sin2a5 & sin2a6
	adr x3,sin2a0 // origin of jump table

    fdiv d3,d1,d2 // d3 <- x / PI_4
    frintm d3,d3  // d3 <- floor (d3)
    fmsub d1,d2,d3,d1 // d0 <- x mod PI_4

	fcvtas x1,d3
	and x1,x1,#7
	add x3,x3,x1,lsl#4
	br  x3

	.align 4
sin2a0: b sin1a

	.align 4
sin2a1:
	fsub d1,d2,d1
	b cos1a

	.align 4
sin2a2: b cos1a

	.align 4
sin2a3:
	fsub d1,d2,d1
	b sin1a

	.align 4
sin2a4:
	fneg d1,d1
	b sin1a

	.align 4
sin2a5:
	fsub d1,d2,d1
	bl cos1a
	fneg d1,d1
	br x2

	.align 4
sin2a6:
	bl cos1a
	fneg d1,d1
	br x2

	.align 4
sin2a7:
	fsub d1,d1,d2
	b sin1a

	// d0 - x
	// Use x0, v0~v7
sin1a:
	adr x0,sin1a1
	ldp d5,d6,[x0],16
	ldp d7,d8,[x0]

	fmul d2,d1,d1 // d2 <- x^2
	fmul d3,d2,d1 // d3 <- x^3
	fmul d4,d3,d2 // d4 <- x^5
	fmul d2,d2,d4 // d2 <- x^7
	fmadd d1,d6,d3,d1
	fmadd d1,d7,d4,d1
	fmadd d1,d8,d2,d1
    fcvt s1, d1
	ret

cos1a:
	adr x0,cos1a1
	ldp d5,d6,[x0],16
	ldp d7,d8,[x0]

	fmul d2,d1,d1 // d1 <- x^2
	fmul d3,d2,d2 // d2 <- x^4
	fmul d4,d3,d2 // d3 <- x^6
	fmov d1,d5 // d0 <- 1
	fmadd d1,d2,d6,d1
	fmadd d1,d3,d7,d1
	fmadd d1,d4,d8,d1
    fcvt s1, d1
	ret

	.align 3
PI:	.double 3.14159265358979
PI_4:	.double 0.78539816339745
PI_2:   .double 1.57079632679489

	.align 4
sin1a1:	.double 1,-0.16666666667,0.00833333333333,-0.0001984126984126
cos1a1: .double 1,-0.5,0.04166666666667,-0.001388888888889
*/

	;; Input:	x5 <- Instrument number
	;;          x4 <- Instrument definition
	;; Output:  s2 <- Value
    ;; Preserve: s0, s1, x10, x11, x12, x13
get_adsr_enveloping:
    LOAD_ADDR x3, instrument_ticks
    ldr w0, [x3, x5, lsl #2]            // w0 <- num ticks
    add w0, w0, #1                      // increase
    str w0, [x3, x5, lsl #2]            // store back to instrument_ticks
    scvtf s2, w0                        // Convert w0 to float in s2
    ldr s3, [x4, #inst_attack]          // s3 <- inst.attack
    fcmp s2, s3                         // are we in attack phase?
    b.gt attack_done                    // no, then jump
    fdiv  s2, s2, s3                    // s2 = s2 / s3
    ret
attack_done:
    fsub s2, s2, s3                      // subtract attack ticks
    ldr s3, [x4, #inst_decay]           // s3 <- inst.decay
    fcmp s2, s3                         // are we in decay phase?
    b.gt decay_done                     // no, then jump
    fmov s7, #1.0
    ldr s5, [x4, #inst_sustain]         // s5 <- inst.sustain
    fsub s4, s7, s5                     // s4 = 1.0 - sustain
    fdiv s6, s2, s3                     // s6 = delta / decay
    fmul s4, s4, s6                     // s4 = (1.0 - sustain) * (delta / decay)
    fsub s2, s7, s4                     // s2 = sustain + (1.0 - sustain) * (delta / decay)
    ret
decay_done:
    fsub s2, s2, s3                      // subtract decay ticks
    LOAD_ADDR x3, instrument_hold
    ldr s3, [x3, x5, lsl #2]            // s3 <- instrument_hold
    fcmp s2, s3                         // are we in sustain phase?
    b.gt sustain_done                   // no, then jump
    ldr s2, [x4, #inst_sustain]         // s2 <- inst.sustain
    ret
sustain_done:
    fsub s2, s2, s3                     // subtract hold ticks
    ldr s3, [x4, #inst_release]         // s3 <- inst.release
    fcmp s2, s3                         // are we in release phase?
    b.gt instrument_done2               // no, then jump
    fdiv s6, s2, s3                     // s6 = delta / release
    fmov s7, #1.0
    fsub s2, s7, s6                     // s2 = 1.0 - (delta / release)
    ldr s3, [x4, #inst_sustain]         // s2 <- inst.sustain
    fmul s2, s2, s3                     // s2 = sustain * (1.0 - (delta / release))
    ret 
instrument_done2:
    fmov s2, #0.0
    ret

pi_const:               .float 3.1415927
pi2_const:              .float 6.2831854
sampling_freq_const:    .float  44100.0

.data

f_echo_amp:         .float  ECHO_AMPLITUDE

track_index:        .word   -1,-1,-1,-1,-1, -1,-1,-1,-1,-1

track_1:            .byte   1, 5, 6, 5, 6, 5, 6, 5, 6, LOOP_TRACK
track_2:            .byte   0, LOOP_TRACK
track_3:            .byte   0, LOOP_TRACK
track_4:            .byte   1, 3,3,4,4, LOOP_TRACK
track_5:            .byte   0, LOOP_TRACK
track_6:            .byte   0, LOOP_TRACK
track_7:            .byte   7, LOOP_TRACK
track_8:            .byte   0, LOOP_TRACK
track_9:            .byte   0, LOOP_TRACK
track_10:           .byte   0, LOOP_TRACK

pattern_0:          .byte   0
                    .byte   END_PATTERN
pattern_1:          .byte   ECHO_ON
                    .byte   END_PATTERN
pattern_2:          .byte   ECHO_OFF
                    .byte   END_PATTERN
pattern_3:          .byte   g3x,g2x,g2x,g2x
                    .byte   g6x,00,00,g3x
                    .byte   g2x,g3x,00,g3x
                    .byte   g5x,00,00,g5x
                    .byte   END_PATTERN
pattern_4:          .byte   f3x,f2x,f2x,f2x
                    .byte   f6x,00,00,f3x
                    .byte   f2x,f3x,00,f3x
                    .byte   f5x,00,00,f5x
                    .byte   END_PATTERN
pattern_5:          .byte   f3x,0,0,f3x
                    .byte   END_PATTERN
pattern_6:          .byte   0,0,c3x,0
                    .byte   END_PATTERN
pattern_7:          .byte   0,0,f3x,0
                    .byte   END_PATTERN
pattern_8:          .byte   a4x,HOLD_4,0,0,0
                    .byte   0,0,0,0
                    .byte   0,0,0,0
                    .byte   END_PATTERN
pattern_9:          .byte   0
                    .byte   END_PATTERN
pattern_10:         .byte   0
                    .byte   END_PATTERN
pattern_11:         .byte   0
                    .byte   END_PATTERN
pattern_12:         .byte   0
                    .byte   END_PATTERN
pattern_13:         .byte   0
                    .byte   END_PATTERN
pattern_14:         .byte   0
                    .byte   END_PATTERN
pattern_15:         .byte   0
                    .byte   END_PATTERN
pattern_16:         .byte   0
                    .byte   END_PATTERN
pattern_17:         .byte   0
                    .byte   END_PATTERN
pattern_18:         .byte   0
                    .byte   END_PATTERN
pattern_19:         .byte   0
                    .byte   END_PATTERN
.align 8
track_list:	        .quad track_1, track_2, track_3, track_4, track_5
                    .quad track_6, track_7, track_8, track_9, track_10

pattern_list:		.quad pattern_0,   pattern_1,  pattern_2,  pattern_3
                    .quad pattern_4,   pattern_5,  pattern_6,  pattern_7
                    .quad pattern_8,   pattern_9,  pattern_10, pattern_11
                    .quad pattern_12,  pattern_13, pattern_14, pattern_15
                    .quad pattern_16,  pattern_17, pattern_18, pattern_19

instrument_definition:
base_drum: // Instrument 0: Sine wave, 5 Attack, 4000 Decay, 0 Sustain, 0 Release, 0 Modulation, -0.000004 Sweep
    .quad _get_sine_waveform
    .float 5, 4000, 0.0, 0, 0.0, -0.000004
snare1: // Instrument 1: Noise wave, 20 Attack, 6000 Decay, 0 Sustain, 0 Release, 0 Modulation, 0 Sweep
    .quad _get_noise_waveform
    .float 20, 6000, 0.0, 0, 0.0, 0.0
snare2:
    .quad _get_sawtooth_waveform
    .float 5, 10000, 0.0, 0, 0.0015, 0.0
base1:
    .quad _get_square_waveform
    .float 30, 2000, 0.0, 0, 0.000, 0.00000001
hit1:
    .quad _get_sine_waveform
    .float 5, 20000, 0.0, 0, 0.0003, 0.0
tom_drum:
    .quad _get_sine_waveform
    .float 5, 6000, 0.0, 0, 0.0, -0.000003
background_base:
    .quad _get_square_waveform
    .float 5, 2000, 0.0, 0, 0.0, 0.0
melody_triangle:
    .quad _get_sawtooth_waveform
    .float 5, 40000, 0.0, 0, 0.0, 0.0
melody_sine1:
    .quad _get_sine_waveform
    .float 10, 6000, 0.0, 0, 0.0005, 0.0
base_2:
    .quad _get_square_waveform
    .float 2, 2000, 0.0, 0, 0.005, 0.000002

msg:
    .ascii        "Hello, You have reached 555-DEBUG!"
len = . - msg

// -exec memory read --format f --count 72 &note_table
note_table:
    .float 0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0
    .float 0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0
    .float 0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0
    .float 0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0
    .float 0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0, 0.0,0.0,0.0
note_table_rework_dst:
    .float 0.0
    .float 1046.502,1108.731,1174.659,1244.508
    .float 1318.510,1396.913,1479.978,1567.982
    .float 1661.219,1760.000,1864.655
note_table_rework_src:
    .float 1975.533
note_table_end:

//sample_pos:		.word  instrument + 65536 * 4
ticks:			    .word  0
random_number:	    .word  RANDOM_SEED

;f_echo_amp:         .float ECHO_AMPLITUDE
f_sine_amp:         .float 32767.0

cos_c4: .float 0.04166667

.bss

;; Instrument data
f_instrument_delta:	    .space	MAX_NUM_INSTRUMENTS * 4 // float
f_instrument_offset:	.space	MAX_NUM_INSTRUMENTS * 4 // float
f_instrument_modo:	    .space	MAX_NUM_INSTRUMENTS * 4 // float
instrument_hold:	    .space	MAX_NUM_INSTRUMENTS * 4 // float
instrument_ticks:	    .space	MAX_NUM_INSTRUMENTS * 4 // uint32


pattern_index:          .space  MAX_NUM_INSTRUMENTS * 4
instrument_echo:        .space  MAX_NUM_INSTRUMENTS
echo_data:		        .space  65536 * MAX_NUM_INSTRUMENTS * 4
