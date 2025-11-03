#include "test_common.h"

uint8_t instrument_instructions[6] = {ENVELOPE_ID, OSCILLATOR_ID, OUTPUT_ID, INSTRUMENT_END, ENVELOPE_ID, INSTRUMENT_END};
uint8_t instrument_parameters[19] =
    {
        72, 96, 96, 88, 128,
        0, 32, 64, 64, 128, 32, 32, 32,
        64,
        72, 96, 96, 88, 128};
uint8_t instrument_patterns[PATTERNS_PER_INSTRUMENT * MAX_NUM_INSTRUMENTS] =
    {
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1,
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2,
        2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3,
        3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 1, 2, 3, 4};

uint8_t pattern_array[NOTES_PER_PATTERN * 19] =
    {
        60, HLD, 62, HLD, 64, 0, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD,
        61, HLD, 63, HLD, 65, 0, 66, HLD, 67, HLD, 70, HLD, 72, HLD, 73, HLD,
        62, HLD, 64, HLD, 65, 0, 66, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD};

float vm_stack[16];
float *x8_ptr;
