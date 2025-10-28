#include "../../include/defines.h"

// Instrument Macros and defines
.macro INSTRUMENT_START def_name
.endmacro

// Envelope
.macro	ENVELOPE attack, decay, sustain, release, gain
    .byte  \attack
    .byte  \decay
    .byte  \sustain
    .byte  \release
    .byte  \gain
.endmacro
.equ ENVELOPE_WS_STATE,     0
.equ ENVELOPE_WS_LEVEL,     ENVELOPE_WS_STATE + 4
.equ ENVELOPE_WS_GAIN_MOD,  ENVELOPE_WS_LEVEL + 4
.equ ENVELOPE_WS_SIZE,      ENVELOPE_WS_GAIN_MOD + 4
.equ ENVELOPE_PARAM_ATTACK, 0
.equ ENVELOPE_PARAM_DECAY,  ENVELOPE_PARAM_ATTACK + 4
.equ ENVELOPE_PARAM_SUSTAIN,ENVELOPE_PARAM_DECAY + 4
.equ ENVELOPE_PARAM_RELEASE,ENVELOPE_PARAM_SUSTAIN + 4
.equ ENVELOPE_PARAM_GAIN,   ENVELOPE_PARAM_RELEASE + 4
.equ ENVELOPE_PARAM_SIZE,   ENVELOPE_PARAM_GAIN + 4
#define	ENV_ATTACK(val) val
#define	ENV_DECAY(val) val
#define	ENV_SUSTAIN(val) val
#define	ENV_RELEASE(val) val
#define	ENV_GAIN(val) val
.equ ENV_STATE_ATTACK,   0
.equ ENV_STATE_DECAY,    1
.equ ENV_STATE_SUSTAIN,  2
.equ ENV_STATE_RELEASE,  3
.equ ENV_STATE_OFF,      4

// Oscillator
.macro OSCILLATOR transpose, detune, phase, gates, color, shape, gain, type
    .byte \transpose
    .byte \detune
    .byte \phase
    .byte \gates
    .byte \color
    .byte \shape
    .byte \gain
    .byte \type
.endmacro
#define OSCILLATOR_TYPE(val) val
#define OSCILLATOR_TRANSPOSE(val) val
#define OSCILLATOR_DETUNE(val) val
#define OSCILLATOR_PHASE(val) val
#define OSCILLATOR_GATES(val) val
#define OSCILLATOR_SHAPE(val) val
#define OSCILLATOR_COLOR(val) val
#define OSCILLATOR_GAIN(val) val
.equ OSCILLATOR_SINE,       0x01
.equ OSCILLATOR_SQUARE,     0x02
.equ OSCILLATOR_SAW,        0x04
.equ OSCILLATOR_TRIANGLE,   0x08
.equ OSCILLATOR_NOISE,      0x10
.equ OSCILLATOR_LFO,        0x20
.equ OSCILLATOR_WS_PHASE,           0
.equ OSCILLATOR_WS_GAIN_MOD,        OSCILLATOR_WS_PHASE + 4
.equ OSCILLATOR_WS_TRANSPOSE_MOD,   OSCILLATOR_WS_GAIN_MOD + 4 // Value will be multiplied by 128
.equ OSCILLATOR_WS_DETUNE_MOD,      OSCILLATOR_WS_TRANSPOSE_MOD + 4
.equ OSCILLATOR_WS_FREQUENCY_MOD,   OSCILLATOR_WS_DETUNE_MOD + 4
.equ OSCILLATOR_WS_COLOR_MOD,       OSCILLATOR_WS_FREQUENCY_MOD + 4
.equ OSCILLATOR_WS_PHASE_MOD,       OSCILLATOR_WS_COLOR_MOD + 4
.equ OSCILLATOR_WS_SIZE,            OSCILLATOR_WS_PHASE_MOD + 4
.equ OSCILLATOR_PARAM_TRANSPOSE,    0
.equ OSCILLATOR_PARAM_DETUNE,       OSCILLATOR_PARAM_TRANSPOSE + 4
.equ OSCILLATOR_PARAM_PHASE,        OSCILLATOR_PARAM_DETUNE + 4
.equ OSCILLATOR_PARAM_GATES,        OSCILLATOR_PARAM_PHASE + 4
.equ OSCILLATOR_PARAM_COLOR,        OSCILLATOR_PARAM_GATES + 4
.equ OSCILLATOR_PARAM_SHAPE,        OSCILLATOR_PARAM_COLOR + 4
.equ OSCILLATOR_PARAM_GAIN,         OSCILLATOR_PARAM_SHAPE + 4
.equ OSCILLATOR_PARAM_SIZE,         OSCILLATOR_PARAM_GAIN + 4

.macro STOREVAL amount, destination
    .byte \amount
    .hword \destination
.endmacro
.equ STOREVAL_PARAM_AMOUNT, 0
.equ STOREVAL_PARAM_SIZE, STOREVAL_PARAM_AMOUNT + 4
#define STORE_AMOUNT(val) val
#define STORE_DEST(val) val
.equ STOREVAL_POP,  0x4000
.equ STOREVAL_ADD,  0x8000
.equ STOREVAL_MASK, 0x3FFF

.macro OPERATION operand
    .byte \operand
.endmacro
.equ OPERATION_PARAM_OPERAND, 0
.equ OPERATION_PARAM_SIZE, OPERATION_PARAM_OPERAND + 4
#define OPERATION_OPERAND(val) val
.equ OPERATOR_MULP,  1

// Output
.macro OUTPUT gain
    .byte \gain
.endmacro

#define OUTPUT_GAIN(val) val

.equ OUTPUT_WS_GAIN_MOD,        0

.equ OUTPUT_PARAM_GAIN,         0
.equ OUTPUT_PARAM_SIZE,         OUTPUT_PARAM_GAIN + 4

// Accumulate
.macro ACCUMULATE
.endmacro

.equ ACCUMULATE_PARAM_SIZE,         0

/// Instrument state structure
.equ instrument_note,           0
.equ instrument_release,        instrument_note + 4
.equ instrument_output,         instrument_release + 4
.equ instrument_workspaces,     instrument_output + 4
.equ instrument_length,         instrument_workspaces + MAX_COMMANDS*MAX_COMMAND_PARAMS*4

/// Synth structure
.equ instrument_data_size,      instrument_length * MAX_NUM_INSTRUMENTS
.equ global_data_size,          instrument_length
.equ synth_data_size,           (instrument_data_size + global_data_size)

