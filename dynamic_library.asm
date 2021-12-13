; 4085
;        bits    32		;

%include "common.inc"
%include "debug.inc"

        cextern	dlopen
	cextern	dlsym
        global	load_libraries

	global	SDL_Init
	global	SDL_Quit
	global	SDL_SetVideoMode
	global	SDL_OpenAudio
	global  SDL_ShowCursor
	global	SDL_PauseAudio
	global	SDL_GetTicks
	global	SDL_GL_SwapBuffers
	global  SDL_PollEvent
	global	SDL_Delay

        section .text
        
load_libraries:
	pushad			; Save registers
	mov     eax,SDL_library	; Name of SDL library
	mov     edi,SDL_pointers; Start of SDL function pointers
	mov     esi,SDL_names	; Start of SDL function names
	call    load		; Load library
; 	mov     eax,GL_library	; Name of GL library
; 	mov     edi,GL_pointers	; Start of GL function pointers
; 	mov     esi,GL_names	; Start of GL function names
; 	call    load		; Load library
	popad			; Restore registers
	ret

load:
	mov     ebx,2		; RTLD_NOW
	push    ebx		; RTLD_NOW
	push    eax		; Name of library
	call    dlopen		; Call dlopen
	mov     ebp,eax		; Move return values to ebp
	add	esp, 8		; Correct stack

scan:	
	lodsd			; Read next name into eax
	cmp     eax,0		; Check if it is the last?
	je      stop_scan	; If last, jump to end
	push    eax		; Name of function
	push    ebp		; Pointer to library
	call    dlsym		; Call dlsym
	add	esp, 8		; Correct stack
	stosd			; Save value in edi
%ifdef DEBUG
 	call	debug_print_int
%endif
	jmp     scan		; Continue loop

stop_scan: 
	ret

	
        section .data
; GL_names		dd	0
; 			dd      nglBegin, nglEnd, nglVertex3f, nglMatrixMode,
; 			dd      nglLoadIdentity, nglClear, nglColor3f
; 			dd      nglRotatef, nglTranslatef, nglEnable, 
; 			dd	nglDisable, nglLineWidth, nglFrustum
; 			dd	nglBindTexture, nglTexParameteri
; 			dd	nglTexImage2D, nglCopyTexSubImage2D,
; 			dd	nglTexCoord2f, nglBlendFunc
; 			dd      0

SDL_names		dd      nSDL_Init, nSDL_Quit, nSDL_SetVideoMode
			dd	nSDL_OpenAudio, nSDL_ShowCursor, 
			dd	nSDL_PauseAudio, nSDL_GetTicks, 
			dd	nSDL_GL_SwapBuffers, nSDL_PollEvent
			dd	nSDL_Delay
			dd      0

; GL_library		db      "GL.dll",0
; SDL_library		db      "SDL.dll",0

%ifdef DLL
; GL_library		db      "GL.dll",0
SDL_library		db      "SDL.dll",0
%endif
%ifdef SO
; GL_library		db      "libGL.so",0
SDL_library		db      "libSDL-1.2.so.0",0
%endif

; nglBegin		db      "glBegin",0
; nglEnd			db      "glEnd",0
; nglVertex3f		db      "glVertex3f",0
; nglMatrixMode		db      "glMatrixMode",0
; nglLoadIdentity		db      "glLoadIdentity",0
; nglClear		db      "glClear",0
; nglColor3f		db      "glColor3f",0
; nglRotatef		db	"glRotatef",0
; nglTranslatef		db	"glTranslatef",0
; nglEnable		db	"glEnable",0
; nglDisable		db      "glDisable",0
; nglLineWidth		db      "glLineWidth",0
; nglFrustum		db      "glFrustum",0
; nglBindTexture		db	"glBindTexture",0
; nglTexParameteri	db	"glTexParameteri",0
; nglTexImage2D		db	"glTexImage2D",0
; nglCopyTexSubImage2D	db	"glCopyTexSubImage2D",0
; nglTexCoord2f		db	"glTexCoord2f",0
; nglBlendFunc		db	"glBlendFunc",0

nSDL_Init		db	"SDL_Init",0
nSDL_Quit		db	"SDL_Quit",0
nSDL_SetVideoMode	db	"SDL_SetVideoMode",0
nSDL_OpenAudio		db	"SDL_OpenAudio",0
nSDL_ShowCursor		db	"SDL_ShowCursor",0
nSDL_PauseAudio		db	"SDL_PauseAudio",0
nSDL_GetTicks		db	"SDL_GetTicks",0
nSDL_GL_SwapBuffers	db	"SDL_GL_SwapBuffers",0
nSDL_PollEvent		db	"SDL_PollEvent",0
nSDL_Delay		db	"SDL_Delay", 0

	
        section .bss
; GL_pointers
; _glBegin		resd    1
; _glEnd			resd    1
; _glVertex3f		resd    1
; _glMatrixMode		resd    1
; _glLoadIdentity		resd    1
; _glClear		resd    1
; _glColor3f		resd    1
; _glRotatef		resd	1
; _glTranslatef		resd	1
; _glEnable		resd	1
; _glDisable		resd    1
; _glLineWidth		resd    1
; _glFrustum		resd    1
; _glBindTexture		resd	1
; _glTexParameteri	resd	1
; _glTexImage2D		resd	1
; _glCopyTexSubImage2D	resd 	1
; _glTexCoord2f		resd	1
; _glBlendFunc		resd	1

SDL_pointers
SDL_Init		resd    1
SDL_Quit		resd    1
SDL_SetVideoMode	resd    1
SDL_OpenAudio		resd    1
SDL_ShowCursor		resd    1
SDL_PauseAudio		resd    1
SDL_GetTicks		resd    1
SDL_GL_SwapBuffers	resd    1
SDL_PollEvent		resd    1
SDL_Delay		resd	1
