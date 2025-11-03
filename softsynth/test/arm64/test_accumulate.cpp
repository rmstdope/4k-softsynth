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

// Accumulate-specific test data
unsigned char instruction_params[5] = {0, 96, 96, 88, 128};
uint32_t instrument_data[SYNTH_SIZE];

void test_accumulate_function(void)
{
    float sum = 0;
    for (int i = 0; i < MAX_NUM_INSTRUMENTS; i++)
    {
        // Set up instrument data
        ((float *)(&instrument_data[i * INSTRUMENT_SIZE + INSTRUMENT_OUTPUT_OFFSET]))[0] = (float)(i + 1); // Output value
        sum += (float)(i + 1);
    }
    // Set up registers
    asm volatile(
        "mov     x8, %0\n"
        "mov     x10, %1\n"
        :
        : "r"(&vm_stack[0]), "r"(instrument_data)
        : "x8", "x10");
    accumulate_function();
    asm volatile("mov %0, x8" : "=r"(x8_ptr));
    TEST_ASSERT_EQUAL_PTR(&vm_stack[1], x8_ptr);
    TEST_ASSERT_EQUAL_FLOAT(sum, vm_stack[0]);
}

int main(void)
{
    UNITY_BEGIN();

    RUN_TEST(test_accumulate_function);

    return UNITY_END();
}