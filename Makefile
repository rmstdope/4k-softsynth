ASM = nasm
CC = g++

INC_DIRS=-IglTexFont-r6

#-O1 -ffast-math -fno-inline -fmove-all-movables -fshort-double\
#	-fexpensive-optimizations -fpeephole2 -Wall -fforce-mem\
#	`sdl-config --cflags` -I/usr/local/include

# Choose one of the following targets
# At present time, only linux is verified to work
#TARGET=win32
#TARGET=cygwin
#TARGET=linux64
TARGET=linux32

# FULL = FULLSCREEN for fullscreen mode, something else for window
FULL=WINDOW
# Set to DEBUG or RELEASE
#DEB = RELEASE
DEB = DEBUG
# x87 or x86?
#SOFTSYNTH_VER=_x87
SOFTSYNTH_VER=_x86
# Comment this out to use OS loading of dlls
#MANUAL_DLL_LOAD=doit
SOFTSYNTH=softsynth$(SOFTSYNTH_VER).asm

ASMTARGET_win32=-f win32 -DBIT32
OBJ_POSTFIX_win32=obj
LINKOPT_INTRO_win32=
LINKOPT_AED_win32= -lSDL -GL
ASMOPT_win32=-DPREFIX -DDLL -DRET
CC_FLAGS_win32=

ASMTARGET_cygwin=-f gnuwin32 -DBIT32
OBJ_POSTFIX_cygwin=o
LINKOPT_INTRO_cygwin=#-nostdlib
LINKOPT_AED_cygwin= -lSDL -lopengl32
ASMOPT_cygwin=-DPREFIX -DDLL -DRET
CC_FLAGS_cygwin=

ASMTARGET_linux32=-felf32 -gdwarf -s -DBIT32
OBJ_POSTFIX_linux32=o
LINKOPT_INTRO_linux32=-lc -m32 -nostdlib
LINKOPT_AED_linux32=-m32 -lGL -lSDL
ASMOPT_linux32=-DSO
PACK_linux32=./pack.sh
CC_FLAGS_linux32=-m32

ASMTARGET_linux64=-felf64 -gdwarf -s -DBIT64
OBJ_POSTFIX_linux64=o
LINKOPT_INTRO_linux64=-lc -m64 -nostdlib
LINKOPT_AED_linux64=-lSDL -lGL
ASMOPT_linux64=-DSO
PACK_linux64=./pack.sh
CC_FLAGS_linux64=

ASMTARGET=$(ASMTARGET_$(TARGET))
OBJ_POSTFIX=$(OBJ_POSTFIX_$(TARGET))
LINKOPT_INTRO=$(LINKOPT_INTRO_$(TARGET))
LINKOPT_AED=$(LINKOPT_AED_$(TARGET))
ASMOPT=$(ASMOPT_$(TARGET))
PACK=$(PACK_$(TARGET))

INTRO_OBJ=main.$(OBJ_POSTFIX) softsynth.$(OBJ_POSTFIX)

ifdef MANUAL_DLL_LOAD
	INTRO_OBJ+= dynamic_library.$(OBJ_POSTFIX)
else
	LINKOPT_INTRO+=-dynamic -lSDL
endif

AED_OBJ=	AudioEditor.$(OBJ_POSTFIX)				\
		EditBase.$(OBJ_POSTFIX) PatternEdit.$(OBJ_POSTFIX)	\
		TrackEdit.$(OBJ_POSTFIX) InstrumentEdit.$(OBJ_POSTFIX)	\
		aed_main.$(OBJ_POSTFIX) softsynth.$(OBJ_POSTFIX) 	\
		softsynth_wrapper.$(OBJ_POSTFIX)			\
		glTexFont.$(OBJ_POSTFIX) glTexFontTGA.$(OBJ_POSTFIX)	\
		glTexFontColor.$(OBJ_POSTFIX)

TEST_OBJ=	Test.$(OBJ_POSTFIX)

UNPACKED = intro
NAME = 4k
AED = aed
TEST = test
STRIP = ../../ELFkickers/sstrip/sstrip -z
REMOVE_ELF_HEADER = ./remove_elf_header.py

ASM_DEBUG_FLAGS_DEBUG=-g -DDEBUG
ASM_DEBUG_FLAGS_RELEASE=

CC_DEBUG_FLAGS_DEBUG=-g -DDEBUG -m32
CC_DEBUG_FLAGS_RELEASE=-s -m32

ASM_FLAGS=$(ASM_DEBUG_FLAGS_$(DEB))
CC_FLAGS=$(CC_DEBUG_FLAGS_$(DEB)) $(CC_FLAGS_$(TARGET))

all: $(UNPACKED) $(AED)

$(NAME): $(UNPACKED) Makefile
	$(PACK) $(UNPACKED) $@

$(UNPACKED): $(INTRO_OBJ) Makefile
	$(CC) $(CC_FLAGS) -o $@ $(INTRO_OBJ) $(LINKOPT_INTRO)
#	$(STRIP) $@
#	$(REMOVE_ELF_HEADER) $@

$(AED): $(AED_OBJ) Makefile
	$(CC) $(CC_FLAGS) -o $@ $(AED_OBJ) $(LINKOPT_AED)

$(TEST): $(TEST_OBJ) Makefile
	$(CC) $(CC_FLAGS) -o $@ $(TEST_OBJ) $(LINKOPT_AED)

main.$(OBJ_POSTFIX): main.asm debug.inc common.inc Makefile
	$(ASM) $(ASM_FLAGS) $(ASMTARGET) -D$(FULL) -D$(DEB) $(ASMOPT) $<

dynamic_library.$(OBJ_POSTFIX): dynamic_library.asm debug.inc Makefile
	$(ASM) $(ASM_FLAGS) $(ASMTARGET)  -D$(DEB) $(ASMOPT) $<

softsynth.$(OBJ_POSTFIX): $(SOFTSYNTH) debug.inc Makefile
	$(ASM) $(ASM_FLAGS) $(ASMTARGET) $(ASMOPT) $(SOFTSYNTH) -o softsynth.$(OBJ_POSTFIX)

softsynth_wrapper.$(OBJ_POSTFIX): softsynth_wrapper.asm debug.inc Makefile
	$(ASM) $(ASM_FLAGS) $(ASMTARGET) $(ASMOPT) $<

aed_main.$(OBJ_POSTFIX): aed_main.cc Makefile
	$(CC) $(INC_DIRS) $(CC_FLAGS) $(ASMOPT) -c $<

%.$(OBJ_POSTFIX): %.c Makefile
	$(CC) $(INC_DIRS) $(CC_FLAGS) -c $<

%.$(OBJ_POSTFIX): %.cc %.hh Makefile
	$(CC) $(INC_DIRS) $(CC_FLAGS) -c $<

glTexFont.$(OBJ_POSTFIX): glTexFont-r6/glTexFont.c Makefile
	$(CC) $(INC_DIRS) $(CC_FLAGS) -c $<

glTexFontTGA.$(OBJ_POSTFIX): glTexFont-r6/glTexFontTGA.c Makefile
	$(CC) $(INC_DIRS) $(CC_FLAGS) -c $<

glTexFontColor.$(OBJ_POSTFIX): glTexFont-r6/glTexFontColor.c Makefile
	$(CC) $(INC_DIRS) $(CC_FLAGS) -c $<

clean:
	rm -f *.$(OBJ_POSTFIX) $(UNPACKED) $(UNPACKED).exe $(NAME) core *~ $(AED) $(AED).exe

