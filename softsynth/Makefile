include ../common.mk

#INC_DIRS=-IglTexFont-r6

SONG_OBJ=bin/song.$(OBJ_POSTFIX)
SOFTSYNTH_OBJ=bin/softsynth.$(OBJ_POSTFIX)
PLAYER_OBJ=bin/main.$(OBJ_POSTFIX) $(SOFTSYNTH_OBJ) $(SONG_OBJ)
TESTS_OBJ=bin/test_softsynth.$(OBJ_POSTFIX) bin/unity.$(OBJ_POSTFIX) $(SOFTSYNTH_OBJ)

PLAYER=bin/softsynth-packed
UNPACKED_PLAYER=bin/softsynth$(EXEC_SUFFIX)
TESTS=bin/test_softsynth$(EXEC_SUFFIX)

all: $(TESTS) $(PLAYER)

bin/:
	mkdir -p bin

$(PLAYER): $(UNPACKED_PLAYER) Makefile | bin/
ifeq ($(VARIANT),RELEASE)
	$(STRIP) $(UNPACKED_PLAYER)
	$(REMOVE_ELF_HEADER) $(UNPACKED_PLAYER)
endif
	$(PACK) $(UNPACKED_PLAYER) $@

$(UNPACKED_PLAYER): $(PLAYER_OBJ) Makefile | bin/
	$(CXX) $(LINK_FLAGS) $(OGL_LIBRARY_LINK) $(SDL_LIBRARY_LINK) $(PLAYER_OBJ) -o $@

bin/main.$(OBJ_POSTFIX): src/main.cpp Makefile | bin/
	$(CXX) $(INC_DIRS) $(CC_FLAGS) $(INCLUDE_PATH) -c  -o $@ $<

bin/softsynth.$(OBJ_POSTFIX): src/$(ARCH)/softsynth.asm src/$(ARCH)/common.asm include/defines.h Makefile | bin/
	$(ASM) $(ASM_FLAGS) $(ASM_FLAGS) -o $@ $<

bin/song.$(OBJ_POSTFIX): src/$(ARCH)/song.asm src/$(ARCH)/common.asm include/defines.h Makefile | bin/
	$(ASM) $(ASM_FLAGS) $(ASM_FLAGS) -o $@ $<

bin/test_softsynth.$(OBJ_POSTFIX): test/$(ARCH)/test_softsynth.cpp Makefile | bin/
	$(CXX) $(INC_DIRS) $(CC_FLAGS) $(INCLUDE_PATH) -c  -o $@ $<

run_tests: $(TESTS)
	bin/test_softsynth

bin/unity.$(OBJ_POSTFIX): test/unity.c Makefile | bin/
	$(CC) $(INC_DIRS) $(CC_FLAGS) $(INCLUDE_PATH) -c  -o $@ $<

$(TESTS): $(TESTS_OBJ) Makefile | bin/
	$(CC) $(LINK_FLAGS) $(OGL_LIBRARY_LINK) $(SDL_LIBRARY_LINK) $(TESTS_OBJ) -o $@

clean:
	rm -f bin/* core *~

