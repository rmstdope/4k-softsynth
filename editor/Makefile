include ../common.mk

INC_DIRS=-I../glTexFont-r6 -I../softsynth -I/opt/homebrew/Cellar/sdl2/2.32.10/include/

EDITOR_OBJ = bin/AudioEditor.$(OBJ_POSTFIX)				\
		bin/EditBase.$(OBJ_POSTFIX) bin/PatternEdit.$(OBJ_POSTFIX)	\
		bin/TrackEdit.$(OBJ_POSTFIX) bin/InstrumentEdit.$(OBJ_POSTFIX)	\
		bin/aed_main.$(OBJ_POSTFIX) ../softsynth/bin/softsynth.$(OBJ_POSTFIX) \
		../softsynth/bin/softsynth_wrapper.$(OBJ_POSTFIX)		\
		bin/glTexFont.$(OBJ_POSTFIX) bin/glTexFontTGA.$(OBJ_POSTFIX)	\
		bin/glTexFontColor.$(OBJ_POSTFIX)

TEST_OBJ = bin/Test.$(OBJ_POSTFIX)

EDITOR = bin/editor
TEST = bin/test

all: $(EDITOR) $(TEST)

bin:
	mkdir -p bin

precompile: bin Makefile ../common.mk
	

softsynth:
	$(MAKE) -C ../softsynth bin/softsynth.$(OBJ_POSTFIX) bin/softsynth_wrapper.$(OBJ_POSTFIX)

$(EDITOR): softsynth $(EDITOR_OBJ) precompile
	$(CC) $(CC_FLAGS) -o $@ $(EDITOR_OBJ) $(LINKOPT_EDITOR)

$(TEST): $(TEST_OBJ) precompile
	$(CC) $(CC_FLAGS) -o $@ $(TEST_OBJ) $(LINKOPT_EDITOR)

bin/%.$(OBJ_POSTFIX): %.cc %.hh precompile
	$(CC) $(INC_DIRS) $(CC_FLAGS) -c -o $@ $<

bin/%.$(OBJ_POSTFIX): %.cc precompile
	$(CC) $(INC_DIRS) $(CC_FLAGS) -c -o $@ $<

bin/glTexFont.$(OBJ_POSTFIX): ../glTexFont-r6/glTexFont.c precompile
	$(CC) $(INC_DIRS) $(CC_FLAGS) -c -o $@ $<

bin/glTexFontTGA.$(OBJ_POSTFIX): ../glTexFont-r6/glTexFontTGA.c precompile
	$(CC) $(INC_DIRS) $(CC_FLAGS) -c -o $@ $<

bin/glTexFontColor.$(OBJ_POSTFIX): ../glTexFont-r6/glTexFontColor.c precompile
	$(CC) $(INC_DIRS) $(CC_FLAGS) -c -o $@ $<

clean:
	rm -f *.$(OBJ_POSTFIX) core *~ $(TEST) $(EDITOR) $(EDITOR).exe

