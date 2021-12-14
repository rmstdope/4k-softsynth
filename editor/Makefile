include ../common.mk

INC_DIRS=-I../glTexFont-r6 -I../softsynth

EDITOR_OBJ=	AudioEditor.$(OBJ_POSTFIX)				\
		EditBase.$(OBJ_POSTFIX) PatternEdit.$(OBJ_POSTFIX)	\
		TrackEdit.$(OBJ_POSTFIX) InstrumentEdit.$(OBJ_POSTFIX)	\
		aed_main.$(OBJ_POSTFIX) ../softsynth/softsynth.$(OBJ_POSTFIX) \
		../softsynth/softsynth_wrapper.$(OBJ_POSTFIX)		\
		glTexFont.$(OBJ_POSTFIX) glTexFontTGA.$(OBJ_POSTFIX)	\
		glTexFontColor.$(OBJ_POSTFIX)

TEST_OBJ=	Test.$(OBJ_POSTFIX)

EDITOR = editor
TEST = test

all: $(EDITOR) $(TEST)

softsynth:
	$(MAKE) -C ../softsynth

$(EDITOR): softsynth $(EDITOR_OBJ) Makefile
	$(CC) $(CC_FLAGS) -o $@ $(EDITOR_OBJ) $(LINKOPT_EDITOR)

$(TEST): $(TEST_OBJ) Makefile
	$(CC) $(CC_FLAGS) -o $@ $(TEST_OBJ) $(LINKOPT_EDITOR)

%.$(OBJ_POSTFIX): %.cc %.hh Makefile
	$(CC) $(INC_DIRS) $(CC_FLAGS) -c $<

%.$(OBJ_POSTFIX): %.cc Makefile
	$(CC) $(INC_DIRS) $(CC_FLAGS) -c $<

glTexFont.$(OBJ_POSTFIX): ../glTexFont-r6/glTexFont.c Makefile
	$(CC) $(INC_DIRS) $(CC_FLAGS) -c $<

glTexFontTGA.$(OBJ_POSTFIX): ../glTexFont-r6/glTexFontTGA.c Makefile
	$(CC) $(INC_DIRS) $(CC_FLAGS) -c $<

glTexFontColor.$(OBJ_POSTFIX): ../glTexFont-r6/glTexFontColor.c Makefile
	$(CC) $(INC_DIRS) $(CC_FLAGS) -c $<

clean:
	rm -f *.$(OBJ_POSTFIX) core *~ $(TEST) $(EDITOR) $(EDITOR).exe

