#include "common.asm"

.global _instrument_instructions
#define instrument_instructions _instrument_instructions
.global _instrument_parameters
#define instrument_parameters _instrument_parameters
.global _instrument_patterns
#define instrument_patterns _instrument_patterns
.global _pattern_array
#define pattern_array _pattern_array

.data

///
/// Instrument definition - instructions
///
instrument_instructions:
INSTRUMENT_START Instrument0
    .byte ENVELOPE_ID
    .byte OSCILLATOR_ID
    .byte OPERATION_ID
    .byte OUTPUT_ID
    .byte INSTRUMENT_END
INSTRUMENT_START Instrument1
    .byte ENVELOPE_ID
    .byte STOREVAL_ID
    .byte OSCILLATOR_ID
    .byte OPERATION_ID
    .byte OUTPUT_ID
    .byte INSTRUMENT_END
INSTRUMENT_START Instrument2
    .byte ENVELOPE_ID
    .byte STOREVAL_ID
    .byte OSCILLATOR_ID
    .byte OPERATION_ID
    .byte FILTER_ID
    // .byte PANNING_ID
    .byte OUTPUT_ID
    .byte INSTRUMENT_END
INSTRUMENT_START Instrument3
    .byte INSTRUMENT_END
INSTRUMENT_START Instrument4
    .byte INSTRUMENT_END
song_instructions:
INSTRUMENT_START Song
    .byte ACCUMULATE_ID
    .byte OUTPUT_ID
    .byte INSTRUMENT_END

///
/// Instrument definition - parameters
///
instrument_parameters:
INSTRUMENT_START Instrument0
	ENVELOPE ENV_ATTACK(70), ENV_DECAY(70), ENV_SUSTAIN(70), ENV_RELEASE(70), ENV_GAIN(128)
	OSCILLATOR OSCILLATOR_TRANSPOSE(64), OSCILLATOR_DETUNE(64), OSCILLATOR_PHASE(64), OSCILLATOR_GATES(0), OSCILLATOR_COLOR(128), OSCILLATOR_SHAPE(64), OSCILLATOR_GAIN(128), OSCILLATOR_TYPE(OSCILLATOR_SINE)
    OPERATION OPERATION_OPERAND(OPERATOR_MULP)
    OUTPUT OUTPUT_GAIN(128)
INSTRUMENT_START Instrument1
	ENVELOPE ENV_ATTACK(72), ENV_DECAY(96), ENV_SUSTAIN(96), ENV_RELEASE(88), ENV_GAIN(128)
	// ENVELOPE ENV_ATTACK(0), ENV_DECAY(0), ENV_SUSTAIN(128), ENV_RELEASE(0), ENV_GAIN(128)
	STOREVAL STORE_AMOUNT(128), STORE_DEST(instrument_workspaces + 0 * MAX_COMMAND_PARAMS + ENVELOPE_WS_GAIN_MOD)
	OSCILLATOR OSCILLATOR_TRANSPOSE(64), OSCILLATOR_DETUNE(64), OSCILLATOR_PHASE(64), OSCILLATOR_GATES(0), OSCILLATOR_COLOR(40), OSCILLATOR_SHAPE(64), OSCILLATOR_GAIN(128), OSCILLATOR_TYPE(OSCILLATOR_SINE)
	// OSCILLATOR OSCILLATOR_TRANSPOSE(64), OSCILLATOR_DETUNE(72), OSCILLATOR_PHASE(32), OSCILLATOR_GATES(0), OSCILLATOR_COLOR(96), OSCILLATOR_SHAPE(112), OSCILLATOR_GAIN(64), OSCILLATOR_TYPE(OSCILLATOR_SINE)
    OPERATION OPERATION_OPERAND(OPERATOR_MULP)
    OUTPUT OUTPUT_GAIN(128)
INSTRUMENT_START Instrument2
    ENVELOPE ENV_ATTACK(0), ENV_DECAY(76), ENV_SUSTAIN(0), ENV_RELEASE(0), ENV_GAIN(32)
    STOREVAL STORE_AMOUNT(128), STORE_DEST(instrument_workspaces + 0 * MAX_COMMAND_PARAMS + ENVELOPE_WS_GAIN_MOD)
    OSCILLATOR OSCILLATOR_TRANSPOSE(64), OSCILLATOR_DETUNE(64), OSCILLATOR_PHASE(64), OSCILLATOR_GATES(0), OSCILLATOR_COLOR(64), OSCILLATOR_SHAPE(64), OSCILLATOR_GAIN(128), OSCILLATOR_TYPE(OSCILLATOR_NOISE)
    OPERATION OPERATION_OPERAND(OPERATOR_MULP)
    FILTER FILTER_FREQUENCY(80), FILTER_RESONANCE(128), FILTER_TYPE(FILTER_LOWPASS)
    // PAN PAN_VALUE(64)
    OUTPUT OUTPUT_GAIN(64)
INSTRUMENT_START Instrument3
INSTRUMENT_START Instrument4
song_parameters:
INSTRUMENT_START Song
    ACCUMULATE
    OUTPUT OUTPUT_GAIN(128)

instrument_patterns:
instrument_2_patterns:  .byte   9,  7, 10,  7, 11,  7, 12,  7,  9,  7, 10,  7, 11,  7, 12,  7,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 12,  7, 13,  7, 14,  7,  3,  7,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 12,  7,  0,  0
instrument_1_patterns:  .byte   0,  0,  0,  0,  0,  0,  0,  0,  1,  2,  3,  0,  4,  5,  6,  7,  0,  0,  0,  0,  0,  0,  0,  0,  1,  2,  3,  0,  4,  5,  6,  7,  0,  0,  0,  0,  0,  0,  0,  0,  1,  2,  3,  0,  4,  5,  6,  7,  1,  2,  3,  0,  4,  5,  6,  7,  8,  2,  9,  0,  0,  0
instrument_3_patterns:  .byte  15,  0, 16,  0, 17,  0, 18,  0, 19,  0, 16,  0, 17,  0, 18,  0, 20, 20, 21, 21, 22, 22, 20, 20, 20, 20, 21, 21, 22, 22, 20, 20, 23, 15, 24, 16, 25, 17, 18,  0, 20, 20, 21, 21, 22, 22, 20, 20, 20, 20, 21, 21, 22, 22, 20, 20, 20, 20,  0,  0,  0,  0
instrument_4_patterns:  .byte   0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26,  0,  0,  0,  0,  0,  0,  0,  0, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26, 26,  0,  0,  0,  0,  0
instrument_5_patterns:  .byte   0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 27, 26, 27, 26, 27, 26, 27, 28, 27, 26, 27, 26, 27, 26, 27, 28, 27, 29, 27, 29, 27, 29, 27, 29, 27, 26, 27, 26, 27, 26, 27, 28, 27, 26, 27, 26, 27, 26, 27, 28, 27, 26, 27,  0,  0,  0
instrument_6_patterns:  .byte   0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 30, 31, 30, 32, 30, 31, 30, 32, 30, 31, 30, 32, 30, 31, 30, 32, 30, 31, 30, 32, 30, 31, 30,  0, 30, 31, 30, 32, 30, 31, 30, 32, 30, 31, 30, 32, 30, 31, 30, 32, 30, 31, 30, 32,  0,  0
instrument_7_patterns:  .byte   0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 33, 33, 33, 34, 33, 33, 33, 34, 33, 33, 33, 34, 33, 33, 33, 34, 33, 33, 33, 34, 33, 33, 33, 34, 33, 33, 33, 34, 33, 33, 33, 34, 33, 33, 33, 34, 33, 33, 33, 34, 33, 33,  0,  0,  0,  0
instrument_8_patterns:  .byte   0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 35, 36,  0, 37, 38, 36,  0, 39, 35, 36,  0, 37, 38, 40,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0
instrument_9_patterns:  .byte   0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0, 11, 41, 41, 41, 11, 41, 41, 41, 11, 41, 41, 41, 11, 41, 41, 41, 11, 41, 41, 41, 11, 41, 41, 41, 11, 41, 41, 41, 11, 41, 41, 41, 11, 41, 41, 41, 11, 41, 41, 41, 11, 41, 41, 41, 11, 41, 41, 41, 41,  0

pattern_array:
    .byte   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0
    .byte  76, HLD, HLD, HLD,   0,   0,   0,   0,  79, HLD, HLD, HLD,   0,   0,   0,   0
    .byte  69, HLD, HLD, HLD, HLD, HLD, HLD, HLD,   0,   0,   0,   0,   0,   0,   0,   0
    .byte  76, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD
    .byte  81, HLD, HLD, HLD,   0,   0,   0,   0,  79, HLD, HLD, HLD,   0,   0,   0,   0
    .byte  84, HLD, HLD, HLD, HLD, HLD, HLD, HLD,   0,   0,   0,   0,   0,   0,   0,   0
    .byte  76, HLD, HLD, HLD,   0,   0,   0,   0,  88, HLD, HLD, HLD, HLD, HLD, HLD, HLD
    .byte HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD,   0,   0,   0,   0
    .byte  76, HLD, HLD, HLD, HLD, HLD, HLD, HLD,   0,   0,   0,   0,   0,   0,   0,   0
    .byte  52, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD
    .byte  57, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD
    .byte  60, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD
    .byte  64, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD
    .byte  69, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD
    .byte  72, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD
    .byte  40,  52, HLD,  64, HLD,  40,  52,  64,  52, HLD, HLD, HLD,   0,   0,   0,   0
    .byte  57,   0,   0,  57,   0,   0,  69,   0,   0,  69,   0,   0,  57, HLD, HLD, HLD
    .byte  52,  64,   0,  57,   0,  69,  48,   0,  48, HLD, HLD, HLD,   0,   0,   0,   0
    .byte  40, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD
    .byte  40,  52, HLD,  40, HLD,  40,  40,  40,  52, HLD, HLD, HLD,   0,   0,   0,   0
    .byte  40,   0,   0,  52,   0,   0,  40,   0,  52,  40,   0,  52,   0,  40,   0,   0
    .byte  45,   0,   0,  57,   0,   0,  45,   0,  57,  45,   0,  57,   0,  45,   0,   0
    .byte  48,   0,   0,  60,   0,   0,  48,   0,  60,  48,   0,  60,   0,  48,   0,   0
    .byte  40, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD,   0,   0,   0,   0
    .byte  45, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD,   0,   0,   0,   0
    .byte  36, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD,   0,   0,   0,   0
    .byte   0,   0,   0,   0,  60, HLD,   0,   0,   0,   0,   0,   0,  60, HLD,   0,   0
    .byte  60, HLD,   0,   0,   0,   0,  60, HLD,   0,   0,  60, HLD,  60, HLD,   0,   0
    .byte   0,   0,   0,   0,  60, HLD,   0,   0,   0,   0,   0,   0,  60, HLD,  60, HLD
    .byte   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,  60, HLD,   0,   0
    .byte  60, HLD,  60, HLD,   0,   0,  60, HLD,   0,   0,   0,   0,  60, HLD,   0,   0
    .byte   0,   0,  60, HLD,   0,   0,   0,   0,  60, HLD,   0,   0,   0,   0,   0,   0
    .byte   0,   0,  60, HLD,   0,   0,   0,   0,  60, HLD,   0,   0,  60, HLD,   0,   0
    .byte   0,   0,   0,  60, HLD,   0,   0,   0,   0,   0,   0,   0,  60, HLD,   0,   0
    .byte   0,   0,   0,  60, HLD,   0,   0,   0,   0,  60, HLD,  60,  60, HLD,   0,   0
    .byte   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,  84,   0,   0,   0
    .byte  91,   0,   0,  88,   0,   0,  76,   0,  81,   0,   0,   0,   0,   0,   0,   0
    .byte  81,   0,   0,  84,   0,   0,  86,   0,  88,   0,   0,   0,   0,   0,   0,   0
    .byte   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,   0,  93,   0,   0,   0
    .byte  81,   0,   0,  84,   0,   0,  86,   0,  81,   0,   0,   0,   0,   0,   0,   0
    .byte  84,   0,   0,  86,   0,   0,  88,   0,   0,  91,   0,   0,  84,   0,   0,   0
    .byte HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD, HLD
