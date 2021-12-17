; The main program
;	bits    32

%include "common.inc"
%include "debug.inc"

;;; Define external c function calls
;;; SDL
	cextern SDL_Init
	cextern	SDL_Quit
	cextern	SDL_OpenAudio
	cextern	SDL_PollEvent
	cextern	SDL_Delay
	cextern	SDL_PauseAudio
	cextern	SDL_SetVideoMode
;;; Windows exit process
 	cextern ExitProcess@4
	
;;; Define external softsynth asm functions
	cextern	softsynth_play
	cextern	softsynth_init

;;; Define necessary start point for different platforms
	cglobal	_start		; Linux32
	cglobal	start
	cglobal	main
 	cglobal	mainCRTStartup	; Win10 Visual Studio 2019

	section .code	align=1
mainCRTStartup:
_start:
start:
main:
 	pushad

%ifdef DEBUG
	;; Debug
	mov	eax, 'main'
	call	debug_print_string
%endif
	
	;; Initialize soft synth
	call	softsynth_init
	
	;; Load GL and SDL libraries
; 	call	load_libraries

	;; Initialize SDL
	call_function SDL_Init, 31h ; 0x31 = TIMER, AUDIO, VIDEO

	;; Open and initialize audio
	; obtained spec, wanted spec
	call_function SDL_OpenAudio, 0, audio_spec

	;; Set the video mode
	; Fullscreen, color depth, height, width
%ifdef FULLSCREEN
        mov     eax,80000003h	; Fullscreen
%else
        mov     eax,00000003h	; Windowed 
%endif
	call_function SDL_SetVideoMode, eax, 32, 480, 640 

	;; Start playing song
	call_function SDL_PauseAudio, 0
		
main_loop:
 	call_function SDL_PollEvent, struct
 	cmp     byte [struct],2 
 	jne     main_loop

quit:
	;; Clean up SDL
 	call    SDL_Quit	; Call SDL_Quit

%ifdef DEBUG
	;; Debug
	mov	eax, 'quit'
	call	debug_print_string
%endif
	
 	popad
	
	;; End process
%ifdef WINDOWS
	push    dword 0
	call    ExitProcess@4
%elifdef RET
	ret
%else
	xor     eax,eax
  	inc     al		; eax=1
  	xor     ebx,ebx		; ebx=0 (ok)
  	int     080h		; Exit process
%endif
	
	section .data align=1

audio_spec:
	dd	44100		; Frequency
	dw	8010h		; Audio data format 
					; (AUDIO_S16LSB)
	db	1		; Mono
	db	0		; Silence value 
	dw	4096		; Num samples
	dw	0		; Alignment
	dd	0		; Size of buffer
	dd	softsynth_play	; Function for playing song 
	dd	0		; Userdata 
	
	section .bss align=1

struct: resd    10000
