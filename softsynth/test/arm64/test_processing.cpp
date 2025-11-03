#include "../unity.h"
#include "../../include/defines.h"
#include "../../include/softsynth.h"
#include "../test_common.h"
#include <string.h>
#include <cmath>
unsigned char instruction_params[5] = {0, 96, 96, 88, 128};
uint32_t instrument_data[SYNTH_SIZE];

// Unity requires these functions to be defined
void setUp(void)
{
    // Set up code to run before each test
    // Leave empty if not needed
}

void tearDown(void)
{
    // Clean up code to run after each test
    // Leave empty if not needed
}

void test_transform_values(void)
{
    unsigned char test_data[4] = {0, 10, 100, 255};
    unsigned char *x4_ptr;
    // Set up registers
    asm volatile(
        "mov     x4, %0\n"
        "mov     x17, #4\n"
        :
        : "r"(test_data)
        : "x4", "x17");
    transform_values();
    // Retrieve x4 register value
    asm volatile("mov %0, x4" : "=r"(x4_ptr));

    // Have all four values been transformed?
    TEST_ASSERT_EQUAL_FLOAT(0 / 128.0f, transformed_parameters[0]);
    TEST_ASSERT_EQUAL_FLOAT(10 / 128.0f, transformed_parameters[1]);
    TEST_ASSERT_EQUAL_FLOAT(100 / 128.0f, transformed_parameters[2]);
    TEST_ASSERT_EQUAL_FLOAT(255 / 128.0f, transformed_parameters[3]);
    // Are we pointing to the next value?
    TEST_ASSERT_EQUAL_PTR(&test_data[4], x4_ptr);
}

unsigned char inum = 0;
unsigned char instructions[4] = {1, 2, 3, 0};
unsigned char icallers[3] = {0, 0, 0};
uint32_t *iargs[3];

void instruction1(void)
{
    // Preserve all registers x0-x17 using inline assembly
    asm volatile(
        "stp x0, x1, [sp, #-16]!\n"
        "stp x2, x3, [sp, #-16]!\n"
        "stp x4, x5, [sp, #-16]!\n"
        "stp x6, x7, [sp, #-16]!\n"
        "stp x8, x9, [sp, #-16]!\n"
        "stp x10, x11, [sp, #-16]!\n"
        "stp x12, x13, [sp, #-16]!\n"
        "stp x14, x15, [sp, #-16]!\n"
        "stp x16, x17, [sp, #-16]!\n" ::: "memory");

    icallers[inum] = 1;
    asm volatile("mov %0, x7" : "=r"(iargs[inum++]));

    asm volatile(
        "ldp x16, x17, [sp], #16\n"
        "ldp x14, x15, [sp], #16\n"
        "ldp x12, x13, [sp], #16\n"
        "ldp x10, x11, [sp], #16\n"
        "ldp x8, x9, [sp], #16\n"
        "ldp x6, x7, [sp], #16\n"
        "ldp x4, x5, [sp], #16\n"
        "ldp x2, x3, [sp], #16\n"
        "ldp x0, x1, [sp], #16\n" ::: "memory");
}

void instruction2(void)
{
    // Preserve all registers x0-x17 using inline assembly
    asm volatile(
        "stp x0, x1, [sp, #-16]!\n"
        "stp x2, x3, [sp, #-16]!\n"
        "stp x4, x5, [sp, #-16]!\n"
        "stp x6, x7, [sp, #-16]!\n"
        "stp x8, x9, [sp, #-16]!\n"
        "stp x10, x11, [sp, #-16]!\n"
        "stp x12, x13, [sp, #-16]!\n"
        "stp x14, x15, [sp, #-16]!\n"
        "stp x16, x17, [sp, #-16]!\n" ::: "memory");

    icallers[inum] = 2;
    asm volatile("mov %0, x7" : "=r"(iargs[inum++]));

    asm volatile(
        "ldp x16, x17, [sp], #16\n"
        "ldp x14, x15, [sp], #16\n"
        "ldp x12, x13, [sp], #16\n"
        "ldp x10, x11, [sp], #16\n"
        "ldp x8, x9, [sp], #16\n"
        "ldp x6, x7, [sp], #16\n"
        "ldp x4, x5, [sp], #16\n"
        "ldp x2, x3, [sp], #16\n"
        "ldp x0, x1, [sp], #16\n" ::: "memory");
}

void instruction3(void)
{
    // Preserve all registers x0-x17 using inline assembly
    asm volatile(
        "stp x0, x1, [sp, #-16]!\n"
        "stp x2, x3, [sp, #-16]!\n"
        "stp x4, x5, [sp, #-16]!\n"
        "stp x6, x7, [sp, #-16]!\n"
        "stp x8, x9, [sp, #-16]!\n"
        "stp x10, x11, [sp, #-16]!\n"
        "stp x12, x13, [sp, #-16]!\n"
        "stp x14, x15, [sp, #-16]!\n"
        "stp x16, x17, [sp, #-16]!\n" ::: "memory");

    icallers[inum] = 3;
    asm volatile("mov %0, x7" : "=r"(iargs[inum++]));

    asm volatile(
        "ldp x16, x17, [sp], #16\n"
        "ldp x14, x15, [sp], #16\n"
        "ldp x12, x13, [sp], #16\n"
        "ldp x10, x11, [sp], #16\n"
        "ldp x8, x9, [sp], #16\n"
        "ldp x6, x7, [sp], #16\n"
        "ldp x4, x5, [sp], #16\n"
        "ldp x2, x3, [sp], #16\n"
        "ldp x0, x1, [sp], #16\n" ::: "memory");
}

void test_process_stack(void)
{
    unsigned char *x7_ptr;
    // Set up lookup table
    instrument_instructions_lookup[1] = instruction1;
    instrument_instructions_lookup[2] = instruction2;
    instrument_instructions_lookup[3] = instruction3;
    // Set up registers
    ///     x5 = instrument data pointer
    ///     x6 = instrument instruction pointer
    asm volatile(
        "mov     x5, %0\n"
        "mov     x6, %1\n" : : "r"(instrument_data),
                               "r"(instructions) : "x5", "x6");
    process_stack();
    TEST_ASSERT_EQUAL_UINT8(3, inum);
    TEST_ASSERT_EQUAL_UINT8_ARRAY(instructions, icallers, 3);
    TEST_ASSERT_EQUAL_PTR(&instrument_data[INSTRUMENT_WS_OFFSET + 16 * 0], iargs[0]);
    TEST_ASSERT_EQUAL_PTR(&instrument_data[INSTRUMENT_WS_OFFSET + 16 * 1], iargs[1]);
    TEST_ASSERT_EQUAL_PTR(&instrument_data[INSTRUMENT_WS_OFFSET + 16 * 2], iargs[2]);
}

void reset_instrument_data(unsigned char val)
{
    memset(instrument_data, val, sizeof(instrument_data));
}

void run_new_instrument_note(uint32_t instrument_num, uint32_t note_num, uint32_t expected_note, bool release = false)
{
    ///     x0 = current note #
    ///     x3 = current instrument #
    ///     x5 = instrument data pointer
    asm volatile(
        "mov     w0, %w0\n"
        "mov     w3, %w1\n"
        "mov     x5, %2\n" :
        : "r"(note_num), "r"(instrument_num), "r"(&instrument_data[instrument_num * INSTRUMENT_SIZE])
        : "x0", "x3", "x5");
    new_instrument_note();
    for (int i = 0; i < MAX_NUM_INSTRUMENTS; i++)
    {
        if (i == instrument_num)
        {
            TEST_ASSERT_EQUAL_UINT32(expected_note, instrument_data[i * INSTRUMENT_SIZE]);
            if (release)
            {
                TEST_ASSERT_NOT_EQUAL_UINT32(0, instrument_data[i * INSTRUMENT_SIZE + INSTRUMENT_RELEASE_OFFSET]);
            }
            else
            {
                TEST_ASSERT_EQUAL_UINT32(0, instrument_data[i * INSTRUMENT_SIZE + INSTRUMENT_RELEASE_OFFSET]);
            }
            TEST_ASSERT_EACH_EQUAL_UINT32(0, &instrument_data[i * INSTRUMENT_SIZE + INSTRUMENT_OUTPUT_OFFSET], INSTRUMENT_SIZE - 2);
        }
        else
        {
            TEST_ASSERT_EACH_EQUAL_UINT32(0xFFFFFFFF, &instrument_data[i * INSTRUMENT_SIZE], INSTRUMENT_SIZE);
        }
    }
}

void test_new_instrument_note(void)
{
    // Strike note 60 on instrument 0
    reset_instrument_data(0xFF);
    run_new_instrument_note(0, 0, 60);
    // Hold
    run_new_instrument_note(0, 1, 60);
    // Release
    run_new_instrument_note(0, 5, 60, true);

    // Strike note 62 on instrument 0, should retrigger
    run_new_instrument_note(0, 2, 62);
    // Hold
    run_new_instrument_note(0, 3, 62);
    // Release
    run_new_instrument_note(0, 5, 62, true);

    // Strike notes on instrument 0
    reset_instrument_data(0xFF);
    run_new_instrument_note(0, NOTES_PER_PATTERN, 61);
    run_new_instrument_note(0, NOTES_PER_PATTERN + 2, 63);

    // Strike notes on instrument 1
    reset_instrument_data(0xFF);
    run_new_instrument_note(1, 0, 61);
    run_new_instrument_note(1, 2, 63);
    run_new_instrument_note(1, NOTES_PER_PATTERN, 62);
    run_new_instrument_note(1, NOTES_PER_PATTERN + 2, 64);
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_transform_values);
    RUN_TEST(test_process_stack);
    RUN_TEST(test_new_instrument_note);
    return UNITY_END();
}