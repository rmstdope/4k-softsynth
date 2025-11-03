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

// Arithmetic-specific test data
unsigned char instruction_params[5] = {0, 96, 96, 88, 128};
uint32_t instrument_data[SYNTH_SIZE];

// Helper function to call cosine_waveform with specific register setup
float call_cosine_waveform(float phase, float color)
{
    float result;
    asm volatile(
        "fmov s0, %w0\n" // phase in s0
        "fmov s1, %w1\n" // color in s1
        :
        : "r"(phase), "r"(color)
        : "s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "x3", "x7", "w11");
    debug_setup_sx_registers();
    cosine_waveform();
    asm volatile(
        "fmov %w0, s0\n" // get result from s0
        : "=r"(result));
    return result;
}

void test_cosine_waveform(void)
{
    // Test 1: phase = 0.0, color = 1.0 -> should give cos(0) = 1.0
    float result = call_cosine_waveform(0.0f, 1.0f);
    TEST_ASSERT_FLOAT_WITHIN(0.02f, 1.0f, result);

    // Test 2: phase = 0.25, color = 1.0 -> should give cos(π/2) ≈ 0.0
    result = call_cosine_waveform(0.25f, 1.0f);
    TEST_ASSERT_FLOAT_WITHIN(0.02f, 0.0f, result);

    // Test 3: phase = 0.5, color = 1.0 -> should give cos(π) = -1.0
    result = call_cosine_waveform(0.5f, 1.0f);
    TEST_ASSERT_FLOAT_WITHIN(0.02f, -1.0f, result);

    // Test 4: phase = 0.75, color = 1.0 -> should give cos(3π/2) ≈ 0.0
    result = call_cosine_waveform(0.75f, 1.0f);
    TEST_ASSERT_FLOAT_WITHIN(0.02f, 0.0f, result);

    // Test 5: phase = 1.0, color = 1.0 -> should give cos(2π) = 1.0
    result = call_cosine_waveform(1.0f, 1.0f);
    TEST_ASSERT_FLOAT_WITHIN(0.02f, 1.0f, result);

    // Test 6: phase > color -> should return 0.0 (based on assembly logic)
    result = call_cosine_waveform(0.8f, 0.5f);
    TEST_ASSERT_FLOAT_WITHIN(0.02f, 0.0f, result);

    // Test 7: Test color effect - phase = 0.5, color = 0.5 -> should give cos(2π) = 1.0
    result = call_cosine_waveform(0.5f, 0.5f);
    TEST_ASSERT_FLOAT_WITHIN(0.02f, 1.0f, result);
}

void test_pwr(void)
{
    float exp;
    float result;
    for (uint8_t note = 0; note < 128; note++)
    {
        exp = note / 12.0f;
        asm volatile(
            "fmov     s1, %w0\n"
            :
            : "r"(exp)
            : "s1");
        debug_setup_sx_registers();
        pwr();
        asm volatile(
            "fmov %w0, s1\n" // get result from s1
            : "=r"(result));
    }
    // Allow an error that is 1% of the expected value due to approximation issues with higher values
    TEST_ASSERT_FLOAT_WITHIN(0.01f * powf(2.0f, exp), powf(2.0f, exp), result);
}

int main(void)
{
    UNITY_BEGIN();

    RUN_TEST(test_cosine_waveform);
    RUN_TEST(test_pwr);

    return UNITY_END();
}