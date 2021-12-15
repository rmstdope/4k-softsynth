ASM = nasm
CC = g++

#-O1 -ffast-math -fno-inline -fmove-all-movables -fshort-double\
#	-fexpensive-optimizations -fpeephole2 -Wall -fforce-mem\
#	`sdl-config --cflags` -I/usr/local/include

# Choose one of the following targets
# At present time, only linux and cygwin are verified to work
#TARGET=win32
#TARGET=cygwin
#TARGET=linux64
TARGET=linux32

# FULL = FULLSCREEN for fullscreen mode, something else for window
#FULL=FULLSCREEN
FULL=WINDOW

# Set to DEBUG or RELEASE
#DEB = RELEASE
DEB = DEBUG

# Flags based on DEBUG/RELEASE
CC_DEBUG_FLAGS_DEBUG=-g -DDEBUG
CC_DEBUG_FLAGS_RELEASE=-s
ASM_DEBUG_FLAGS_DEBUG=-g -DDEBUG
ASM_DEBUG_FLAGS_RELEASE=

# Comment this out to use OS loading of dlls
#MANUAL_DLL_LOAD=doit

# Win32
#ASMTARGET_win32=-f win32 -DBIT32
#OBJ_POSTFIX_win32=obj
#LINKOPT_INTRO_win32=
#LINKOPT_EDITOR_win32= -lSDL -GL
#ASMOPT_win32=-DPREFIX -DDLL -DRET
#CC_FLAGS_win32=

# 32-bit Cygwin
ASMTARGET_cygwin=-felf32 -gdwarf -s -DBIT32
OBJ_POSTFIX_cygwin=o
LINKOPT_INTRO_cygwin=-lc -m32
LINKOPT_EDITOR_cygwin=-m32 -lSDL -luGL
ASMOPT_cygwin=-DPREFIX -DSO -DRET
PACK_cygwin=./pack.sh
CC_FLAGS_cygwin=-m32
EXEC_SUFFIX_cygwin=.exe
STRIP_cygwin=strip
REMOVE_ELF_HEADER_cygwin = echo

# 32-bit Linux
ASMTARGET_linux32=-felf32 -gdwarf -s -DBIT32
OBJ_POSTFIX_linux32=o
LINKOPT_INTRO_linux32=-lc -m32 -nostdlib
LINKOPT_EDITOR_linux32=-m32 -lGL -lSDL
ASMOPT_linux32=-DSO
PACK_linux32=../scripts/pack.sh
CC_FLAGS_linux32=-m32
STRIP_linux32=../../ELFkickers/sstrip/sstrip -z
REMOVE_ELF_HEADER_linux32 = ../scripts/fix_elf_header.py

# 64-bit Linux
#ASMTARGET_linux64=-felf64 -gdwarf -s -DBIT64
#OBJ_POSTFIX_linux64=o
#LINKOPT_INTRO_linux64=-lc -m64 -nostdlib
#LINKOPT_EDITOR_linux64=-lSDL -lGL
#ASMOPT_linux64=-DSO
#PACK_linux64=../scripts/pack.sh
#CC_FLAGS_linux64=

# Set generic flags
ASMTARGET=$(ASMTARGET_$(TARGET))
OBJ_POSTFIX=$(OBJ_POSTFIX_$(TARGET))
LINKOPT_INTRO=$(LINKOPT_INTRO_$(TARGET))
LINKOPT_EDITOR=$(LINKOPT_EDITOR_$(TARGET))
ASMOPT=$(ASMOPT_$(TARGET))
PACK=$(PACK_$(TARGET))
STRIP=$(STRIP_$(TARGET))
REMOVE_ELF_HEADER=$(REMOVE_ELF_HEADER_$(TARGET))
ASM_FLAGS=$(ASM_DEBUG_FLAGS_$(DEB))
CC_FLAGS=$(CC_DEBUG_FLAGS_$(DEB)) $(CC_FLAGS_$(TARGET))


