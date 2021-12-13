	bits    32

%include "common.inc"
%include "debug.inc"

	;; For AED
	cglobal	softsynth_init
	cglobal	softsynth_play
	cglobal	instrument_definition
	cglobal	instrument_hold
	cglobal	instrument_ticks
	cglobal	pattern_list
	cglobal	pattern_index
	cglobal	track_list
	cglobal	track_index
	cglobal	ticks
	cglobal	sample_data
	cglobal get_sine_waveform
	cglobal get_noise_waveform
	cglobal get_square_waveform
	cglobal get_sawtooth_waveform

	;; For softsynth_wrapper.asm
	global	get_instrument_value
	global	note_table
	global	f_sampling_freq
	global	f_instrument_delta
	global	f_instrument_offset
	global	f_instrument_modo

	
section .text

%define c1 0
%define C1 1
%define d1 2
%define D1 3
%define e1 4
%define f1 5
%define F1 6
%define g1 7
%define G1 8
%define a1 9
%define A1 10
%define B1 11
%define c2 12
%define C2 13
%define d2 14
%define D2 15
%define e2 16
%define f2 17
%define F2 18
%define g2 19
%define G2 20
%define a2 21
%define A2 22
%define B2 23
%define c3 24
%define C3 25
%define d3 26
%define D3 27
%define e3 28
%define f3 29
%define F3 30
%define g3 31
%define G3 32
%define a3 33
%define A3 34
%define B3 35
%define c4 36
%define C4 37
%define d4 38
%define D4 39
%define e4 40
%define f4 41
%define F4 42
%define g4 43
%define G4 44
%define a4 45
%define A4 46
%define B4 47
%define c5 48
%define C5 49
%define d5 50
%define D5 51
%define e5 52
%define f5 53
%define F5 54
%define g5 55
%define G5 56
%define a5 57
%define A5 58
%define B5 59
%define c6 60
%define C6 61
%define d6 62
%define D6 63
%define e6 64
%define f6 65
%define F6 66
%define g6 67
%define G6 68
%define a6 69
%define A6 70
%define B6 71

%define NUM_INSTRUMENTS 10

%define BEATS_PER_MINUTE 125
%define NOTES_PER_BEAT 4
%define ROW_TICKS (60 * 44100 / (BEATS_PER_MINUTE * NOTES_PER_BEAT))

%define ECHO_LENGTH (ROW_TICKS * 3)
%define ECHO_AMPLITUDE 2.0
%define RANDOM_SEED 038fa39bch

%define END_PATTERN -2
%define END_TRACK -2
%define LOOP_TRACK -3
%define STOP -4
%define ECHO_ON -5
%define ECHO_OFF -6
%define HOLD_5 -7
%define HOLD_4 -8
%define HOLD_3 -9
%define HOLD_2 -10
%define HOLD_1 -11
%define HOLD_ADD -HOLD_1 + 1

		
	; The init routine of the softsynth
softsynth_init:	
	pushad					; Save registers

	;; Create note table
notes_init:
	mov     esi,note_table_end - 4		; Set esi to end of note_table 
	mov     edi,note_table_end-(12+1)*4	; Set edi to last zero row
	mov     ecx,5*12			; The number of loops 
note_loop:
	fld	dword [esi]			; Load value
	fld	dword [f_two]			; Load two
	fdivp	st1,st0				; Divide value by two
	fstp	dword [edi]			; Store in edi
	sub	esi,4				; Sub 4 from esi
	sub	edi,4				; Sub 4 from edi
	loop    note_loop			; loop

	popad
	ret

%define PLAY_DATA_OFFSET    12
%define PLAY_LEN_OFFSET     16

softsynth_play:
	push	ebp				; Save ebp register
	mov	ebp,esp				; Set ebp to esp
	pushad					; Save all registers
	mov	edi,[ebp+PLAY_DATA_OFFSET]	; Pointer edi to data buffer
do_sample:
	mov	eax,[ticks]			; Get # of ticks
        mov	ebx,ROW_TICKS			; Move row ticks to ebx
        cdq					; Convert to wuad word
        div	ebx				; Divide ticks with row ticks
        or	edx,edx				; Check if remained is 0
        jz	new_row				; If 0, get new row
        jmp	sum_instruments			; No new row

new_row:
	xor	ecx, ecx			; Clear ecx
row_loop:	
	mov	eax,[track_index+ecx]		; Get track index for instr
instrument_not_done:
	inc	dword [pattern_index+ecx]	; Do next pattern
	cmp	eax,-1				; Check if track index is -1
        je	new_pos				; If so, get new pos
	call	get_command			; Get command
	cmp	al,END_PATTERN			; Check if command is END_PATT
        jne	no_new_pos			; No new pos

new_pos:
	inc	dword [track_index+ecx]		; Do next track
	mov	eax,[track_index+ecx]		; Get track index for instr
	mov	ebx,[track_list+ecx]		; Get track pointer for instr
	add	ebx,eax				; Add index to pointer
	mov	al,[ebx]			; Get track info
	xor	edx,edx				; Clear edx
	cmp	al,LOOP_TRACK			; Check if this is a LOOP_TRACK
	jne	no_loop				; If not, jump
	mov	[track_index+ecx],edx		; Clear track index
no_loop:
	mov	[pattern_index+ecx],edx		; Clear pattern index

no_new_pos:
	call    get_command			; Get command
	or      al,al				; Check if zero
	jz      instrument_done			; If so, jump
	cmp     al,STOP				; Check if STOP command
	jne     no_stop				; If not, jump
	je      instrument_done			; Instrument done
no_stop:
	cmp     al,ECHO_ON			; Check if ECHO_ON command
	jne     no_echo_on			; If not, jump
	mov     [ecx+instrument_echo],al	; Set echo on
	je      instrument_not_done		; Instrument done
no_echo_on:
	cmp     al,ECHO_OFF			; Check if ECHO_OFF command
	jne     no_echo_off			; If not, jump
	xor     dl,dl				; Clear dl
	mov     [ecx+instrument_echo],dl	; Set echo off
	jz      instrument_not_done		; Instrument done
no_echo_off:

	;; Start instrument
	shl	eax,2				; Note table is dwords
	fld	dword [note_table+eax]		; Get value from note_table
	fldpi					; Load Pi
	fadd	st0,st0				; 2 * Pi -> st0
	fmulp	st1,st0				; 2 * Pi * Freq -> st0
	fdiv	dword [f_sampling_freq]		; 2 * Pi * Freq / 44100 -> st0
	fstp	dword [f_instrument_delta+ecx]	; Store delta
	fldz					; Load 0.0 in st0
	fist	dword [instrument_ticks+ecx]	; Clear instrument ticks
	fist	dword [instrument_hold+ecx]	; Clear instrument hold time
	fst	dword [f_instrument_offset+ecx]	; Clear instrument offset
	fstp	dword [f_instrument_modo+ecx]	; Clear instrument modulation 

	cmp	bl,HOLD_5			; Check if HOLD_x command
	jg	no_hold				; If not, jump
	add	bl,HOLD_ADD			; Add HOLD_ADD to bl
	xor	bh,bh				; Clear bh
	mov	ax, ROW_TICKS
	mul	bx				; Mul ROW_TICKS with ax
	mov	[ecx+instrument_hold],eax	; Set instrument_hold
	inc	dword [pattern_index+ecx]	; Skip next pattern note
no_hold:
	
instrument_done:
	add     ecx,4				; Add 4 (next instrument)
	cmp     ecx,NUM_INSTRUMENTS * 4		; Check if done
	je      sum_instruments			; If so, jump
	jmp     row_loop			; loop back

	;; The summing loop
sum_instruments:
	fldz					; Clear sum
	xor	ecx,ecx				; Clear ecx
	mov     esi,echo_data			; Set esi to echo

sum_loop:
	;; First, do echo
	mov     eax,[ticks]			; Get ticks
	inc     eax				; Increase
	call    get_echo_pointer		; Call echo
	fld	dword [edx]			; Load echo value
	fld	st0				; Load once again
	fld	dword [f_two]			; Load two
	fdivp	st1, st0			; Divide by two
	
	mov     eax,[ticks]			; Get ticks again
	call    get_echo_pointer		; Call echo
	fstp	dword [edx]			; Store half echo value
	faddp	st1, st0			; Add echo value to sum
	push	edx				; Push echo pointer

	call	get_instrument_value
	fadd	st1,st0				; Add value to sum
	pop	ebx				; Restore echo pointer
	test    byte [instrument_echo+ecx],0ffh	; Check if echo should be added
	jz      no_echo				; If not, jump
	fld	dword [f_echo_amp]		; Load echo amplitude
	fdivp	st1, st0			; Divide sample with amp
	fadd	dword [ebx]			; Store as new echo
	fstp	dword [ebx]
	jmp	skipchan        
no_echo:
	fcomp	st0				; Pop stack
	
skipchan:
	add     esi,65536*4			; Point esi to next instrument
	add     ecx,4				; Add four to ecx
	cmp     ecx,NUM_INSTRUMENTS * 4		; Check if all instruments done
	je      instruments_summed		; If so, jump
	jmp     sum_loop			; Loop back

instruments_summed:
	fld	dword [f_three]			; Load three
	fdivp	st1, st0			; Divide sum with three
	fistp	dword [temp_dword]		; Store in temp_dword
	mov	eax,[temp_dword]		; Move temp_dword to eax
	cmp     eax,-32767			; Check if too low
	jge     clip2				; If not, jump
	mov     eax,-32767			; Clamp
clip2:
	cmp     eax,32767			; Check if too high
	jle     done				; If not, jump
	mov     eax,32767			; Clamp
done:
	stosw					; Store in destination
	inc     dword [ticks]			; Increase ticks
	sub     dword [ebp+PLAY_LEN_OFFSET],2	; Sub two from length
	jz      all_done			; If zero, jump
	jmp     do_sample			; Else loop
all_done:   
	mov     edi,[ebp+PLAY_DATA_OFFSET]	; Save destination in edi
	mov     [sample_data],edi		; Store in smp (for later analyze)

	popad					; Restore registers
	pop     ebp				; Restore ebp
	ret					; Return

get_command:
	mov     eax,[track_index+ecx]		; Get track index
	mov     ebx,[track_list+ecx]		; Get track pointer
	add     ebx,eax				; Add index to pointer
	xor     eax,eax				; Clear eax
	mov     al,[ebx]			; Get pointed value
	shl     eax,2				; Mul with 4
	mov     ebx,[pattern_list+eax]		; Get pattern pointer
	add     ebx,[pattern_index+ecx]		; Add pattern index
	mov     al,[ebx]			; Get pointer value
	mov     bl,[ebx+1]			; Get possible hold value
	ret					; Return

get_echo_pointer:
	mov     ebx,ECHO_LENGTH			; Get echo length
	cdq					; Convert to quad word
	div     ebx				; Divide eax with echo length
	shl     edx,2				; Mul remainder with 4
	add     edx,esi				; Add esi to edx
	ret					; Return
    	
rnd:    mov     eax,[random_number]
        add     eax,RANDOM_SEED
        xor     eax,RANDOM_SEED
        ror     eax,1
        mov     [random_number],eax
        ret

	;; Output:	eax <- Value
get_instrument_value:
	push	ebp
	mov	eax,ecx				; Move ecx to eax
	shr	eax,2				; eax = instr
	mov	edx,inst.size			; Move inst.size to edx
	mul	edx				; eax = instr * inst.size
 	mov	ebp,eax				; Move eax to ebp
 	add	ebp,instrument_definition	; Add instrument def. to ebp
	fld	dword [f_instrument_offset+ecx]	; Load offset
; 	fld	st0				; Load offset again
	;; Get basic waveform
 	call	dword [ebp+inst.waveform]; Get waveform value
	;; Add ADSR volume enveloping
	call	get_adrs_enveloping		; Get volume value
	fmulp	st1,st0				; Multiply waveform with volume
	;; Add modulation
	fld	dword [f_instrument_modo+ecx]	; Load modulation offset
	call	get_sine_waveform		; Get sine waveform
	mov	dword [temp_dword],16		; Put 16 in temp dword
	fild	dword [temp_dword]		; Load 16
	fdivp	st1,st0				; Divide modulation with 16 and pop
	fmulp	st1,st0				; Multiply waveform with modulation
	mov	dword [temp_dword],256 * 16	; Put 256 * 16 in temp dword
	fild	dword [temp_dword]		; Load 256 * 16
	fdivp	st1,st0				; Divide modulation with 16 and pop
	;; Increase values
	fld	dword [f_instrument_offset+ecx]	; Load offset
	fadd	dword [f_instrument_delta+ecx]	; Add delta to offset
	fstp	dword [f_instrument_offset+ecx]	; Store result in offset
	fld	dword [f_instrument_delta+ecx]	; Load delta
	fadd	dword [ebp+inst.sweep]		; Add sweep to delta
	fstp	dword [f_instrument_delta+ecx]	; Store result in delta
	fld	dword [f_instrument_modo+ecx]	; Load modulation offset
	fadd	dword [ebp+inst.modulation]	; Add delta to modulation offset
	fstp	dword [f_instrument_modo+ecx]	; Store modulation offset
	pop	ebp
	ret
	

	;; Input:	st0 <- Position
	;; Output:	st0 <- Value
get_sine_waveform:
	fcos					; sin(st0) -> st0
	fmul	dword [f_sine_amp]		; st0 * amp -> st0
	ret

	;; Input:	st0 <- Position
	;; Output:	st0 <- Value
get_noise_waveform:
	fcomip	st0
	call    rnd				; Get a random value in eax
	and     eax,0ffffh			; Set range to [0..65536]
	sub     eax,32768			; Set range to [-32767..32768]
	mov	[temp_dword], eax		; Move to temp dword
	fild	dword [temp_dword]		; Load temp dword
	ret

	;; Input:	st0 <- Position
	;; Output:	st0 <- Value
get_square_waveform:
	fsin					; sin(st0) -> st0
	ftst					; Test st0 to 0.0
	fstsw	ax				; Move FPU register to ax
	fcomip	st0				; Pop stack
	fld	dword [f_sine_amp]		; Load 32767 into st0
	sahf					; Load flags with ah
	ja	positive_square			; If so, jump
	fchs					; Change sign of st0
positive_square:
	ret

	;; Input:	st0 <- Position
	;; Output:	st0 <- Value
get_sawtooth_waveform:
	fldpi					; Load Pi
	fadd	st0,st0				; Load 2 * Pi
 	fxch					; Exchange st0 and st1
	fprem					; Get remained of division st0/(2*pi)
	fxch					; Exchange st0 and st1
	fdivp	st1,st0				; Divide with 2*Pi
	fmul	dword [f_sine_amp]		; Mul with 32767
	fadd	st0,st0				; Mul with 2
	fsub	dword [f_sine_amp]		; Make in range [-32767..32767]
	ret

	;; Input:	ecx <- Instrument number * 4
	;;		ebp <- Instrument definition
	;; Output:	st0 <- Value
get_adrs_enveloping:		
	mov	ebx,[instrument_ticks+ecx]	; Get instrument ticks
	inc	ebx				; Increase with one
	mov	[instrument_ticks+ecx], ebx	; Store back
	cmp	ebx,[ebp+inst.attack]
	jg	attack_done
	fld1					; Load one
	fild	dword [instrument_ticks+ecx]	; Load num ticks
	fidiv	dword [ebp+inst.attack]		; Divide with attack ticks
	fmulp	st1				; Multiply st0 and st1 and pop
	ret
attack_done:
	sub	ebx,[ebp+inst.attack]		; Subtract attack ticks
	cmp	ebx,[ebp+inst.decay]		; Check if we are in decay phase
	jg	decay_done
	fld1					; Load one
	fld	dword [ebp+inst.sustain]	; Load sustain volume
	fsub	st0,st1				; st0 <- st0-st1
	mov	[temp_dword], ebx		; Move delta ticks to temp word
	fild	dword [temp_dword]		; Load temp word
	fidiv	dword [ebp+inst.decay]		; Divide with decay ticks
	fmulp	st1,st0				; Multiply st0 with st1 and pop
	faddp	st1,st0				; Add st0 with st1 and pop
	ret
decay_done:
	sub	ebx,[ebp+inst.decay]		; Subtract decay ticks
	cmp	ebx,[instrument_hold+ecx]	; Check if we are in sustain phase
	jg	sustain_done
	fld	dword [ebp+inst.sustain]	; Load sustain volume
	ret
sustain_done:
	sub	ebx,[instrument_hold+ecx]	; Subtract hold from ticks
	cmp	ebx,[ebp+inst.release]		; Check if we are in release phase
	jg	instrument_done2
	fld	dword [ebp+inst.sustain]	; Load sustain volume
	fld	st0				; Load again
	mov	[temp_dword], ebx		; Move delta ticks to temp word
	fild	dword [temp_dword]		; Load temp word
	fidiv	dword [ebp+inst.release]	; Divide with release ticks
	fmulp	st1,st0				; Multiply st0 with st1 and pop
	fsubp	st1,st0				; Subtract st0 from st1 and pop
	ret
instrument_done2:
	fldz
	ret
	
section	.data

struc inst
	.waveform	resd	1
	.attack		resd	1
	.decay		resd	1
	.sustain	resd	1
	.release	resd	1
	.modulation	resd	1
	.sweep		resd	1
	.size		resd	0
endstruc

f_two:			dd	2.0
f_three:		dd	3.0
f_echo_amp:		dd	ECHO_AMPLITUDE
f_sine_amp:		dd	32767.0
f_sampling_freq:	dd	44100.0

track_index:		dd      -1,-1,-1,-1,-1, -1,-1,-1,-1,-1

track_1:		db	1, 5, 6, 5, 6, 5, 6, 5, 6, LOOP_TRACK
track_2:		db	0, LOOP_TRACK
track_3:		db	0, LOOP_TRACK
track_4:		db	1, 3,3,4,4, LOOP_TRACK
track_5:		db	0, LOOP_TRACK
track_6:		db	0, LOOP_TRACK
track_7:		db	7, LOOP_TRACK
track_8:		db	0, LOOP_TRACK
track_9:		db	0, LOOP_TRACK
track_10:		db	0, LOOP_TRACK

pattern_0:		db	0
			db	END_PATTERN
pattern_1:		db	ECHO_ON
			db	END_PATTERN
pattern_2:		db	ECHO_OFF
			db	END_PATTERN
pattern_3:		db	g3,g2,g2,g2
			db	g6,00,00,g3
			db	g2,g3,00,g3
			db	g5,00,00,g5
			db	END_PATTERN
pattern_4:		db	f3,f2,f2,f2 
			db	f6,00,00,f3
			db	f2,f3,00,f3
			db	f5,00,00,f5
			db	END_PATTERN
pattern_5:		db	f3,0,0,f3
			db	END_PATTERN
pattern_6:		db	0,0,c3,0
			db	END_PATTERN
pattern_7:		db	0,0,f3,0
			db	END_PATTERN
pattern_8:		db	a4,HOLD_4,0,0,0
			db	0,0,0,0
			db	0,0,0,0
			db	END_PATTERN
pattern_9:		db	0
			db	END_PATTERN
pattern_10:		db	0
			db	END_PATTERN
pattern_11:		db	0
			db	END_PATTERN
pattern_12:		db	0
			db	END_PATTERN
pattern_13:		db	0
			db	END_PATTERN
pattern_14:		db	0
			db	END_PATTERN
pattern_15:		db	0
			db	END_PATTERN
pattern_16:		db	0
			db	END_PATTERN
pattern_17:		db	0
			db	END_PATTERN
pattern_18:		db	0
			db	END_PATTERN
pattern_19:		db	0
			db	END_PATTERN

track_list:		dd	track_1, track_2, track_3, track_4, track_5, 
			dd	track_6, track_7, track_8, track_9, track_10

pattern_list:		dd	pattern_0,  pattern_1,  pattern_2,  pattern_3
			dd	pattern_4,  pattern_5,  pattern_6,  pattern_7
			dd	pattern_8,  pattern_9,  pattern_10, pattern_11
			dd	pattern_12, pattern_13, pattern_14, pattern_15
			dd	pattern_16, pattern_17, pattern_18, pattern_19

instrument_definition:
base_drum:
	istruc	inst
		at inst.waveform,	dd	get_sine_waveform
		at inst.attack,		dd	5
		at inst.decay,		dd	4000
		at inst.sustain,	dd	0.0
		at inst.release,	dd	0
		at inst.modulation,	dd	0.0
		at inst.sweep,		dd	-0.000004
	iend
snare1:
	istruc	inst
; 		at inst.waveform,	dd	get_sine_waveform 
		at inst.waveform,	dd	get_noise_waveform
		at inst.attack,		dd	20
		at inst.decay,		dd	6000
		at inst.sustain,	dd	0.0
		at inst.release,	dd	0
		at inst.modulation,	dd	0.0
		at inst.sweep,		dd	0.0
	iend
snare2:
	istruc	inst
		at inst.waveform,	dd	get_sawtooth_waveform
		at inst.attack,		dd	5
		at inst.decay,		dd	10000
		at inst.sustain,	dd	0.0
		at inst.release,	dd	0
		at inst.modulation,	dd	0.0015
		at inst.sweep,		dd	0.0
	iend
base1:
	istruc	inst
		at inst.waveform,	dd	get_square_waveform
		at inst.attack,		dd	30
		at inst.decay,		dd	2000
		at inst.sustain,	dd	0.0
		at inst.release,	dd	0
		at inst.modulation,	dd	0.000
		at inst.sweep,		dd	0.00000001
	iend
hit1:
	istruc	inst
		at inst.waveform,	dd	get_sine_waveform
; 		at inst.waveform,	dd	get_noise_waveform
		at inst.attack,		dd	5
		at inst.decay,		dd	20000
		at inst.sustain,	dd	0.0
		at inst.release,	dd	0
		at inst.modulation,	dd	0.0003
		at inst.sweep,		dd	0.0
	iend
tom_drum:
	istruc	inst
		at inst.waveform,	dd	get_sine_waveform
		at inst.attack,		dd	5
		at inst.decay,		dd	6000
		at inst.sustain,	dd	0.0
		at inst.release,	dd	0
		at inst.modulation,	dd	0.0
		at inst.sweep,		dd	-0.000003
	iend
background_base:
	istruc	inst
		at inst.waveform,	dd	get_square_waveform
		at inst.attack,		dd	5
		at inst.decay,		dd	2000
		at inst.sustain,	dd	0.0
		at inst.release,	dd	0
		at inst.modulation,	dd	0.0
		at inst.sweep,		dd	0.0
	iend
melody_triangle:
	istruc	inst
		at inst.waveform,	dd	get_sawtooth_waveform
		at inst.attack,		dd	5
		at inst.decay,		dd	40000
		at inst.sustain,	dd	0.0
		at inst.release,	dd	0
		at inst.modulation,	dd	0.0
		at inst.sweep,		dd	0.0
	iend
melody_sine1:
	istruc	inst
		at inst.waveform,	dd	get_sine_waveform
		at inst.attack,		dd	10
		at inst.decay,		dd	6000
		at inst.sustain,	dd	0.0
		at inst.release,	dd	0
		at inst.modulation,	dd	0.0005
		at inst.sweep,		dd	0.0
	iend
base_2:
	istruc	inst
		at inst.waveform,	dd	get_square_waveform
		at inst.attack,		dd	2
		at inst.decay,		dd	2000
		at inst.sustain,	dd	0.0
		at inst.release,	dd	0
		at inst.modulation,	dd	0.005
		at inst.sweep,		dd	0.000002
	iend
	
note_table:	
		dd	0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0
		dd	0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0
		dd	0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0
		dd	0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0
		dd	0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0, 0.0,0.0,0.0,0.0
		dd	1046.502,1108.731,1174.659,1244.508
		dd	1318.510,1396.913,1479.978,1567.982
		dd	1661.219,1760.000,1864.655,1975.533
note_table_end:

sample_pos:		dd  instrument + 65536 * 4
ticks:			dd  0

random_number:		dd  RANDOM_SEED

section .bss

;; Temp variables for rendering loop
sample_data:	resd	1

instrument:
_instrument:	resd    65536 * (NUM_INSTRUMENTS+1)

;; Instrument data
f_instrument_delta:	resd	NUM_INSTRUMENTS
f_instrument_offset:	resd	NUM_INSTRUMENTS
f_instrument_modo:	resd	NUM_INSTRUMENTS
instrument_hold:	resd	NUM_INSTRUMENTS * 2
instrument_ticks:	resd	NUM_INSTRUMENTS * 2

temp_dword:		resd	1

pattern_index:		resd    NUM_INSTRUMENTS

instrument_echo:	resd    NUM_INSTRUMENTS
echo_data:		resd    65536 * NUM_INSTRUMENTS
