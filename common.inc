%ifdef PREFIX
	%macro  cglobal 1 
		global  _%1 
		%define %1 _%1 
	%endmacro 
	%macro  cextern 1 
		extern  _%1 
		%define %1 _%1 
	%endmacro
%else
	%define cglobal global 
	%define cextern extern 
%endif

%ifdef BIT64
        %macro argument 1
	       mov rdi, %1
	%endmacro
        %macro argument 2
	       mov rdi, %1
	       mov rsi, %2
	%endmacro
%elifdef BIT32
        %macro call_function 2
	       %ifnidni %2, eax
	       	       mov eax, %2
	       %endif
	       push eax
	       call %1
	       add esp, 4
	%endmacro
        %macro call_function 3
	       %ifnidni %2, eax
	       	       mov eax, %2
	       %endif
	       push eax
	       mov eax, %3
	       push eax
	       call %1
	       add esp, 8
	%endmacro
        %macro call_function 4
	       %ifnidni %2, eax
	       	       mov eax, %2
	       %endif
	       push eax
	       mov eax, %3
	       push eax
	       mov eax, %4
	       push eax
	       call %1
	       add esp, 12
	%endmacro
        %macro call_function 5
	       %ifnidni %2, eax
	       	       mov eax, %2
	       %endif
	       push eax
	       mov eax, %3
	       push eax
	       mov eax, %4
	       push eax
	       mov eax, %5
	       push eax
	       call %1
	       add esp, 16
	%endmacro
        %macro argument 1
	       mov eax, %1
	%endmacro
%else
	%error BIT32 or BIT64 needs to be set
%endif
