#ifndef TEST_COMMON_H
#define TEST_COMMON_H

#include <stdint.h>
#include "../include/defines.h"

#define INSTRUMENT_NOTE_OFFSET 0
#define INSTRUMENT_RELEASE_OFFSET 1
#define INSTRUMENT_OUTPUT_OFFSET 2
#define INSTRUMENT_WS_OFFSET 3

#define INSTRUMENT_SIZE (3 + MAX_COMMANDS * MAX_COMMAND_PARAMS)
#define SYNTH_SIZE INSTRUMENT_SIZE *MAX_NUM_INSTRUMENTS

// Global test data and symbols required by softsynth.o
extern uint8_t instrument_instructions[6];
extern uint8_t instrument_parameters[19];
extern uint8_t instrument_patterns[PATTERNS_PER_INSTRUMENT * MAX_NUM_INSTRUMENTS];
extern uint8_t pattern_array[NOTES_PER_PATTERN * 19];
extern float vm_stack[16];
extern float *x8_ptr;

#endif // TEST_COMMON_H