%ifdef DEBUG
	cextern	printf
	cextern	fflush
%endif

section .text

%ifdef DEBUG
debug_print_int:
	pushad
 	mov     ebp,esp
	push	eax
	push	dword format_int
	call    printf
	add     esp, byte 8
	popad
	ret

debug_print_string:
	pushad
 	mov     ebp,esp
	mov	ebx, eax
	shr	ebx, 24
	and	ebx, 0FFh
	push	ebx
	mov	ebx, eax
	shr	ebx, 16
	and	ebx, 0FFh
	push	ebx
	mov	ebx, eax
	shr	ebx, 8
	and	ebx, 0FFh
	push	ebx
	mov	ebx, eax
	and	ebx, 0FFh
	push	ebx
	push	dword format_str
	call    printf
	add     esp, byte 20
	popad
	ret
%endif

%ifdef DEBUG
peax:	
	pushad
	push    eax
	mov     eax,print_int
	push    eax
	call    printf
	pop     eax
	pop     eax
	xor     eax,eax
	push    eax
	call    fflush
	pop     eax
	popad
	ret

fpeaxebx:
	pushad
	push    ebx
	push    eax
	mov     eax,print_float
	push    eax
	call    printf
	pop     eax
	pop     eax
	pop     eax
	xor     eax,eax
	push    eax
	call    fflush
	pop     eax
	popad
	ret

fpeax:
	pushad
	mov	[printf_dword], eax
	fld	dword [printf_dword]
	fstp	qword [printf_qword]
	push	dword [printf_qword+4]
	push	dword [printf_qword+0]
	mov     eax,print_float
	push    eax
	call    printf
	pop     eax
	pop     eax
	pop     eax
	xor     eax,eax
	push    eax
	call    fflush
	pop     eax
	popad
	ret
fpst0:
	pushad
	fst	qword [printf_qword]
	push	dword [printf_qword+4]
	push	dword [printf_qword+0]
	mov     eax,print_float
	push    eax
	call    printf
	pop     eax
	pop     eax
	pop     eax
	xor     eax,eax
	push    eax
	call    fflush
	pop     eax
	popad
	ret

pnl:
	pushad
	mov     eax,print_newline
	push    eax
	call    printf
	pop     eax
	xor     eax,eax
	push    eax
	call    fflush
	pop     eax
	popad
	ret
%endif


section .data
%ifdef DEBUG
format_int		db 'DEBUG: 0x%0lx',10,0
format_str		db 'DEBUG: %c%c%c%c',10,0
print_int:		db	"%d:",0
print_float:		db	"%.4f:",0
print_newline:		db	10,0
printf_dword		dd	0.0
printf_qword		dq	0.0
%endif

