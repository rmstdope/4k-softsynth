	bits    32

%include "common.inc"
%include "debug.inc"

	;; From softsynth.asm
	extern	get_instrument_value
	extern	note_table
	extern	f_sampling_freq
	extern	f_instrument_delta
	cextern	instrument_ticks
	extern	f_instrument_offset
	extern	f_instrument_modo

	;; For AED
	cglobal	get_instrument_value_c
	cglobal	start_instrument

section .text

	;; Output:	eax <- Value
get_instrument_value_c:
	push	ebp
	mov	ebp,esp				; Move esp to ebp
	pushad
	mov	ecx,[ebp+8]			; Move instrument to ecx
	shl	ecx,2
	call	get_instrument_value
	popad
	pop	ebp
	fistp	dword [temp_dword]
	mov	eax,[temp_dword]
	ret

	;; 440Hz -> 2 * Pi * 440 / 44100 increase per tick
start_instrument:
	push	ebp
	mov	ebp,esp				; Move esp to ebp
	pushad
	mov	eax,dword [ebp+12]		; Move tone to eax
	mov	ecx,dword [ebp+8]		; Move instrument to ecx
	shl	ecx,2				; ecx = instr * 4
	shl	eax,2				; Note table is dwords
	fld	dword [note_table+eax]		; Get value from note_table
	fldpi					; Load Pi
	fadd	st0,st0				; 2 * Pi -> st0
	fmulp	st1,st0				; 2 * Pi * Freq -> st0
	fdiv	dword [f_sampling_freq]		; 2 * Pi * Freq / 44100 -> st0
	fstp	dword [f_instrument_delta+ecx]	; Store delta
	fldz					; Load 0.0 in st0
	fist	dword [instrument_ticks+ecx]	; Clear instrument ticks
	fst	dword [f_instrument_offset+ecx]	; Clear instrument offset
	fstp	dword [f_instrument_modo+ecx]	; Clear instrument modulation offset
	popad
	pop	ebp
	ret
	


section	.bss

temp_dword:		resd	1
