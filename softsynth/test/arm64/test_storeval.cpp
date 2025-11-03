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

// Storeval-specific test data
unsigned char instruction_params[5] = {0, 96, 96, 88, 128};
uint32_t instrument_data[SYNTH_SIZE];

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
        : "r"(instruction_params), "r"(instrument_data), "r"(&instrument_data[INSTRUMENT_WS_OFFSET]), "r"(&vm_stack[1])
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

int main(void)
{
    UNITY_BEGIN();

    RUN_TEST(test_storeval_function);

    return UNITY_END();
}