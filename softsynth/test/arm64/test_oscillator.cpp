#include "../unity.h"
#include "../../include/defines.h"
#include "../../include/softsynth.h"
#include "../test_common.h"
#include <string.h>
#include <cmath>

// Musical constants
#define NOTES_IN_OCTAVE 12 // Number of semitones in an octave

// MIDI note definitions for A notes
#define A2 45 // A2 note (MIDI note 45)
#define A3 57 // A3 note (MIDI note 57)
#define A4 69 // A4 note (MIDI note 69)

// Frequency definitions for A notes
#define A2_FREQ 110.0f   // A2 frequency in Hz
#define A3_FREQ 220.0f   // A3 frequency in Hz
#define A4_FREQ 440.0f   // A4 frequency in Hz
#define AS2_FREQ 116.54f // A#2 frequency in Hz
#define GS3_FREQ 207.65f // G#3 frequency in Hz

// Parameter constants
#define PARAM_CENTER 64 // Center value for transpose/detune parameters
#define PARAM_MAX 128   // Maximum value for most parameters
#define PARAM_MIN 0     // Minimum value for most parameters

// Test tolerance constants
#define PHASE_TOLERANCE_COARSE 0.0002f   // Tolerance for initial phase checks
#define PHASE_TOLERANCE_FINE 0.000001f   // Tolerance for accumulated phase checks
#define OUTPUT_TOLERANCE_COARSE 0.00001f // Tolerance for initial output checks
#define OUTPUT_TOLERANCE_FINE 0.1f       // Tolerance for accumulated output checks

// Array size constants
#define INSTRUMENT_PARAMS_SIZE 8 // Size of instrument parameters array
#define INSTRUMENT_WS_SIZE 16    // Size of instrument workspace array
#define INSTRUMENT_DATA_SIZE 3   // Size of instrument data array

// Unity required functions
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

void run_oscillator_function(int num, uint8_t note, uint8_t types, uint8_t transpose, uint8_t detune, uint8_t phase, uint8_t gates, uint8_t color, uint8_t shape, uint8_t gain, float *output_value, float *output_phase)
{
    uint8_t instrument_params[8] = {transpose, detune, phase, gates, color, shape, gain, types};
    float instrument_ws[16] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
    uint32_t instrument_data2[3] = {note, 0, 0};

    // Set up registers
    ///     x4 = current instrument parameters pointer
    ///     x5 = instrument data pointer
    ///     x7 = instrument instruction workspace pointer
    for (int n = 0; n < num; n++)
    {
        asm volatile(
            "mov     x4, %0\n"
            "mov     x5, %1\n"
            "mov     x7, %2\n"
            "mov     x8, %3\n"
            :
            : "r"(instrument_params), "r"(instrument_data2), "r"(instrument_ws), "r"(vm_stack)
            : "x4", "x5", "x7", "x8");
        debug_setup_sx_registers();
        oscillator_function();
    }
    *output_value = vm_stack[0];
    *output_phase = instrument_ws[0];
}

void run_sine_test(uint8_t note, uint8_t transpose, uint8_t detune, uint8_t gain, float expected_freq)
{
    float output;
    float phase;
    float f_gain = (float)gain / (float)PARAM_MAX;
    run_oscillator_function(1, note, OSCILLATOR_SINE, transpose, detune, PARAM_MIN, PARAM_MIN, PARAM_MAX, PARAM_MIN, gain, &output, &phase);
    // Check that phase has stepped one tick
    TEST_ASSERT_FLOAT_WITHIN(PHASE_TOLERANCE_COARSE, expected_freq / SAMPLE_RATE, phase);
    TEST_ASSERT_FLOAT_WITHIN(OUTPUT_TOLERANCE_COARSE, cosf(phase * 2 * M_PI) * f_gain, output);
    float one_phase = phase;
    for (int i = 2; i < (int)(1.0f / one_phase); i++)
    {
        run_oscillator_function(i, note, OSCILLATOR_SINE, transpose, detune, PARAM_MIN, PARAM_MIN, PARAM_MAX, PARAM_MIN, gain, &output, &phase);
        // Check that phase has stepped one tick
        TEST_ASSERT_FLOAT_WITHIN(PHASE_TOLERANCE_FINE, one_phase * i, phase);
        TEST_ASSERT_FLOAT_WITHIN(OUTPUT_TOLERANCE_FINE, cosf(phase * 2 * M_PI) * f_gain, output);
    }
}

void test_basic_sine(void)
{
    // A4 = 440Hz, No transpose or detune
    run_sine_test(A4, PARAM_CENTER, PARAM_CENTER, PARAM_MAX, A4_FREQ);
    // A2 = 110Hz, No transpose or detune
    run_sine_test(A2, PARAM_CENTER, PARAM_CENTER, PARAM_MAX, A2_FREQ);
}

void test_transpose_detune_sine(void)
{
    // A3 = 220Hz
    // Transpose down one octave to A2
    // Detune up one note to A#2
    run_sine_test(A3, PARAM_CENTER - NOTES_IN_OCTAVE, PARAM_MAX, PARAM_MAX, AS2_FREQ);
    // A2 = 110Hz
    // Transpose up one octave to A3
    // Detune down one note to G#2
    run_sine_test(A2, PARAM_CENTER + NOTES_IN_OCTAVE, PARAM_MIN, PARAM_MAX, GS3_FREQ);
}

void test_gain_sine(void)
{
    // A4 = 440Hz, No transpose or detune
    run_sine_test(A4, PARAM_CENTER, PARAM_CENTER, PARAM_MIN, A4_FREQ);
    // A2 = 110Hz, No transpose or detune
    run_sine_test(A2, PARAM_CENTER, PARAM_CENTER, PARAM_CENTER, A2_FREQ);
}

int main(void)
{
    UNITY_BEGIN();
    RUN_TEST(test_basic_sine);
    RUN_TEST(test_transpose_detune_sine);
    RUN_TEST(test_gain_sine);
    return UNITY_END();
}