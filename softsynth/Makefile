include ../common.mk

INC_DIRS=-IglTexFont-r6

INTRO_OBJ=bin/main.$(OBJ_POSTFIX) bin/softsynth.$(OBJ_POSTFIX)

ifdef MANUAL_DLL_LOAD
	INTRO_OBJ+= dynamic_library.$(OBJ_POSTFIX)
else
	LINKOPT_INTRO+=-dynamic -lSDL
endif

NAME = softsynth-packed
UNPACKED = softsynth$(EXEC_SUFFIX_$(TARGET))

all: $(NAME) bin/softsynth_wrapper.$(OBJ_POSTFIX)

$(NAME): $(UNPACKED) Makefile
	$(STRIP) $(UNPACKED)
	$(REMOVE_ELF_HEADER) $(UNPACKED)
	$(PACK) $(UNPACKED) $@

$(UNPACKED): $(INTRO_OBJ) Makefile
	$(CC) $(CC_FLAGS) -o $@ $(INTRO_OBJ) $(LINKOPT_INTRO)

bin/main.$(OBJ_POSTFIX): main.S debug.inc common.inc Makefile
	$(ASM) $(ASM_FLAGS) $(ASMTARGET) -D$(FULL) -D$(DEB) $(ASMOPT) -o $@ $<

bin/dynamic_library.$(OBJ_POSTFIX): dynamic_library.S debug.inc Makefile
	$(ASM) $(ASM_FLAGS) $(ASMTARGET)  -D$(DEB) $(ASMOPT) -o $@ $<

bin/softsynth.$(OBJ_POSTFIX): softsynth_$(ARCH).S debug.inc Makefile
	$(ASM) $(ASM_FLAGS) $(ASMTARGET) $(ASMOPT) -o $@ $<

bin/softsynth_wrapper.$(OBJ_POSTFIX): softsynth_wrapper_$(ARCH).S debug.inc Makefile
	$(ASM) $(ASM_FLAGS) $(ASMTARGET) $(ASMOPT) -o $@ $<

bin/%.$(OBJ_POSTFIX): %.c Makefile
	$(CC) $(INC_DIRS) $(CC_FLAGS) -c  -o $@ $<

bin/%.$(OBJ_POSTFIX): %.cc %.hh Makefile
	$(CC) $(INC_DIRS) $(CC_FLAGS) -c -o $@ $<

bin/glTexFont.$(OBJ_POSTFIX): glTexFont-r6/glTexFont.c Makefile
	$(CC) $(INC_DIRS) $(CC_FLAGS) -c -o $@ $<

bin/glTexFontTGA.$(OBJ_POSTFIX): glTexFont-r6/glTexFontTGA.c Makefile
	$(CC) $(INC_DIRS) $(CC_FLAGS) -c -o $@ $<

bin/glTexFontColor.$(OBJ_POSTFIX): glTexFont-r6/glTexFontColor.c Makefile
	$(CC) $(INC_DIRS) $(CC_FLAGS) -c -o $@ $<

clean:
	rm -f *.$(OBJ_POSTFIX) $(UNPACKED) $(UNPACKED).exe $(NAME) core *~ $(AED) $(AED).exe

