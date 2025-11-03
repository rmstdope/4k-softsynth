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

// Output-specific test data
unsigned char instruction_params[5] = {0, 96, 96, 88, 128};
uint32_t instrument_data[SYNTH_SIZE];

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
        : "r"(instruction_params), "r"(instrument_data), "r"(&instrument_data[INSTRUMENT_WS_OFFSET]), "r"(&vm_stack[1])
        : "x4", "x5", "x7", "x8");
    output_function();
    asm volatile("mov %0, x8" : "=r"(x8_ptr));
}

void test_output_function(void)
{
    run_output_function(0.5f, 32, 0.25f); // 0.5 * (0.25 + 0.25) = 0.25
    TEST_ASSERT_EQUAL_PTR(&vm_stack[0], x8_ptr);
    TEST_ASSERT_EQUAL_FLOAT(0.25f, ((float *)(&instrument_data[INSTRUMENT_OUTPUT_OFFSET]))[0]);

    run_output_function(1.0f, 128, 1.0f); // 1.0 * (1.0 + 1.0) = 2.0
    TEST_ASSERT_EQUAL_PTR(&vm_stack[0], x8_ptr);
    TEST_ASSERT_EQUAL_FLOAT(2.0f, ((float *)(&instrument_data[INSTRUMENT_OUTPUT_OFFSET]))[0]);

    run_output_function(0.1f, 64, 0.2f); // 0.1 * (0.5 + 0.2) = 0.07
    TEST_ASSERT_EQUAL_PTR(&vm_stack[0], x8_ptr);
    TEST_ASSERT_EQUAL_FLOAT(0.07f, ((float *)(&instrument_data[INSTRUMENT_OUTPUT_OFFSET]))[0]);
}

void test_debug_instrument_output(void)
{
    float output;

    debug_start_instrument_note(0, 32);
    TEST_ASSERT_EQUAL_UINT32(32, synth_data[INSTRUMENT_NOTE_OFFSET]);
    TEST_ASSERT_EQUAL_UINT32(0, synth_data[INSTRUMENT_RELEASE_OFFSET]);

    debug_next_instrument_sample(0, &output, 0);
}

int main(void)
{
    UNITY_BEGIN();

    RUN_TEST(test_output_function);
    RUN_TEST(test_debug_instrument_output);

    return UNITY_END();
}