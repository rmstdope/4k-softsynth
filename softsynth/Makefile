include ../common.mk

#INC_DIRS=-IglTexFont-r6

SONG_OBJ=bin/song.$(OBJ_POSTFIX)
SOFTSYNTH_OBJ=bin/softsynth.$(OBJ_POSTFIX)
PLAYER_OBJ=bin/main.$(OBJ_POSTFIX) $(SOFTSYNTH_OBJ) $(SONG_OBJ)

# Automatically discover test files
TEST_SOURCES := $(wildcard test/$(ARCH)/test_*.cpp)
TEST_NAMES := $(patsubst test/$(ARCH)/test_%.cpp,%,$(TEST_SOURCES))
TEST_EXECUTABLES := $(patsubst %,bin/test_%$(EXEC_SUFFIX),$(TEST_NAMES))
TEST_OBJECTS := $(patsubst %,bin/test_%.$(OBJ_POSTFIX),$(TEST_NAMES))

# Common test dependencies
COMMON_TEST_OBJ=bin/unity.$(OBJ_POSTFIX) bin/test_common.$(OBJ_POSTFIX) $(SOFTSYNTH_OBJ)

PLAYER=bin/softsynth-packed
UNPACKED_PLAYER=bin/softsynth$(EXEC_SUFFIX)

all: $(TEST_EXECUTABLES) $(PLAYER)

# Help target
help:
	@echo "Available targets:"
	@echo "  all          - Build all test executables and player"
	@echo "  tests        - Build all test executables"
	@echo "  run_tests    - Build and run all test executables"
	@echo "  list_tests   - List all discovered test files"
	@echo "  clean        - Remove all build artifacts"
	@echo "  help         - Show this help message"
	@echo ""
	@echo "Individual test targets (automatically discovered):"
	@for test in $(TEST_NAMES); do \
		echo "  bin/test_$$test     - Build test_$$test executable"; \
		echo "  run_test_$$test     - Build and run test_$$test"; \
	done

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

# Generic pattern rule for test object files
bin/test_%.$(OBJ_POSTFIX): test/$(ARCH)/test_%.cpp Makefile | bin/
	$(CXX) $(INC_DIRS) $(CC_FLAGS) $(INCLUDE_PATH) -c  -o $@ $<

tests: $(TEST_EXECUTABLES)

# List all discovered tests
list_tests:
	@echo "Discovered test files:"
	@for test in $(TEST_NAMES); do \
		echo "  test_$$test"; \
	done
	@echo ""
	@echo "Test executables:"
	@for test in $(TEST_EXECUTABLES); do \
		echo "  $$test"; \
	done

run_tests: $(TEST_EXECUTABLES)
	@echo "Running all tests..."
	@for test in $(TEST_EXECUTABLES); do \
		echo "Running $$test..."; \
		$$test; \
	done

# Pattern rule to run individual tests by name (e.g., make run_test_envelope)
run_test_%: bin/test_%$(EXEC_SUFFIX)
	@echo "Running test_$*..."
	@$<

bin/unity.$(OBJ_POSTFIX): test/unity.c Makefile | bin/
	$(CC) $(INC_DIRS) $(CC_FLAGS) $(INCLUDE_PATH) -c  -o $@ $<

bin/test_common.$(OBJ_POSTFIX): test/test_common.c Makefile | bin/
	$(CC) $(INC_DIRS) $(CC_FLAGS) $(INCLUDE_PATH) -c  -o $@ $<

# Generic pattern rule for test executables
bin/test_%$(EXEC_SUFFIX): bin/test_%.$(OBJ_POSTFIX) $(COMMON_TEST_OBJ) Makefile | bin/
	$(CC) $(LINK_FLAGS) $(OGL_LIBRARY_LINK) $(SDL_LIBRARY_LINK) $< $(COMMON_TEST_OBJ) -o $@

# Prevent Make from deleting object files as intermediate files (needed for debugging)
.PRECIOUS: $(TEST_OBJECTS)

clean:
	rm -rf bin/* core *~

