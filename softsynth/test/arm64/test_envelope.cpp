#include "../unity.h"
#include "../../include/defines.h"
#include "../../include/softsynth.h"
#include "../test_common.h"
#include <string.h>
#include <cmath>

// Unity setup/teardown functions
extern "C"
{
    void setUp(void)
    {
        // Unity runs this before each test
    }

    void tearDown(void)
    {
        // Unity runs this after each test
    }
}

// Envelope-specific test data (these variables are specific to envelope tests)
unsigned char instruction_params[5] = {0, 96, 96, 88, 128};
uint32_t instrument_data[SYNTH_SIZE];

void setup_envelope_function(uint32_t current_note, bool is_released = false, unsigned char attack = 0, unsigned char decay = 0, unsigned char sustain = 0, unsigned char release = 0, unsigned char gain = 128)
{
    instruction_params[0] = attack;
    instruction_params[1] = decay;
    instruction_params[2] = sustain;
    instruction_params[3] = release;
    instruction_params[4] = gain;
    memset(instrument_data, 0, sizeof(instrument_data));
    instrument_data[INSTRUMENT_NOTE_OFFSET] = current_note;           // Current note
    instrument_data[INSTRUMENT_RELEASE_OFFSET] = is_released ? 1 : 0; // Release (1 if true, 0 if false)
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
        : "r"(instruction_params), "r"(instrument_data), "r"(&instrument_data[INSTRUMENT_WS_OFFSET]), "r"(vm_stack)
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
    ((float *)instrument_data)[INSTRUMENT_WS_OFFSET + 2] = 1.0f; // GAIN_MOD
    run_envelope_function();
    TEST_ASSERT_EQUAL_FLOAT(2.0f, vm_stack[0]);

    setup_envelope_function(1, false, 0, 0, 128, 0, 64);
    ((float *)instrument_data)[INSTRUMENT_WS_OFFSET + 2] = 1.0f; // GAIN_MOD
    run_envelope_function();
    TEST_ASSERT_EQUAL_FLOAT(1.5f, vm_stack[0]);

    setup_envelope_function(1, false, 0, 0, 128, 0, 32);
    ((float *)instrument_data)[INSTRUMENT_WS_OFFSET + 2] = 0.25f; // GAIN_MOD
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
        TEST_ASSERT_EQUAL_UINT32(0, instrument_data[INSTRUMENT_WS_OFFSET]);
        run_envelope_function();
        val = fmin(val + k, 1.0f);
        TEST_ASSERT_EQUAL_FLOAT(val, vm_stack[0]);
    }
    /// DECAY
    // State should now be decay
    TEST_ASSERT_EQUAL_UINT32(1, instrument_data[INSTRUMENT_WS_OFFSET]);
    run_envelope_function();
    k = 1.f - vm_stack[0];
    val = vm_stack[0];
    while (val > 0.5f)
    {
        // State should still be decay
        TEST_ASSERT_EQUAL_UINT32(1, instrument_data[INSTRUMENT_WS_OFFSET]);
        run_envelope_function();
        val = fmax(val - k, 0.5f);
        TEST_ASSERT_EQUAL_FLOAT(val, vm_stack[0]);
    }
    /// SUSTAIN
    for (int i = 0; i < 10; i++)
    {
        // State should now be sustain
        TEST_ASSERT_EQUAL_UINT32(2, instrument_data[INSTRUMENT_WS_OFFSET]);
        run_envelope_function();
        TEST_ASSERT_EQUAL_FLOAT(val, vm_stack[0]);
    }
    /// RELEASE
    instrument_data[INSTRUMENT_RELEASE_OFFSET] = 1;
    run_envelope_function();
    k = 0.5f - vm_stack[0];
    val = vm_stack[0];
    while (val > 0.0f)
    {
        // State should still be release
        TEST_ASSERT_EQUAL_UINT32(3, instrument_data[INSTRUMENT_WS_OFFSET]);
        run_envelope_function();
        val = fmax(val - k, 0.0f);
        TEST_ASSERT_EQUAL_FLOAT(val, vm_stack[0]);
    }
    /// OFF
    for (int i = 0; i < 10; i++)
    {
        // State should still be invalid
        TEST_ASSERT_EQUAL_UINT32(4, instrument_data[INSTRUMENT_WS_OFFSET]);
        run_envelope_function();
        TEST_ASSERT_EQUAL_FLOAT(val, vm_stack[0]);
    }
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_envelope_function_no_note);
    RUN_TEST(test_envelope_function_attack_starts);
    RUN_TEST(test_envelope_function_gain);
    RUN_TEST(test_envelope_function_adsr_run);
    return UNITY_END();
}