#include "../unity.h"
#include "../../include/defines.h"
#include "../../include/softsynth.h"
#include <string.h>

#define INSTRUMENT_SIZE (3 + MAX_COMMANDS * MAX_COMMAND_PARAMS)
#define SYNTH_SIZE INSTRUMENT_SIZE *MAX_NUM_INSTRUMENTS

uint8_t instrument_instructions[4] = {ENVELOPE_ID, OSCILLATOR_ID, OSCILLATOR_ID, INSTRUMENT_END};
uint8_t instrument_parameters[16] =
    {
        72, 96, 96, 88, 128,
        0, 32, 64, 64, 128};
uint8_t instrument_patterns[PATTERNS_PER_INSTRUMENT * MAX_NUM_INSTRUMENTS] =
    {
        0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15,
        1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
        2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17,
        3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18};

uint8_t pattern_array[NOTES_PER_PATTERN * 19] =
    {
        60, HLD, 62, HLD, 64, 0, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        61, HLD, 63, HLD, 65, 0, 66, HLD, 67, HLD, 70, HLD, 72, HLD, 73, HLD, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        62, HLD, 64, HLD, 65, 0, 66, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        60, HLD, 62, HLD, 64, HLD, 65, HLD, 67, HLD, 69, HLD, 71, HLD, 72, HLD, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
float vm_stack[16];
float *x8_ptr;
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

void setup_envelope_function(uint32_t current_note, bool is_released = false, unsigned char attack = 0, unsigned char decay = 0, unsigned char sustain = 0, unsigned char release = 0, unsigned char gain = 128)
{
    instruction_params[0] = attack;
    instruction_params[1] = decay;
    instruction_params[2] = sustain;
    instruction_params[3] = release;
    instruction_params[4] = gain;
    memset(instrument_data, 0, sizeof(instrument_data));
    instrument_data[0] = current_note;        // Current note
    instrument_data[1] = is_released ? 1 : 0; // Release (1 if true, 0 if false)
}

void run_envelope_function()
{
    for (int i = 0; i < 16; i++)
        vm_stack[i] = -1.0f;
    // Set up registers
    ///     x4 = instrument instruction parameters pointer
    ///     x5 = instrument data pointer
    ///     x7 = current instrument instruction workspace pointer
    ///     x8 = VM stack data pointer
    asm volatile(
        "mov     x4, %0\n"
        "mov     x5, %1\n"
        "mov     x7, %2\n"
        "mov     x8, %3\n"
        :
        : "r"(instruction_params), "r"(instrument_data), "r"(&instrument_data[3]), "r"(vm_stack)
        : "x4", "x5", "x7", "x8");
    envelope_function();
    asm volatile("mov %0, x8" : "=r"(x8_ptr));
}

void test_envelope_function_no_note(void)
{
    setup_envelope_function(0);
    run_envelope_function();
    TEST_ASSERT_EQUAL_FLOAT(0, vm_stack[0]);
    // Are we pointing to the next value?
    TEST_ASSERT_EQUAL_PTR(&vm_stack[1], x8_ptr);
}

void test_envelope_function_attack_starts(void)
{
    unsigned char attacks[8] = {1, 2, 4, 8, 16, 32, 64, 100};
    for (int i = 0; i < 8; i++)
    {
        setup_envelope_function(1, false, attacks[i]);
        run_envelope_function();
        float percent = abs(pow(2, -24 * attacks[i] / 128.0f) - vm_stack[0]) / vm_stack[0];
        TEST_ASSERT_LESS_THAN_FLOAT(1.0f, percent);
        // Are we pointing to the next value?
        TEST_ASSERT_EQUAL_PTR(&vm_stack[1], x8_ptr);
    }
}

void test_envelope_function_gain(void)
{
    setup_envelope_function(1, false, 0, 0, 128, 0, 128);
    run_envelope_function();
    TEST_ASSERT_EQUAL_FLOAT(1.0f, vm_stack[0]);

    setup_envelope_function(1, false, 0, 0, 128, 0, 64);
    run_envelope_function();
    TEST_ASSERT_EQUAL_FLOAT(0.5f, vm_stack[0]);

    setup_envelope_function(1, false, 0, 0, 128, 0, 32);
    run_envelope_function();
    TEST_ASSERT_EQUAL_FLOAT(0.25f, vm_stack[0]);

    // Now test with GAIN_MOD
    setup_envelope_function(1, false, 0, 0, 128, 0, 128);
    ((float *)instrument_data)[5] = 1.0f; // GAIN_MOD
    run_envelope_function();
    TEST_ASSERT_EQUAL_FLOAT(2.0f, vm_stack[0]);

    setup_envelope_function(1, false, 0, 0, 128, 0, 64);
    ((float *)instrument_data)[5] = 1.0f; // GAIN_MOD
    run_envelope_function();
    TEST_ASSERT_EQUAL_FLOAT(1.5f, vm_stack[0]);

    setup_envelope_function(1, false, 0, 0, 128, 0, 32);
    ((float *)instrument_data)[5] = 0.25f; // GAIN_MOD
    run_envelope_function();
    TEST_ASSERT_EQUAL_FLOAT(0.5f, vm_stack[0]);
}

void test_envelope_function_adsr_run(void)
{
    setup_envelope_function(1, false, 64, 100, 64, 30);
    /// ATTACK
    run_envelope_function();
    float k = vm_stack[0];
    float val = vm_stack[0];
    while (val < 1.0f)
    {
        // State should still be attack
        TEST_ASSERT_EQUAL_UINT32(0, instrument_data[3]);
        run_envelope_function();
        val = fmin(val + k, 1.0f);
        TEST_ASSERT_EQUAL_FLOAT(val, vm_stack[0]);
    }
    /// DECAY
    // State should now be decay
    TEST_ASSERT_EQUAL_UINT32(1, instrument_data[3]);
    run_envelope_function();
    k = 1.f - vm_stack[0];
    val = vm_stack[0];
    while (val > 0.5f)
    {
        // State should still be decay
        TEST_ASSERT_EQUAL_UINT32(1, instrument_data[3]);
        run_envelope_function();
        val = fmax(val - k, 0.5f);
        TEST_ASSERT_EQUAL_FLOAT(val, vm_stack[0]);
    }
    /// SUSTAIN
    for (int i = 0; i < 10; i++)
    {
        // State should now be sustain
        TEST_ASSERT_EQUAL_UINT32(2, instrument_data[3]);
        run_envelope_function();
        TEST_ASSERT_EQUAL_FLOAT(val, vm_stack[0]);
    }
    /// RELEASE
    instrument_data[1] = 1;
    run_envelope_function();
    k = 0.5f - vm_stack[0];
    val = vm_stack[0];
    while (val > 0.0f)
    {
        // State should still be release
        TEST_ASSERT_EQUAL_UINT32(3, instrument_data[3]);
        run_envelope_function();
        val = fmax(val - k, 0.0f);
        TEST_ASSERT_EQUAL_FLOAT(val, vm_stack[0]);
    }
    /// OFF
    for (int i = 0; i < 10; i++)
    {
        // State should still be invalid
        TEST_ASSERT_EQUAL_UINT32(4, instrument_data[3]);
        run_envelope_function();
        TEST_ASSERT_EQUAL_FLOAT(val, vm_stack[0]);
    }
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
    TEST_ASSERT_EQUAL_PTR(&instrument_data[3 + 16 * 0], iargs[0]);
    TEST_ASSERT_EQUAL_PTR(&instrument_data[3 + 16 * 1], iargs[1]);
    TEST_ASSERT_EQUAL_PTR(&instrument_data[3 + 16 * 2], iargs[2]);
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
                TEST_ASSERT_NOT_EQUAL_UINT32(0, instrument_data[i * INSTRUMENT_SIZE + 1]);
            }
            else
            {
                TEST_ASSERT_EQUAL_UINT32(0, instrument_data[i * INSTRUMENT_SIZE + 1]);
            }
            TEST_ASSERT_EACH_EQUAL_UINT32(0, &instrument_data[i * INSTRUMENT_SIZE + 2], INSTRUMENT_SIZE - 2);
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

void run_storeval(uint8_t amount, uint16_t addr, float stack_value, float dest_value)
{
    // Amount
    instruction_params[0] = amount;
    // Destination index
    ((uint16_t *)(&instruction_params[1]))[0] = addr;
    // Stack value
    vm_stack[0] = stack_value;
    // Destination value
    ((float *)(&instrument_data[(addr & 0x3FFF) / 4]))[0] = dest_value;
    // Set up registers
    ///     x4 = instrument instruction parameters pointer
    ///     x5 = instrument data pointer
    ///     x7 = current instrument instruction workspace pointer
    ///     x8 = VM stack data pointer
    asm volatile(
        "mov     x4, %0\n"
        "mov     x5, %1\n"
        "mov     x7, %2\n"
        "mov     x8, %3\n"
        :
        : "r"(instruction_params), "r"(instrument_data), "r"(&instrument_data[3]), "r"(&vm_stack[1])
        : "x4", "x5", "x7", "x8");
    storeval_function();
    asm volatile("mov %0, x8" : "=r"(x8_ptr));
}

void test_storeval_function(void)
{
    // SET
    run_storeval(0, 42 * 4, 1.0f, 0.3f);
    TEST_ASSERT_EQUAL_FLOAT(-1.0f * 1.0f, ((float *)(&instrument_data[42]))[0]);
    TEST_ASSERT_EQUAL_PTR(&vm_stack[1], x8_ptr);

    // SET + POP
    run_storeval(128, 44 * 4 + 0x4000, 0.5f, 0.3f);
    TEST_ASSERT_EQUAL_FLOAT(1.0f * 0.5f, ((float *)(&instrument_data[44]))[0]);
    TEST_ASSERT_EQUAL_PTR(&vm_stack[0], x8_ptr);

    // ADD
    run_storeval(0, 42 * 4 + 0x8000, 1.0f, 0.3f);
    TEST_ASSERT_EQUAL_FLOAT(-1.0f * 1.0f + 0.3f, ((float *)(&instrument_data[42]))[0]);
    TEST_ASSERT_EQUAL_PTR(&vm_stack[1], x8_ptr);

    // ADD + POP
    run_storeval(128, 44 * 4 + 0xc000, 0.5f, 0.3f);
    TEST_ASSERT_EQUAL_FLOAT(1.0f * 0.5f + 0.3f, ((float *)(&instrument_data[44]))[0]);
    TEST_ASSERT_EQUAL_PTR(&vm_stack[0], x8_ptr);
}

void run_output_function(float stack_value, unsigned char gain, float gain_modulator)
{
    // Set up stack value
    vm_stack[0] = stack_value;
    // Set up gain
    instruction_params[0] = gain;
    // Set up gain modulator
    ((float *)instrument_data)[3] = gain_modulator;
    // Set up registers
    asm volatile(
        "mov     x4, %0\n"
        "mov     x5, %1\n"
        "mov     x7, %2\n"
        "mov     x8, %3\n"
        :
        : "r"(instruction_params), "r"(instrument_data), "r"(&instrument_data[3]), "r"(&vm_stack[1])
        : "x4", "x5", "x7", "x8");
    output_function();
    asm volatile("mov %0, x8" : "=r"(x8_ptr));
}
void test_output_function(void)
{
    run_output_function(0.5f, 32, 0.25f); // 0.5 * (0.25 + 0.25) = 0.25
    TEST_ASSERT_EQUAL_PTR(&vm_stack[0], x8_ptr);
    TEST_ASSERT_EQUAL_FLOAT(0.25f, ((float *)(&instrument_data[2]))[0]);

    run_output_function(1.0f, 128, 1.0f); // 1.0 * (1.0 + 1.0) = 2.0
    TEST_ASSERT_EQUAL_PTR(&vm_stack[0], x8_ptr);
    TEST_ASSERT_EQUAL_FLOAT(2.0f, ((float *)(&instrument_data[2]))[0]);

    run_output_function(0.1f, 64, 0.2f); // 0.1 * (0.5 + 0.2) = 0.07
    TEST_ASSERT_EQUAL_PTR(&vm_stack[0], x8_ptr);
    TEST_ASSERT_EQUAL_FLOAT(0.07f, ((float *)(&instrument_data[2]))[0]);
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_transform_values);
    RUN_TEST(test_envelope_function_no_note);
    RUN_TEST(test_envelope_function_attack_starts);
    RUN_TEST(test_envelope_function_gain);
    RUN_TEST(test_envelope_function_adsr_run);
    RUN_TEST(test_storeval_function);
    RUN_TEST(test_output_function);
    RUN_TEST(test_process_stack);
    RUN_TEST(test_new_instrument_note);
    return UNITY_END();
}
