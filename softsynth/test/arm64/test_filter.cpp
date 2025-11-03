#include "../unity.h"
#include "../../include/defines.h"
#include "../../include/softsynth.h"
#include "../test_common.h"
#include <string.h>
#include <cmath>

// Filter constants
#define FILTER_WS_SIZE_WORDS 4    // Size of filter workspace in 32-bit words
#define FILTER_PARAM_SIZE_WORDS 3 // Size of filter parameters in 32-bit words

// Parameter constants
#define PARAM_CENTER 64 // Center value for parameters
#define PARAM_MAX 128   // Maximum value for most parameters
#define PARAM_MIN 0     // Minimum value for most parameters

// Test tolerance constants
#define OUTPUT_TOLERANCE_COARSE 0.0001f // Tolerance for output checks

// Array size constants
#define INSTRUMENT_PARAMS_SIZE 8 // Size of instrument parameters array
#define INSTRUMENT_WS_SIZE 16    // Size of instrument workspace array
#define INSTRUMENT_DATA_SIZE 3   // Size of instrument data array

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

// External filter function declaration
extern "C" void filter_function();

// Helper function to run filter function with specific parameters
void run_filter_function(uint8_t frequency, uint8_t resonance, uint8_t filter_type, float input_value, float ws_low, float ws_band)
{
    // Set up instrument parameters (8 bytes total)
    uint8_t instrument_params[INSTRUMENT_PARAMS_SIZE] = {frequency, resonance, filter_type};

    // Set up filter workspace (low, band freq_mod, res_mod)
    float filter_ws[FILTER_WS_SIZE_WORDS] = {ws_low, ws_band, 0.0f, 0.0f};

    // Set input value on VM stack
    vm_stack[0] = input_value;

    float freq = ((float)(frequency) / PARAM_MAX);
    freq *= freq; // Squared frequency
    float res = ((float)(resonance) / PARAM_MAX);

    // Set up registers
    ///     x4 = current instrument parameters pointer
    ///     x5 = instrument data pointer
    ///     x7 = instrument instruction workspace pointer
    ///     x8 = VM stack pointer
    asm volatile(
        "mov     x4, %0\n"
        "mov     x7, %1\n"
        "mov     x8, %2\n"
        :
        : "r"(instrument_params), "r"(filter_ws), "r"(&vm_stack[1])
        : "x4", "x7", "x8");
    debug_setup_sx_registers();
    filter_function();

    ///     high = input - ws.low - resonance * ws.band
    ///     band = ws.band + squared_frequency * high
    ///     low = ws.low + squared_frequency * ws.band
    float high = input_value - ws_low - res * ws_band;
    TEST_ASSERT_EQUAL_FLOAT(ws_band + freq * high, filter_ws[1]);
    TEST_ASSERT_EQUAL_FLOAT(ws_low + freq * ws_band, filter_ws[0]);
    float new_out = 0.0f;
    if (filter_type & FILTER_LOWPASS)
        new_out += filter_ws[0];
    if (filter_type & FILTER_BANDPASS)
        new_out += filter_ws[1];
    if (filter_type & FILTER_HIGHPASS)
        new_out += high;
    TEST_ASSERT_EQUAL_FLOAT(new_out, vm_stack[0]);
}

void test_basic_filter(void)
{
    // Test with basic lowpass filter parameters
    run_filter_function(64, 64, FILTER_LOWPASS, 1.0f, 0.0f, 0.0f);
    run_filter_function(64, 64, FILTER_BANDPASS, 1.0f, 0.0f, 0.0f);
    run_filter_function(64, 64, FILTER_HIGHPASS, 1.0f, 0.0f, 0.0f);
    run_filter_function(64, 64, FILTER_LOWPASS + FILTER_BANDPASS + FILTER_HIGHPASS, 1.0f, 0.0f, 0.0f);
    run_filter_function(48, 80, FILTER_LOWPASS, 1.0f, 0.2f, 0.3f);
    run_filter_function(32, 96, FILTER_HIGHPASS, 1.0f, 0.3f, 0.4f);
    run_filter_function(16, 112, FILTER_BANDPASS, 1.0f, 0.4f, 0.5f);
    run_filter_function(0, 128, FILTER_LOWPASS + FILTER_BANDPASS + FILTER_HIGHPASS, 1.0f, 0.5f, 0.6f);
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_basic_filter);
    return UNITY_END();
}