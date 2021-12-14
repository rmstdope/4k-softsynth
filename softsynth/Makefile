include ../common.mk

INC_DIRS=-IglTexFont-r6

INTRO_OBJ=main.$(OBJ_POSTFIX) softsynth.$(OBJ_POSTFIX)

ifdef MANUAL_DLL_LOAD
	INTRO_OBJ+= dynamic_library.$(OBJ_POSTFIX)
else
	LINKOPT_INTRO+=-dynamic -lSDL
endif

NAME = softsynth-packed
UNPACKED = softsynth$(EXEC_SUFFIX_$(TARGET))

all: $(NAME) softsynth_wrapper.$(OBJ_POSTFIX)

$(NAME): $(UNPACKED) Makefile
	$(STRIP) $(UNPACKED)
	$(REMOVE_ELF_HEADER) $(UNPACKED)
	$(PACK) $(UNPACKED) $@

$(UNPACKED): $(INTRO_OBJ) Makefile
	$(CC) $(CC_FLAGS) -o $@ $(INTRO_OBJ) $(LINKOPT_INTRO)

$(AED): $(AED_OBJ) Makefile
	$(CC) $(CC_FLAGS) -o $@ $(AED_OBJ) $(LINKOPT_AED)

$(TEST): $(TEST_OBJ) Makefile
	$(CC) $(CC_FLAGS) -o $@ $(TEST_OBJ) $(LINKOPT_AED)

main.$(OBJ_POSTFIX): main.asm debug.inc common.inc Makefile
	$(ASM) $(ASM_FLAGS) $(ASMTARGET) -D$(FULL) -D$(DEB) $(ASMOPT) $<

dynamic_library.$(OBJ_POSTFIX): dynamic_library.asm debug.inc Makefile
	$(ASM) $(ASM_FLAGS) $(ASMTARGET)  -D$(DEB) $(ASMOPT) $<

softsynth.$(OBJ_POSTFIX): softsynth.asm debug.inc Makefile
	$(ASM) $(ASM_FLAGS) $(ASMTARGET) $(ASMOPT) $<

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

